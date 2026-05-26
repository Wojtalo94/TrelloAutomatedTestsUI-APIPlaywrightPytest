import pytest
from pages.board_page import BoardPage


@pytest.mark.ui
@pytest.mark.parametrize("board_name",
                         [
                             "DevBoard",
                             "QABoard",
                             "ManagerBoard"
                         ])
def test_create_board(logged_in_page, capture_bad_responses, board_name):
    board_page = BoardPage(logged_in_page)
    board_page.create_board(board_name)
    board_page.delete_board(board_name)
    board_page.check_that_all_boards_have_been_removed()

    