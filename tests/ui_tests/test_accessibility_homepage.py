import pytest


@pytest.mark.accessibility
def test_login_accessibility(logged_in_page, check_accessibility):
    page = logged_in_page

    confirm_button = page.get_by_test_id("create-board-tile")
    confirm_button.wait_for(state="visible", timeout=15000)
    check_accessibility()