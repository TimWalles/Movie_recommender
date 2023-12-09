def normalize_movie_info_response(response: dict) -> dict:
    return {
        'id': response.get('id'),
        'title': response.get('title'),
        'description': response.get('overview'),
        'poster_path': response.get('poster_path'),
    }
