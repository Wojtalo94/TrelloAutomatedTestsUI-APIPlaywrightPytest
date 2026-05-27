import pytest


@pytest.mark.accessibility
def test_card_modal_accessibility(logged_in_page, check_accessibility):
    """
    Otwiera pierwszą kartę na testowej tablicy i skanuje modal karty.
    """
    page = logged_in_page
    board_url = "https://trello.com/b/BOARD_ID/example-board" # tutaj zmienić na inny na stronie
    page.goto(board_url)
    page.wait_for_selector("div.list-card, .list-card", timeout=20000)
    first_card = page.locator("div.list-card, .list-card").first
    first_card.click()
    # modal karty w Trello ma klasę window lub role dialog
    page.wait_for_selector("div.window, [role='dialog']", timeout=10000)
    # opcjonalna kontrola focus trap (nie wymagana przez Axe, ale przydatna)
    check_accessibility()
    # zamknięcie modala
    try:
        page.click("a.dialog-close-button, button[aria-label='Close dialog'], button[aria-label='Close']")
    except Exception:
        # fallback: ESC
        page.keyboard.press("Escape")
