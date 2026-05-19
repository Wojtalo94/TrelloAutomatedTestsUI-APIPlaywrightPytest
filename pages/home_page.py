import logging
from playwright.sync_api import Page


class HomePage():
    def __init__(self, page: Page):
        self._logger = logging.getLogger("Base Page")
        self.page = page
        self._log_in_field = page.get_by_role("link", name="Log in").nth(0)
        self._email_field = page.locator("input[name='username']")
        self._password_field = page.locator("input[type='password']")
        self._submit_login_field = page.get_by_test_id("login-submit-idf-testid")
        self._without_two_step_verification_field = page.get_by_test_id("mfa-promote-dismiss-idf-testid")
        self._main_page_field = page.locator('input[name="x"]')


    def sign_in_to_home_page(self, BASE_URL: str, EMAIL: str, PASSWORD: str):
        self._logger.info("Sign in to home page")
        self.page.goto(BASE_URL)

        self._log_in_field.click()
        self._email_field.fill(EMAIL)
        self._submit_login_field.click()
        self._password_field.fill(PASSWORD)
        self._submit_login_field.click()
        #self._without_two_step_verification_field.click()

        self.page.wait_for_load_state(timeout=15000)