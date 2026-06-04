import logging
from urllib.parse import urljoin
from playwright.sync_api import Page
from config.config_loader import BASE_URL, LOGIN


class MainPage():
    def __init__(self, page: Page):
        self._logger = logging.getLogger("Main Page")
        self.page = page


    def open_main_page(self) -> None:
        url = urljoin(BASE_URL, f"u/{LOGIN}/boards")
        self._logger.info("Open main page: %s", url)
        self.page.goto(url)
        self.page.wait_for_load_state(timeout=15000)