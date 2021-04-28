import os
from pathlib import Path
import json
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient, UpdateOne


try:
    from dotenv import load_dotenv
    dotenv_path = Path("env/mongo.env")
    load_dotenv(dotenv_path=dotenv_path)
except:
    print("error")


"""Connecting to remote database"""


def connect_to_mongo(url):
    client = MongoClient(url)
    movie_db = client['movie-db']
    movie_collection = movie_db['movie']
    menu_collection = movie_db["menu"]
    return movie_collection, menu_collection


""" Resources functions here"""


def rename_dict_key(dictionary, old_key, new_key):
    dictionary[new_key] = dictionary[old_key]
    del dictionary[old_key]


def time_normalizer(time_string):
    ''' in imdb title block movie duration appears in string format nut in db we have only integer minutes '''
    time_string = time_string.replace("h", "")
    time_string = time_string.replace("min", "")

    if len(time_string.split()) == 1:
        return int(time_string)
    else:
        hour_min_list = time_string.split()
        hour = int(hour_min_list[0])
        minute = int(hour_min_list[1])
        return (hour*60) + minute


""" Global Variables """


imdb_link = "https://www.imdb.com"
headers = {"Accept-Language": "en-US,en;q=0.5"}
parsing_routes = {
    "popular": "/chart/moviemeter",
    "top": "/chart/top",
    # "toptv":"/chart/toptv/",
    # "populartv": "/chart/tvmeter"
}


""" Scraping begins here """


def scrape(db_url=os.environ.get("DB_HOST")):

    movie_collection, menu_collection = connect_to_mongo(db_url)

    for route in parsing_routes:
        title_instances = []
        crew_instances = []
        movie_ids = []

        print(route)
        response = requests.get(
            f'{imdb_link}{parsing_routes[route]}', headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        title_blocks_wrapper = soup.find('tbody', {'class': 'lister-list'})
        title_blocks = title_blocks_wrapper.find_all('tr')

        for element in title_blocks[:2]:
            title_instance = {}
            title_column_td = element.find('td', 'titleColumn')

            # id
            imdb_title_link_a = title_column_td.a
            title_instance["_id"] = imdb_title_link_a['href'].split('/')[2]
            movie_ids.append(title_instance["_id"])

            # title
            print(imdb_title_link_a.string)
            title_instance["primary_title"] = imdb_title_link_a.string

            # year
            year_info_span = title_column_td.find('span', 'secondaryInfo')
            title_instance["start_year"] = year_info_span.string.strip("()")

            # rating and num_votes
            rating_strong = element.find(
                'td', {'class': ['ratingColumn', 'imdbRating']}).strong

            if rating_strong:
                title_instance["rating"] = float(rating_strong.string)
                title_instance["num_votes"] = int(
                    rating_strong['title'].split()[3].replace(",", ""))

            """ Movie Page Scraping for more details(director, writer, description, ...) """

            movie_page_response = requests.get(
                imdb_link+imdb_title_link_a["href"], headers=headers)
            movie_page = BeautifulSoup(movie_page_response.text, "html.parser")

            # release_date, runtime_minutes, genres
            title_block_div = movie_page.find("div", "title_block")
            subtext_div = title_block_div.find("div", "subtext")

            try:
                runtime = subtext_div.find("time").text
                runtime = time_normalizer(runtime.strip())
                title_instance["runtime_minutes"] = runtime
            except:
                pass

            try:
                genres_a_list = subtext_div.find_all(
                    "a", href=lambda url: url.startswith("/search/title"))
                genres = [a_tag.text for a_tag in genres_a_list]
                title_instances["genres"] = genres
            except:
                pass

            try:
                release_date = subtext_div.find(
                    "a", href=lambda url: "releaseinfo" in url).text
                title_instance["release_date"] = release_date
            except Exception as e:
                print(e)

            # images
            title_image_div = movie_page.find("div", "poster")
            if title_image_div:
                title_image_img = title_image_div.a.img
                title_instance["images"] = {
                    "sm": title_image_img["src"],
                    "lg": title_image_img["src"].split("._")[0]+".jpg"
                }

            plot_summary_div = movie_page.find("div", "plot_summary")

            # description
            summary_text_div = plot_summary_div.find("div", "summary_text")
            if summary_text_div:
                title_instance["summary_text"] = summary_text_div.text.strip()

            # director
            try:
                credit_summary_item_div = plot_summary_div.find(
                    "h4", text="Director:").parent  # div containing director
                director_instance = {
                    "_id": credit_summary_item_div.a["href"].split("/")[2],
                    "full_name": credit_summary_item_div.a.string
                }
                crew_instances.append(director_instance)
                rename_dict_key(director_instance, old_key="_id",
                                new_key="director_id")
                title_instance["director"] = director_instance
            except:
                print("no director")

            # writer
            try:
                credit_summary_item_writer = plot_summary_div.find(
                    "h4",
                    text=lambda word: word == "Writer:" or word == "Writers:"
                ).parent  # div containing writer

                writers = credit_summary_item_writer.find_all(
                    "a", href=lambda link: link.startswith("/name/"))
                writer_instances = [{"_id": tag['href'].split(
                    "/")[2], "full_name": tag.string} for tag in writers]

                crew_instances.extend(writer_instances)

                for writer in writer_instances:
                    rename_dict_key(writer, "_id", "writer_id")
                title_instance["writers"] = writer_instances

            except:
                print("no writers")

            # casts
            cast_instances = []
            cast_table = movie_page.find("table", "cast_list")
            cast_tr_list = cast_table.find_all(
                "tr", class_=lambda classname: classname == 'odd' or classname == "even")

            for cast_tr in cast_tr_list:
                cast_instance = {}

                # actor id
                td_primary_photo = cast_tr.find("td", "primary_photo")
                cast_instance["_id"] = td_primary_photo.a['href'].split("/")[2]

                # actor fullname
                cast_instance["full_name"] = td_primary_photo.a.img['title']

                # character name
                try:
                    td_character = cast_tr.find("td", "character")
                    cast_instance["character_name"] = td_character.a.string
                except:
                    pass
                cast_instances.append(cast_instance)

            for cast in cast_instances:
                rename_dict_key(cast, '_id', "actor_id")

            title_instance["cast"] = cast_instances
            title_instances.append(title_instance)

        """ Data insertion """

        updatable_title_objects = [UpdateOne(
            {"_id": title["_id"]},
            {"$set": title},
            upsert=True
        ) for title in title_instances]
        result = movie_collection.bulk_write(updatable_title_objects)
        print(result.bulk_api_result)

        menu_instance = {"name": route, "titles": movie_ids}

        menu_result = menu_collection.update_one(
            {"name": menu_instance["name"]},
            {"$set": menu_instance}, upsert=True)
        print(menu_result.matched_count)


if __name__ == "__main__":
    scrape()
