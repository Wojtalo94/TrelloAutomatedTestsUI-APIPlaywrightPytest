import pytest


@pytest.mark.accessibility
def test_notifications_accessibility(logged_in_page, check_accessibility):
    page = logged_in_page
    # kliknij ikonę powiadomień
    try:
        page.click("button[aria-label='Notifications'], button[title='Notifications']") # tutaj zmienić na inny na stronie
    except Exception:
        # jeśli nie ma przycisku, przejdź do URL powiadomień (jeśli istnieje)
        page.goto("https://trello.com/notifications")
    page.wait_for_selector("div.notifications-list, .notifications", timeout=10000) # tutaj zmienić na inny na stronie
    check_accessibility()
