from flask import  Response, request
from flask_restful import Resource
from database.models import Movie, Menu


main_fields = ["primary_title", "start_year", "rating", "genres", "images__sm"]

# create views here

class PopularMoviesApi(Resource):
	def get(self):
		page = request.args.get("page", 0)
		limit = request.args.get("limit", 20)
		try:
			page = int(page)
			limit = int(limit)
		except Exception as e:
			return Response(f'{e}', status=400)
		start = page*limit
		end = start+limit

		popular_movies = Menu.objects(name="popular").first() # later put limit here
		movies = Movie.objects(_id__in=popular_movies.titles[start:end]).scalar(*main_fields).to_json()

		return Response(movies, mimetype="application/json", status=200)


class TopMoviesApi(Resource):
	def get(self):
		page = request.args.get("page", 0)
		limit = request.args.get("limit", 20)
		try:
			page = int(page)
			limit = int(limit)
		except Exception as e:
			return Response(f'{e}', status=400)
		start = page*limit
		end = start+limit

		top_movies = Menu.objects(name="top").first() # later put limit here
		movies = Movie.objects(_id__in=top_movies.titles[start:end]).scalar(*main_fields).to_json()

		return Response(movies, mimetype="application/json", status=200)


class MovieSearchApi(Resource):	
	def get(self):
		string = request.args.get("q", default='')
		movies = Movie.objects.search_text(string).scalar(*main_fields[:2])\
			.order_by('$text_score')[:10].to_json()
		return Response(movies, mimetype="application/json", status=200)


class MovieApi(Resource):
	def get(self, id):
		movie = Movie.objects.get(_id=id).to_json()
		return Response(movie, mimetype='application/json', status=200)