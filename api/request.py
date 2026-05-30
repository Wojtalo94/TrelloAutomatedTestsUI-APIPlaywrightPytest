import requests
import logging
from typing import Any
from json import JSONDecodeError


class Request():
    def __init__(self, timeout: int = 15):
        self._logger = logging.getLogger("Request")
        # A timeout has been added to prevent HTTP requests from hanging and blocking tests
        self._timeout = timeout
        self._urls = {"boards": "https://api.trello.com/1/boards/"}
    
    
    def url(self, name: str) -> str:
        """
        Acts as a centralized registry for all API URLs used in tests.
        """
        if name not in self._urls:
            raise AttributeError(f"Missing {name} in urls list")
        return self._urls[name]


    def _prepare_return(self, response) -> tuple[Any, int]:
        """
        Normalizes HTTP response into a consistent structure for tests.
        """
        try:
            data = response.json()
        except (JSONDecodeError, ValueError):
            self._logger.error("Response is not JSON: %s", response.text)
            data = {}
        if response.status_code >= 400:
            self._logger.error(f"Request failed: {response.status_code} - {response.text}")
        return data, response.status_code


    def get(self, url: str) -> tuple[Any, int]:
        with requests.Session() as s:
            return self._prepare_return(s.get(url, timeout=self._timeout))


    def patch(self, url: str, json: dict) -> tuple[Any, int]:
        with requests.Session() as s:
            return self._prepare_return(s.patch(url, timeout=self._timeout, json=json))


    def put(self, url: str, json=None) -> tuple[Any, int]:
        with requests.Session() as s:
            return self._prepare_return(s.put(url, timeout=self._timeout, json=json))


    def post(self, url: str, json: dict = None) -> tuple[Any, int]:
        with requests.Session() as s:
            return self._prepare_return(s.post(url, timeout=self._timeout, json=json))


    def delete(self, url: str) -> tuple[Any, int]:
        with requests.Session() as s:
            return self._prepare_return(s.delete(url, timeout=self._timeout))


# ==============================
# convenience methods for boards
# ==============================

    def post_board(self, path: str) -> tuple[Any, int]:
        return self.post(self.url("boards") + path)


    def get_board(self, path: str) -> tuple[Any, int]:
        return self.get(self.url("boards") + path)


    def delete_board(self, path: str) -> tuple[Any, int]:
        return self.delete(self.url("boards") + path)
    

    def put_board(self, path: str) -> tuple[Any, int]:
        return self.put(self.url("boards") + path)