import pytest


@pytest.mark.accessibility
def test_login_accessibility(logged_in_page, check_accessibility):
    page = logged_in_page
    page.goto("https://trello.com/login") # tutaj zmienić na inny na stronie
    page.wait_for_selector('input[id="user"], input[name="user"]', timeout=15000) # tutaj zmienić na inny na stronie
    check_accessibility()