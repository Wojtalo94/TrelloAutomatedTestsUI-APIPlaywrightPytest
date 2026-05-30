import os
import pytest
import base64
import logging
import datetime
from pathlib import Path
from pytest_html import extras
from pages.home_page import HomePage
from pytest_playwright_axe import Axe
from playwright.sync_api import Playwright
from api.rest_controller import RestController
from helpers.bad_responses import BadResponses
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

    def on_new_page(new_page):
        logger.info("New page detected and attached to BadResponses")
        bad.add_page(new_page)

    context.on("page", on_new_page)
    try:
        yield bad

    finally:
        try:
            if hasattr(context, "remove_listener"):
                context.remove_listener("page", on_new_page)
            elif hasattr(context, "off"):
                context.off("page", on_new_page)
            else:
                logger.debug("BrowserContext has no remove_listener/off method; leaving listener attached")
        except Exception as e:
            logger.warning(f"Failed to detach page listener: {e}")

        bad.assert_no_bad_responses()

# =========================
# Axe fixtures and helpers
# =========================

@pytest.fixture(scope="session")
def axe_instance():
    """
    Session-scoped Axe instance configured to fail on critical/serious is desabled.
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
            # Build concise summary for pytest failure
            summary_lines = []
            for v in violations:
                impact = v.get("impact", "")
                summary_lines.append(f"{v['id']} ({impact}) - {v.get('description','')}")
                # include first target per violation for quick debugging
                nodes = v.get("nodes", [])
                if nodes:
                    targets = nodes[0].get("target", [])
                    if targets:
                        summary_lines.append(f"  target: {', '.join(targets)}")
            summary = "\n".join(summary_lines)
            pytest.fail(f"A11y violations found ({len(violations)}):\n{summary}")

    return _check


# =========================
# Pytest-html integration
# =========================

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Attach axe report paths from the test node to the test report object so pytest-html hooks can render them.
    Additionally, if the test fails (rep.when == 'call' and rep.failed), it takes a screenshot and attaches it to pytest-html.
    """
    outcome = yield
    rep = outcome.get_result()
    # copy attributes if present
    axe_html = getattr(item, "axe_html", None)
    axe_json = getattr(item, "axe_json", None)
    if axe_html:
        rep.axe_html = axe_html
    if axe_json:
        rep.axe_json = axe_json

    # only for UI / accessibility tests and only when the test failed in 'call'
    if rep.when == "call" and rep.failed and ("ui" in item.keywords or "accessibility" in item.keywords):
        page = item.funcargs.get("logged_in_page")

        if page is not None and hasattr(page, "screenshot") and callable(getattr(page, "screenshot")):
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_test_name = item.name.replace(" ", "_").replace("/", "_")
            filename = SCREENSHOT_DIR / f"{safe_test_name}_{ts}.png"
            try:
                page.screenshot(path=str(filename), full_page=True)
                if not hasattr(rep, "extra"):
                    rep.extra = []
                rep.extra.append(extras.image(str(filename)))
            except Exception as e:
                logging.getLogger(__name__).exception(f"Failed to capture screenshot: {e}")
        else:
            logging.getLogger(__name__).debug("logged_in_page fixture not found or has no screenshot method; skipping screenshot.")


def pytest_html_results_table_html(report, data):
    """
    Append Axe HTML (iframe) and JSON (pre) to pytest-html report for each test.
    """
    axe_html = getattr(report, "axe_html", None)
    axe_json = getattr(report, "axe_json", None)


    if axe_html:
        try:
            raw = Path(axe_html).read_bytes()
            b64 = base64.b64encode(raw).decode("ascii")
            data_uri = f"data:text/html;base64,{b64}"
            data.append(f"<h4>Axe Accessibility Report</h4><iframe src='{data_uri}' width='100%' height='500px'></iframe>")
        except Exception:
            # fallback to file path
            data.append(f"<h4>Axe Accessibility Report</h4><iframe src='{axe_html}' width='100%' height='500px'></iframe>")


    if axe_json:
        try:
            content = Path(axe_json).read_text(encoding="utf-8")
            # limit size to avoid huge HTML rows
            if len(content) > 20000:
                content = content[:20000] + "\n... (truncated)"
            data.append(f"<h4>Axe JSON</h4><pre style='max-height:300px;overflow:auto'>{content}</pre>")
        except Exception:
            pass