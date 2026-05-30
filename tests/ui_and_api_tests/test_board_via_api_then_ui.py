import pytest
import time
from pages.board_page import BoardPage

@pytest.mark.ui_and_api
def test_create_board_via_UI_and_verify_in_api(rest_controller, logged_in_page):
    board_page = BoardPage(logged_in_page)
    board_name = f"hybrid_UI_API_test_board_{int(time.time())}"

    board_page.create_board(board_name)
    board_id = rest_controller.get_board_id(board_name)
    rest_controller.check_board_name_and_desc(board_id, board_name)
    rest_controller.delete_board(board_id)
    rest_controller.check_if_board_has_been_deleted(board_id, board_name)
