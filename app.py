import os
os.environ["FLASK_ENV"] = "development"
from flask import Flask, jsonify, request
import requests
import csv
import logging
import re


app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)
app.logger.handlers = logging.getLogger().handlers
app.logger.setLevel(logging.DEBUG)

PORT=8080
HOST="0.0.0.0"

def parse_csv_to_dict(file_path):
    movies = []
    with open(file_path, mode="r", encoding="utf-8") as file:
        csv_reader = csv.reader(file)
        headers = [
            "Rank",
            "Title",
            "Genre",
            "Description",
            "Director",
            "Actors",
            "Year",
            "Runtime (Minutes)",
            "Rating",
            "Votes",
            "Revenue (Millions)",
            "Metascore",
        ]

        for row in csv_reader:
            movie = {headers[i]: row[i] for i in range(len(headers))}
            movies.append(movie)

    return movies


def search_movies(movies, column, value):
    pattern = re.compile(value, re.IGNORECASE)
    return [movie for movie in movies if pattern.search(movie.get(column, ""))]


imdb = parse_csv_to_dict("imdb.csv")


@app.route("/")
def root():
    app.logger.debug("Debug message from the root route.")
    
    genre = request.args.get("genre")
    app.logger.debug(f"GENRE: {genre}")

    if genre:
        try:
            response = requests.get(f"http://{HOST}:{PORT}/{genre}")

            response.raise_for_status()
            return response.json(), 200

        except Exception as e:
            error_details = {
                "error": str(e),  
                "traceback": traceback.format_exc()  
            }
            status_code = getattr(e.response, "status_code", 500) if hasattr(e, 'response') else 500
            return jsonify(error_details), status_code
    
    else:
        return {
            "message": "Hello World! From the root URL of the (fake) IMDB API server :)"
        }


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    return jsonify(search_movies(imdb, "Genre", path)), 200


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=True)