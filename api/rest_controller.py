import logging
from .api_client import ApiClient


class RestController():
    def __init__(self):
        self._logger = logging.getLogger("AppController")
        self._request = ApiClient()


    def get_board_information(self):
        response, status_code = self._request.get_board()
        assert status_code == 200, f"Expected status code 200, but got {status_code}"
        return response