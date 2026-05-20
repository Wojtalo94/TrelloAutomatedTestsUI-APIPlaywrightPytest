import logging
from playwright.sync_api import Page


class BadResponses:
    def __init__(self):
        self._logger = logging.getLogger("BadResponses")
        self.bad_responses = []

    def add_page(self, page: Page):
        """Podłącza nasłuch na response dla tej konkretnej strony."""

        def _on_response(response):
            try:
                status = response.status
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
        """Sprawdza zebrane złe odpowiedzi."""
        if self.bad_responses:
            for resp in self.bad_responses:
                self._logger.error(
                    f"Bad response: {resp['status']} "
                    f"[{resp['resource']}] {resp['url']} (page: {resp['page_url']})"
                )
            raise AssertionError(f"Invalid HTTP responses found: {self.bad_responses}")
