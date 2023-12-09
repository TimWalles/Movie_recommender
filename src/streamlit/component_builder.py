import json
import pathlib

from src.normalizers.tmdb_normalizer import normalize_movie_info_response
from src.service.tmdb_api import TheMovieDB


class StreamLitComponentBuilder:
    def __init__(self) -> None:
        self.image_button_css = "<a href='#' id='{movie_id}'><img width='8%' src='{poster_url}'></a>"
        self.get_movie_info_url = "https://api.themoviedb.org/3/movie/{movie_id}?language=en-US"
        self.get_movie_poster_url = "https://image.tmdb.org/t/p/w500{poster_path}"
        self.tmdb_api = TheMovieDB()
        self.movies_infos_file_path = pathlib.Path('.', 'data', 'movies_info.json')
        self.movies_info_dict = self.load_movies_info()

    def load_movies_info(self):
        if not pathlib.Path.exists(self.movies_infos_file_path):
            return {}
        with open(self.movies_infos_file_path, 'r') as json_file:
            movies_infos = json.load(json_file)
            movies_infos = {int(key): val for key, val in movies_infos.items()}
        return movies_infos

    def update_movies_info(self):
        with open(self.movies_infos_file_path, "w") as fp:
            json.dump(self.movies_info_dict, fp)

    def get_movie_info(self, movie_id: int) -> dict:
        response = self.tmdb_api.get_response(url=self.get_movie_info_url.format(movie_id=movie_id))
        if response:
            response = normalize_movie_info_response(response)
        else:
            response = {}
        self.movies_info_dict[int(movie_id)] = response
        self.update_movies_info()
        return response

    def get_movie_infos(self, movie_ids: list[int]) -> list[dict]:
        return [self.movies_info_dict[movie_id] if movie_id in self.movies_info_dict else self.get_movie_info(movie_id) for movie_id in movie_ids]

    def build_movie_poster_url(self, movie_info: dict) -> str:
        return self.get_movie_poster_url.format(poster_path=movie_info.get('poster_path'))

    def build_clickable_image_button(self, movie_info: dict) -> str:
        return self.image_button_css.format(
            movie_id=movie_info.get('id'),
            poster_url=self.build_movie_poster_url(movie_info),
        )

    def build_image_columns(self, movie_ids: list[int], n: int):
        movie_infos = self.get_movie_infos(movie_ids)
        content = ''
        counter = 0
        for movie_info in movie_infos:
            if movie_info:
                content += self.build_clickable_image_button(movie_info)
                counter += 1
                if counter >= n:
                    break
        return content
