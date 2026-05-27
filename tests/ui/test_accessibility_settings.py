import pytest


@pytest.mark.accessibility
def test_settings_accessibility(logged_in_page, check_accessibility):
    """
    Ustawienia konta / profil.
    Dostosuj URL jeśli Twoje środowisko ma inny endpoint.
    """
    page = logged_in_page
    page.goto("https://trello.com/your/account") # tutaj zmienić na inny na stronie
    page.wait_for_load_state("networkidle")
    # przykładowy selektor formularza ustawień
    page.wait_for_selector("form#account-settings, div.account-settings, form[action*='account']", timeout=15000) # tutaj zmienić na inny na stronie
    check_accessibility()
