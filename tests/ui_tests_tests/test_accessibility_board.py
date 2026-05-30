import pytest


@pytest.mark.accessibility
def test_board_accessibility(logged_in_page, check_accessibility):
    page = logged_in_page
    board_url = "https://trello.com/b/BOARD_ID/example-board" # tutaj zmienić na inny na stronie
    page.goto(board_url)
    page.wait_for_load_state("networkidle")
    page.wait_for_selector("div.list, .list-wrapper, .js-list-content", timeout=20000) # tutaj zmienić na inny na stronie
    check_accessibility()
