import pytest


@pytest.mark.accessibility
def test_search_accessibility(logged_in_page, check_accessibility):
    """
    Otwiera panel wyszukiwania i skanuje jego UI.
    Dostosuj selektory jeśli Trello zmienił elementy.
    """
    page = logged_in_page
    # jeśli masz globalny shortcut do search, możesz użyć page.keyboard.press("/")
    # tutaj używamy przycisku z aria-label
    try:
        page.click("button[aria-label='Search'], button[title='Search']")  # tutaj zmienić na inny na stronie
    except Exception:
        # fallback: przejdź bezpośrednio do strony wyszukiwania jeśli istnieje
        page.goto("https://trello.com/search")
    page.wait_for_selector("input[placeholder='Search'], input[type='search']", timeout=10000) # tutaj zmienić na inny na stronie
    check_accessibility()
