import os
import pytest
import logging
import tempfile
from pages.home_page import HomePage
from helpers.bad_responses import BadResponses
from playwright.sync_api import Playwright
from config.config_loader import load_test_config, BASE_URL, TRELLO_API_KEY, TRELLO_API_TOKEN, EMAIL, PASSWORD


logging.basicConfig(filename="logs/logs_web.log",
                    filemode='a',
                    format='%(asctime)s.%(msecs)03d [%(levelname)s][%(name)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def pytest_runtest_setup(item):
    logger.info(f"====================| Start test: {item.name} |====================")


@pytest.fixture(scope="module")
def logged_in_context(playwright: Playwright):
    '''
    Fixture wykonujący się raz na moduł/plik.
    Logowanie i zapisywanie stanu autoryzacji.
    '''
    config = load_test_config()
    headless = config.get('headless', True)
    slow_mo = config.get('slow_mo', 0)
    browser = playwright.chromium.launch(headless=headless, slow_mo=slow_mo, args=["--start-maximized"])
    context = browser.new_context(base_url=BASE_URL, no_viewport=True)
    page = context.new_page()

    # logowanie do trello
    home_page = HomePage(page)
    home_page.sign_in_to_home_page(BASE_URL, EMAIL, PASSWORD)
    
    # zapisujemy stan (ciasteczka, local storage)
    context.storage_state(path="state.json")

    yield context

    context.close()
    browser.close()


@pytest.fixture(scope="function")
def auth_page(logged_in_context):
    '''
    Fixture dla każdego testu.
    Nowa karta z zapisanego/zalogowanego kontekstu,
    gwarantująca niezależność testów.
    '''
    browser = logged_in_context.browser
    context = browser.new_context(storage_state="state.json", base_url=BASE_URL)
    page = context.new_page()

    yield page

    page.close()
    context.close()


@pytest.fixture(scope="session")
def api_context():
    '''
    Fixture do testów API.
    '''


@pytest.fixture(scope="function")
def capture_bad_responses(auth_page):
    """Create BadResponses BEFORE the test runs so it collects during the test.
    Yields the BadResponses instance so the test can inspect it during execution.
    After the test finishes the fixture will call assert_no_bad_responses() which will
    raise AssertionError if any bad responses were collected (thus failing the test).
    """
    page = auth_page
    context = page.context
    bad = BadResponses()
    bad.add_page(page)

    def on_new_page(new_page):
        bad.add_page(new_page)

    context.on("page", on_new_page)
    try:
        yield bad
    finally:
        try:
            context.off("page", on_new_page)
        except Exception:
            pass

        bad.assert_no_bad_responses()