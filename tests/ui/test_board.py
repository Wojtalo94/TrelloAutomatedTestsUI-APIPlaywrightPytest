import pytest
from pages.board_page import BoardPage


@pytest.mark.ui
@pytest.mark.parametrize("board_name",
                         [
                             #"DevBoard",
                             #"QABoard",
                             "ManagerBoard"
                         ])
def test_create_board(auth_page, capture_bad_responses, board_name):
    # Inicjalizacja POM
    board_page = BoardPage(auth_page)
    board_page.create_board(board_name)