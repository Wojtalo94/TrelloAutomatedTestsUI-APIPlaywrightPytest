import pytest
import time
from pages.board_page import BoardPage

@pytest.mark.ui_and_api
def test_create_board_via_api_and_verify_in_ui(rest_controller, logged_in_page):
    board_name = f"hybrid_test_board_{int(time.time())}"

    board_id = rest_controller.create_board(board_name)

    try:
        page = logged_in_page
        # przykład: przejście do strony głównej i odświeżenie listy
        page.goto("https://trello.com")  # lub BASE_URL
        page.wait_for_load_state("networkidle")

        # 3) Weryfikacja przez UI: użyj Page Object
        board_page = BoardPage(page)
        assert board_page.is_board_present(board_name), "Board not visible in UI"

    finally:
        # cleanup
        rest_controller.delete_board()
