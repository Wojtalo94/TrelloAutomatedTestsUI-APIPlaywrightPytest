import os
import pytest
import logging
from pages.home_page import HomePage
from helpers.bad_responses import BadResponses
from playwright.sync_api import Playwright
from config.config_loader import load_test_config, BASE_URL, TRELLO_API_KEY, TRELLO_API_TOKEN, EMAIL, PASSWORD


# =========================
# Logging configuration
# =========================

os.makedirs("logs", exist_ok=True)
logging.basicConfig(filename="logs/logs_web.log",
                    filemode='a',
                    format='%(asctime)s.%(msecs)03d [%(levelname)s][%(name)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO,
                    encoding="utf-8")

logger = logging.getLogger(__name__)


# =========================
# Pytest hooks
# ========================

def pytest_runtest_setup(item):
    logger.info(f"====================| START TEST: {item.name} |====================")


def pytest_runtest_teardown(item):
    logger.info(f"====================| END TEST: {item.name} |====================")


# =========================
# Fixtures
# =========================

@pytest.fixture(scope="session")
def browser_options():
    config = load_test_config()
    return {
        "headless": config.get("headless", True),
        "slow_mo": config.get("slow_mo", 0),
    }


@pytest.fixture(scope="module")
def logged_in_page(playwright: Playwright, browser_options):
    '''
    Logs in once per module.
    '''
    browser = playwright.chromium.launch(headless=browser_options["headless"], slow_mo=browser_options["slow_mo"], args=["--start-maximized"])
    context = browser.new_context(base_url=BASE_URL, no_viewport=True)
    page = context.new_page()
    page.set_default_timeout(25000)

    try:
        home_page = HomePage(page)
        home_page.sign_in_to_home_page(BASE_URL, EMAIL, PASSWORD)

        yield page

    finally:
        try:
            page.close() 
        except Exception as e:
            logger.exception(f"Failed to close page: {e}")
        try:
            context.close()
        except Exception as e:
            logger.exception(f"Failed to close context: {e}")
        try:
            browser.close()
        except Exception as e:
            logger.exception(f"Failed to close browser: {e}")


@pytest.fixture(scope="session")
def api_context():
    '''
    Fixture do testów API.
    '''
    pass


@pytest.fixture(scope="function")
def capture_bad_responses(logged_in_page):
    """Create BadResponses BEFORE the test runs so it collects during the test.
    Yields the BadResponses instance so the test can inspect it during execution.
    After the test finishes the fixture will call assert_no_bad_responses() which will
    raise AssertionError if any bad responses were collected (thus failing the test).
    """
    page = logged_in_page
    context = page.context

    bad = BadResponses()
    bad.add_page(page)

    def on_new_page(new_page):
        logger.info("New page detected and attached to BadResponses")
        bad.add_page(new_page)

    context.on("page", on_new_page)
    try:
        yield bad

    finally:
        try:
            context.remove_listener("page", on_new_page)
        except Exception as e:
            logger.warning(f"Failed to detach page listener: {e}")

        bad.assert_no_bad_responses()
