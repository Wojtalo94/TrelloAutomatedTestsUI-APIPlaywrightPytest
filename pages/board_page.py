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
        self._show_menu = page.get_by_role("button", name="Pokaż menu")
        self._close_board_button = page.get_by_role("button", name="Zamknij tablicę")
        self._confirm_close_board_button = page.get_by_test_id("popover-close-board-confirm")
        # 'side menu' locators
        self._back_to_home_page = page.get_by_test_id("header-logo-glyph-and-text") 
        # 'delete board' locators
        self._all_closed_boards_button = page.get_by_role("button", name="Wyświetl wszystkie zamknięte tablice")
        self._delete_board_button = page.get_by_test_id("close-board-delete-board-button")
        self._confirm_delete_board_button = page.get_by_test_id("close-board-delete-board-confirm-button")
        self._text_for_verification_of_lack_of_tables = page.get_by_test_id("no-boards-to-reopen")
        self._board_share_button = page.get_by_test_id("board-share-button")
        self._close_window_closed_boards = page.locator('button:has(span[data-testid="CloseIcon"])')


    def create_board(self, board_name: str) -> None:
        self._logger.info(f"Creating an board named: '{board_name}'")
        self._create_board_button.click()
        self._board_name_field.fill(board_name)
        self._confirm_create_board_button.click()
        self.page.wait_for_load_state(timeout=15000)


    def delete_board(self, board_name: str) -> None:
        self._logger.info(f"Deleting an board named: '{board_name}'")
        self._board_share_button.wait_for(state="visible", timeout=5000)
        self._show_menu.click()
        self._close_board_button.click()
        self._confirm_close_board_button.click()

        self._back_to_home_page.click()
        self.page.wait_for_load_state(timeout=15000)

        self._all_closed_boards_button.click()
        self._delete_board_button.click()
        self._confirm_delete_board_button.click()


    def check_that_all_boards_have_been_removed(self) -> None:
        self._logger.info("Checking if there is no message about lack of open board")
        text_to_verify = self._text_for_verification_of_lack_of_tables.inner_text()
        assert text_to_verify == "Żadne tablice nie zostały zamknięte", f"Text is '{text_to_verify}', should be 'Żadne tablice nie zostały zamknięte'"
        self._close_window_closed_boards.click()
        self.page.wait_for_load_state(timeout=15000)