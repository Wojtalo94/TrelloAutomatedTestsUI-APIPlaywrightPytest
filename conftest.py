import os
import pytest
import allure
import logging
import datetime
from pathlib import Path
from pytest_html import extras
from pages.home_page import HomePage
from pytest_playwright_axe import Axe
from playwright.sync_api import Playwright
from api.rest_controller import RestController
from helpers.bad_responses import BadResponses
from allure_commons.types import AttachmentType
from config.config_loader import load_test_config, BASE_URL, EMAIL, PASSWORD


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
# Allure env
# =========================

# Optional fallback for allure results dir (you can remove if you always pass --alluredir)
os.environ.setdefault("ALLURE_RESULTS_DIR", "allure-results")

# =========================
# Screenshots configuration
# =========================

SCREENSHOT_DIR = Path("screenshots")
SCREENSHOT_DIR.mkdir(exist_ok=True)


# =========================
# Pytest hooks
# ========================

def pytest_runtest_setup(item):
    logger.info(f"====================| START TEST: {item.name} |====================")


def pytest_runtest_teardown(item):
    logger.info(f"====================| END TEST: {item.name} |====================")


# =========================
# Axe configuration
# =========================

# Fail only on critical and serious
AXE_FAIL_ON = ["critical", "serious"]

# Ensure reports dir exists
AXE_OUTPUT_DIR = Path("axe-reports")
AXE_OUTPUT_DIR.mkdir(exist_ok=True)


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


@pytest.fixture(scope="function")
def rest_controller():
    rc = RestController()
    
    yield rc


@pytest.fixture(scope="function")
def capture_bad_responses(logged_in_page):
    """
    Create BadResponses BEFORE the test runs so it collects during the test.
    Yields the BadResponses instance so the test can inspect it during execution.
    After the test finishes the fixture will call assert_no_bad_responses() which will raise AssertionError if any bad responses were collected (thus failing the test).
    """
    page = logged_in_page
    context = page.context

    bad = BadResponses()
    bad.add_page(page)

    def _on_new_page(new_page):
        logger.info("New page detected and attached to BadResponses")
        bad.add_page(new_page)

    context.on("page", _on_new_page)
    try:
        yield bad

    finally:
        # detaching the context listener
        try:
            if hasattr(context, "off"):
                context.off("page", _on_new_page)
            elif hasattr(context, "remove_listener"):
                context.remove_listener("page", _on_new_page)
            else:
                logger.debug("BrowserContext has no off/remove_listener; leaving listener attached")
        except Exception:
            logger.exception("Failed to detach context page listener")

        # removing all handlers added to pages
        try:
            bad.detach()
        except Exception:
            logger.exception("Failed to detach page handlers")

        # assertion
        bad.assert_no_bad_responses()


# =========================
# Axe fixtures and helpers
# =========================

@pytest.fixture(scope="session")
def axe_instance():
    """
    Session-scoped Axe instance configured to fail on critical/serious is disabled.
    Reused across tests to avoid reloading axe-core every time.
    """
    axe = Axe(output_directory=str(AXE_OUTPUT_DIR))#, fail_on=AXE_FAIL_ON)
    return axe


@pytest.fixture(scope="function")
def axe(axe_instance):
    """
    Function-scoped wrapper returning the shared Axe instance.
    You can call axe.run(page) in tests or use check_accessibility fixture below.
    """
    return axe_instance


@pytest.fixture(scope="function")
def check_accessibility(axe, request, logged_in_page):
    """
    Helper to run Axe on the current page, auto-fail on violations (critical/serious), and attach generated report paths to the test node for pytest-html integration.
    Usage in test: check_accessibility()
    """
    def _check():
        page = logged_in_page
        try:
            results = axe.run(page)
        except Exception as e:
            logger.exception("Axe run failed")
            pytest.fail(f"Axe run failed: {e}")
        
        violations = results.get("violations", [])

        # Save latest report paths on the test node so hooks can access them
        try:
            request.node.axe_html = axe.get_latest_html_report_path()
        except Exception:
            request.node.axe_html = None
        try:
            request.node.axe_json = axe.get_latest_json_report_path()
        except Exception:
            request.node.axe_json = None

        if violations:
            summary_lines = []
            for v in violations:
                impact = v.get("impact", "")
                summary_lines.append(f"{v['id']} ({impact}) - {v.get('description','')}")
                nodes = v.get("nodes", [])
                if nodes:
                    targets = nodes[0].get("target", [])
                    if targets:
                        summary_lines.append(f"  target: {', '.join(targets)}")
            summary = "\n".join(summary_lines)

            # store concise summary on node for pytest-html and Allure
            try:
                request.node.axe_summary = summary
            except Exception:
                logger.exception("Failed to set axe_summary on node")

            # keep failing the test if you want (original behavior)
            pytest.fail(f"A11y violations found ({len(violations)}):\n{summary}")

    return _check


# =========================
# Pytest-html report integration
# =========================

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    A hook wrapper that captures and attaches a screenshot for failed UI tests.
    After the test runs, it retrieves the report object; if the failure occurred in the 'call' phase and the test is marked as 'ui' or 'ui_and_api', it attempts to load the fixture.
    'logged_in_page', take a full-page screenshot, and save it.
    """
    outcome = yield
    report = outcome.get_result()
    # ensure report.extra exists
    report.extra = getattr(report, "extra", [])

    # only for UI / UI+API tests and only when the test failed in 'call'
    if report.when == "call" and report.failed and ("ui" in item.keywords or "ui_and_api" in item.keywords):
        page = item.funcargs.get("logged_in_page")

        if page:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = SCREENSHOT_DIR / f"{item.name}_{timestamp}.png"

            page.screenshot(path=str(filename), full_page=True)

            if hasattr(report, "extra"):
                report.extra.append(extras.image(str(filename)))


# =========================
# Allure report integration
# =========================

@pytest.fixture(scope="function", autouse=True)
def allure_report(request):
    """
    Autouse fixture that attaches concise info to Allure per test.
    - attaches basic metadata
    - attaches Axe concise summary if present on request.node (no full Axe report)
    - attaches screenshot only on failure (if logged_in_page used)
    """
    # let test run
    yield

    # attach basic metadata
    try:
        meta_lines = [f"Test: {request.node.name}", f"NodeId: {getattr(request.node, 'nodeid', '')}"]
        if hasattr(request.node, "custom_log"):
            meta_lines.append("Custom log:")
            meta_lines.append(request.node.custom_log)
        allure.attach("\n".join(meta_lines), name="test-metadata", attachment_type=AttachmentType.TEXT)
    except Exception:
        logger.exception("Failed to attach test metadata to Allure")

    # attach Axe concise summary if present (only short text)
    try:
        axe_summary = getattr(request.node, "axe_summary", None)
        if axe_summary:
            allure.attach(axe_summary, name="Axe summary (concise)", attachment_type=AttachmentType.TEXT)
    except Exception:
        logger.exception("Failed to attach Axe summary to Allure")

    # attach screenshot only if test failed and logged_in_page is available
    try:
        rep = getattr(request.node, "rep_call", None)
        failed = bool(rep and getattr(rep, "failed", False))
        if failed:
            page = request.node.funcargs.get("logged_in_page")
            if page:
                try:
                    # Playwright returns bytes when no path provided
                    screenshot_bytes = page.screenshot(full_page=True)
                    allure.attach(screenshot_bytes, name=f"{request.node.name}_screenshot", attachment_type=AttachmentType.PNG)
                except Exception:
                    # fallback: save to file and attach file
                    try:
                        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                        filename = SCREENSHOT_DIR / f"{request.node.name}_{timestamp}.png"
                        page.screenshot(path=str(filename), full_page=True)
                        allure.attach.file(str(filename), name="screenshot-file", attachment_type=AttachmentType.PNG)
                    except Exception:
                        logger.exception("Failed to capture/attach screenshot for Allure")
    except Exception:
        logger.exception("Error while attaching screenshot to Allure")