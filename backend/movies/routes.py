from .apis import (PopularMoviesApi, TopMoviesApi, MovieSearchApi, MovieApi)

def initialize_routes(api):
	api.add_resource(PopularMoviesApi, '/movies/popular')
	api.add_resource(TopMoviesApi, '/movies/top')
	api.add_resource(MovieSearchApi, '/movies/search')
	api.add_resource(MovieApi, '/movies/<id>')