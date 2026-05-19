import logging
from playwright.sync_api import Page


class BoardPage():
    def __init__(self, page: Page):
        self._logger = logging.getLogger("Board Page")
        self.page = page


    def create_board(self, board_name: str):
        pass