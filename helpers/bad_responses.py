import logging
from playwright.sync_api import Page


class BadResponses:
    def __init__(self):
        self._logger = logging.getLogger("BadResponses")
        self.bad_responses = []

    def add_page(self, page: Page):
        """
        Attaches a Playwright response listener to the given page.
        Collects all HTTP responses with status >= 400 (client/server errors) and stores them in memory for later validation.
        This allows passive monitoring of network failures during E2E tests without interrupting test execution immediately.
        """

        def _on_response(response):
            try:
                status = response.status
            # ignore Playwright errors
            except Exception:
                return

            if status >= 400:
                try:
                    page_url = page.url
                except Exception:
                    page_url = "<unknown>"

                self.bad_responses.append({
                    "url": response.url,
                    "status": status,
                    "resource": response.request.resource_type,
                    "page_url": page_url
                })

        page.on("response", _on_response)

    def assert_no_bad_responses(self) -> None:
        """
        Asserts that no HTTP errors (status >= 400) were captured during the test run.
        Iterates through all collected bad responses, logs detailed information about each failure (URL, status code, resource type, and page context), and fails the test if any invalid responses were detected.
        This acts as a final safeguard to ensure frontend does not trigger hidden API or asset failures during E2E execution.
        """
        if self.bad_responses:
            for resp in self.bad_responses:
                self._logger.error(
                    f"Bad response: {resp['status']} "
                    f"[{resp['resource']}] {resp['url']} (page: {resp['page_url']})"
                )
            raise AssertionError(f"Invalid HTTP responses found: {self.bad_responses}")
