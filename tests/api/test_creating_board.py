import pytest
import time

@pytest.mark.api
def test_create_update_and_delete_board(rest_controller):
    board_name = f"api_test_board_{int(time.time())}"

    rest_controller.create_board(board_name)
    rest_controller.check_board_name_and_desc(board_name)

    changed_board_name, changed_board_desc = rest_controller.update_board("Test name", "Test desc")
    rest_controller.check_board_name_and_desc(changed_board_name, changed_board_desc)

    rest_controller.delete_board()
