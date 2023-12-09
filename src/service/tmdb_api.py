import json
import os

from src.service.query_builder import QueryBuilder


class TheMovieDB(QueryBuilder):
    def __init__(self):
        super().__init__(
            headers={
                "accept": "application/json",
                'Authorization': f'Bearer {os.getenv("TMDB_API_KEY")}',
            }
        )
