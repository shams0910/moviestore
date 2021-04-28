import os
from pathlib import Path

from flask import Flask, request, Response
from database.db import initialize_db
from flask_restful import Api
from movies.routes import initialize_routes
from database.models import Movie

try:
	from dotenv import load_dotenv
	dotenv_path = Path("env/mongo.env")
	load_dotenv(dotenv_path=dotenv_path)
except:
	print("error")


app = Flask(__name__)
api = Api(app)


# app settings goes here
app.config['MONGODB_SETTINGS'] = {
	'host': os.environ.get("DB_HOST"),
	'port': 27017
}


# intializations goes here

initialize_db(app)
initialize_routes(api)


if __name__ == '__main__':
	app.run(debug=True)