import requests


class QueryBuilder:
    def __init__(self, headers):
        self.headers = headers

    def get_response(cls, url: str = '', params: dict | None = None):
        response = requests.get(url=url, headers=cls.headers, params=params)
        if response.status_code != 200:
            print(f'Error {response.status_code}: {response.json()}')
            return None
        return response.json()
