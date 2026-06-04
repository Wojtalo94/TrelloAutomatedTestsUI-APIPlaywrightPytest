import pytest
from pages.main_page import MainPage
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
    main_page = MainPage(logged_in_page)

    # We need to reopen the page at the beginning of the test to isolate the tests. An assertion error during testing means that cleaning up after the test is possible ONLY after a `yield`, and since there are different tests, this cleanup after `yield` might need to be done per test, so it’s best to perform a new page load at the start of the test. Adding ‘assert’ in try/finally is also not an option, because screenshots will not be taken during an assertion error but only later, when we have, for example, a different page. It is possible to take screenshots in assert, but this requires adding code there every time to take screenshots whenever an assertion is made. 
    main_page.open_main_page()

    board_page.create_board(board_name)
    board_page.delete_board(board_name)
    board_page.check_that_all_boards_have_been_removed()