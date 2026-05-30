import logging
from api.request import Request
from config.config_loader import TRELLO_API_KEY, TRELLO_API_TOKEN


class RestController():
    def __init__(self):
        self._logger = logging.getLogger("RestController")
        self._request = Request()
        self.query_string = f"key={TRELLO_API_KEY}&token={TRELLO_API_TOKEN}"
        self.board_id = None
    
    
    def get_members_boards_information(self):
        response = self._request.get_board(f"{self.board_id}/memberships?{self.query_string}")
        return response
    

    def get_board_information(self):
        response = self._request.get_board(f"{self.board_id}?{self.query_string}")
        return response
    

    def create_board(self, board_name):
        response, status_code = self._request.post_board(f"?name={board_name}&{self.query_string}")
        assert status_code == 200, f"Expected status code 200, but got {status_code}"
        self.board_id = response['id']
        return self.board_id


    def delete_board(self):
        _ , status_code = self._request.delete_board(f"{self.board_id}?{self.query_string}")
        assert status_code == 200, f"Expected status code 200, but got {status_code}"


    def update_board(self, board_name, board_desc):
        _ , status_code = self._request.put_board(f"{self.board_id}?{self.query_string}&name={board_name}&desc={board_desc}")
        assert status_code == 200, f"Expected status code 200, but got {status_code}"