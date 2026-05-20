import logging
from playwright.sync_api import Page


class BoardPage():
    def __init__(self, page: Page):
        self._logger = logging.getLogger("Board Page")
        self.page = page
        # 'create board' locators
        self._create_board_button = page.get_by_test_id("create-board-tile")
        self._board_name_field = page.get_by_test_id("create-board-title-input")
        self._confirm_create_board_button = page.get_by_test_id("create-board-submit-button")
        # 'table menu' locators
        self._show_menu = page.get_by_test_id("OverflowMenuHorizontalIcon")
        self._close_board_button = page.get_by_role("button", name="Zamknij tablicę")
        self._confirm_close_board_button = page.get_by_role("button", name="Zamknij")
        # 'side menu' locators
        self._board_view_button = page.get_by_role("button", name="Tablice")
        # 'delete board' locators
        self._all_closed_boards_button = page.get_by_role("button", name="Wyświetl wszystkie zamknięte tablice")
        self._delete_board_button = page.get_by_test_id("close-board-delete-board-button")
        self._confirm_delete_board_button = page.get_by_test_id("close-board-delete-board-confirm-button")
        self._text_for_verification_of_lack_of_tables = page.get_by_test_id("no-boards-to-reopen")


    def create_board(self, board_name: str) -> None:
        self._logger.info(f"Creating an board named: '{board_name}'")
        self._create_board_button.click()
        self._confirm_close_board_button.fill(board_name)
        self._confirm_create_board_button.click()


    def delete_board(self, board_name: str) -> None:
        self._logger.info(f"Deleting an board named: '{board_name}'")
        self._show_menu.click()
        self._close_board_button.click()
        self._confirm_close_board_button.click()

        self._board_view_button.click()
        self.page.wait_for_load_state(timeout=15000)

        self._all_closed_boards_button.click()
        self._delete_board_button.click()
        self._confirm_delete_board_button.click()

    def check_that_all_boards_have_been_removed(self) -> None:
        self._logger.info("Checking if there is no message about lack of open board")
        assert self._text_for_verification_of_lack_of_tables == "Żadne tablice nie zostały zamknięte", ("There is no message about lack of open boards")
