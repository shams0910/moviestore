from .db import db

class Crew(db.Document):
	full_name = db.StringField()
	birth_year = db.IntField()
	death_year = db.IntField()
	professions = db.ListField(db.StringField())
	known_for_movies = db.ListField(db.StringField())


class MainCast(db.EmbeddedDocument):
	actor_id = db.ReferenceField(Crew)
	full_name = db.StringField()
	character_name = db.StringField()


class MovieDirector(db.EmbeddedDocument):
	director_id = db.ReferenceField(Crew)
	full_name = db.StringField()


class MovieWriter(db.EmbeddedDocument):
	writer_id = db.ReferenceField(Crew)
	full_name = db.StringField()


class Image(db.EmbeddedDocument):
	sm = db.StringField()
	lg = db.StringField()


class Movie(db.Document):
	_id = db.StringField()
	title_type = db.StringField()
	primary_title = db.StringField()
	original_title = db.StringField()
	summary_text = db.StringField()
	is_adult = db.BooleanField()
	start_year = db.IntField()
	end_year = db.IntField()
	release_date = db.DateTimeField()
	runtime_minutes = db.IntField()
	rating = db.DecimalField()
	num_votes = db.IntField()
	director = db.EmbeddedDocumentField(MovieDirector)
	writers = db.ListField(db.EmbeddedDocumentField(MovieWriter))
	images = db.EmbeddedDocumentField(Image)
	genres = db.ListField(db.StringField())
	cast = db.ListField(db.EmbeddedDocumentField(MainCast))

	meta = {'indexes': [
		{
			'fields': ['$primary_title'],
			'default_language': 'english'
		}
	]}


class Menu(db.Document):
	name = db.StringField()
	titles = db.ListField(db.StringField())