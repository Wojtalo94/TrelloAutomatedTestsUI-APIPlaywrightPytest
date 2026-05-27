import pytest


@pytest.mark.accessibility
def test_dashboard_accessibility(logged_in_page, check_accessibility):
    page = logged_in_page
    page.goto("https://trello.com/u/me/boards") # tutaj zmienić na inny na stronie
    page.wait_for_load_state("networkidle")
    page.wait_for_selector("div.boards-page-board-section, div.boards-page", timeout=15000) # tutaj zmienić na inny na stronie
    check_accessibility()
