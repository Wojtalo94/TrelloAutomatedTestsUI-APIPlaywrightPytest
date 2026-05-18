import pytest
import logging
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
    config = load_test_config()
    headless = config.get('headless', True)
    slow_mo = config.get('slow_mo', 0)
    browser = playwright.chromium.launch(headless=headless, slow_mo=slow_mo, args=["--start-maximized"])
    context = browser.new_context(base_url=BASE_URL, no_viewport=True) # tutaj
    page = context.new_page()

    # logowanie do trello
    
    # zapisujemy stan (ciasteczka, local storage)
    context.storage_state(path="state.json")

    yield context

    context.close()
    browser.close()


@pytest.fixture(scope="function")
def auth_page(logged_in_context):
    browser = logged_in_context.browser
    context = browser.new_context(storage_state="state.json", base_url=BASE_URL)
    page = context.new_page()

    yield page

    context.close


@pytest.fixture(scope="function")
def capture_bad_responses(set_up, request):
    """Create BadResponses BEFORE the test runs so it collects during the test.
    Yields the BadResponses instance so the test can inspect it during execution.
    After the test finishes the fixture will call assert_no_bad_responses() which will
    raise AssertionError if any bad responses were collected (thus failing the test).
    """
    page = set_up
    bad = BadResponses(page)

    yield bad

    bad.assert_no_bad_responses()