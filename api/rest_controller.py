import logging
from api.request import Request
from config.config_loader import TRELLO_API_KEY, TRELLO_API_TOKEN


class RestController():
    def __init__(self):
        self._logger = logging.getLogger("RestController")
        self._request = Request()
        self.query_string = f"key={TRELLO_API_KEY}&token={TRELLO_API_TOKEN}"
    
    
    def get_members_boards_information(self, board_id):
        self._logger.info("Getting information about members from the boards")
        response, status_code = self._request.get_board(f"{board_id}/memberships?{self.query_string}")
        assert status_code == 200, f"Expected status code 200, but got {status_code}"
        return response
    

    def get_board_information(self, board_id):
        self._logger.info("Getting information about the board")
        response, status_code = self._request.get_board(f"{board_id}?{self.query_string}")
        return response, status_code
    

    def check_board_name_and_desc(self, board_id, board_name, board_desc = None):
        self._logger.info(f"Checking information about the board: '{board_name}'")
        response, status_code = self.get_board_information(board_id)
        assert status_code == 200, f"Expected status code 200, but got {status_code}"
        actual_name = response.get('name')
        actual_desc = response.get('desc')
        assert actual_name == board_name, f"Wrong board name: {actual_name}, expected: {board_name}"
        if board_desc is not None:
            assert actual_desc == board_desc, f"Wrong board desc: {actual_desc}, expected: {board_desc}"


    def create_board(self, board_name):
        self._logger.info("Creating the board")
        response, status_code = self._request.post_board(f"?name={board_name}&{self.query_string}")
        assert status_code == 200, f"Expected status code 200, but got {status_code}"
        actual_board_id = response.get('id')
        return actual_board_id


    def delete_board(self, board_id):
        self._logger.info("Deleting the board")
        _ , status_code = self._request.delete_board(f"{board_id}?{self.query_string}")
        assert status_code == 200, f"Expected status code 200, but got {status_code}"


    def update_board(self,board_id, board_name, board_desc):
        self._logger.info("Updating the board")
        response, status_code = self._request.put_board(f"{board_id}?{self.query_string}&name={board_name}&desc={board_desc}")
        assert status_code == 200, f"Expected status code 200, but got {status_code}"
        actual_board_name = response.get('name')
        actual_board_desc = response.get('desc')
        return actual_board_name, actual_board_desc


    def check_if_board_has_been_deleted(self, board_id, board_name):
        self._logger.info(f"Checking if the board: '{board_name}' has been deleted")
        _ , status_code = self.get_board_information(board_id)
        assert status_code == 404, f"Expected status code 200, but got {status_code}"


    def get_board_id(self, board_name):
        self._logger.info(f"Checking the boards '{board_name}' ID")
        response, status_code = self._request.get_board(f"{board_name}?{self.query_string}") #tutaj jest błąd
        assert status_code == 200, f"Expected status code 200, but got {status_code}"
        actual_board_id = response.get('board_id')
        return actual_board_id