# badresponses.py
import logging
from typing import Dict, Callable
from playwright.sync_api import Page, Response

logger = logging.getLogger(__name__)

class BadResponses:
    def __init__(self):
        self._logger = logging.getLogger("BadResponses")
        self.bad_responses = []
        # mapowanie page -> dict(event_name -> handler)
        self._handlers: Dict[Page, Dict[str, Callable]] = {}

    def add_page(self, page: Page):
        """Attach simple handlers for response, requestfailed, pageerror and console errors."""

        handlers = {}

        def _on_response(response: Response):
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
                    "type": "response",
                    "url": response.url,
                    "status": status,
                    "resource": response.request.resource_type,
                    "page_url": page_url
                })

        handlers["response"] = _on_response
        page.on("response", _on_response)

        def _on_requestfailed(request):
            try:
                page_url = page.url
            except Exception:
                page_url = "<unknown>"

            self.bad_responses.append({
                "type": "requestfailed",
                "url": getattr(request, "url", "<unknown>"),
                "status": None,
                "resource": getattr(request, "resource_type", "<unknown>"),
                "page_url": page_url,
                "error": getattr(request, "failure", None),
            })

        handlers["requestfailed"] = _on_requestfailed
        page.on("requestfailed", _on_requestfailed)

        def _on_pageerror(error):
            try:
                page_url = page.url
            except Exception:
                page_url = "<unknown>"

            self.bad_responses.append({
                "type": "pageerror",
                "error": str(error),
                "page_url": page_url,
            })

        handlers["pageerror"] = _on_pageerror
        page.on("pageerror", _on_pageerror)

        def _on_console(msg):
            try:
                if msg.type == "error":
                    try:
                        page_url = page.url
                    except Exception:
                        page_url = "<unknown>"

                    self.bad_responses.append({
                        "type": "console",
                        "text": msg.text,
                        "page_url": page_url,
                    })
            except Exception:
                # nie przerywamy działania testu z powodu błędu w handlerze
                self._logger.exception("Error in console handler")

        handlers["console"] = _on_console
        page.on("console", _on_console)

        self._handlers[page] = handlers

    def detach(self):
        """Detach all handlers from all pages. Safe to call multiple times."""
        for page, handlers in list(self._handlers.items()):
            for event_name, handler in handlers.items():
                try:
                    if hasattr(page, "off"):
                        page.off(event_name, handler)
                    elif hasattr(page, "remove_listener"):
                        page.remove_listener(event_name, handler)
                    else:
                        # fallback: log and skip if page API doesn't support removal
                        self._logger.debug("Page has no off/remove_listener; cannot detach %s", event_name)
                except Exception:
                    self._logger.exception("Failed to detach handler %s from page", event_name)
            self._handlers.pop(page, None)


    def assert_no_bad_responses(self) -> None:
        if self.bad_responses:
            for resp in self.bad_responses:
                # prosty, czytelny log w zależności od typu wpisu
                if resp.get("type") == "response":
                    self._logger.error(
                        f"Bad response: {resp['status']} "
                        f"[{resp['resource']}] {resp['url']} (page: {resp['page_url']})"
                    )
                elif resp.get("type") == "requestfailed":
                    self._logger.error(
                        f"Request failed: {resp.get('url')} error={resp.get('error')} (page: {resp['page_url']})"
                    )
                elif resp.get("type") == "pageerror":
                    self._logger.error(
                        f"Page error: {resp.get('error')} (page: {resp['page_url']})"
                    )
                elif resp.get("type") == "console":
                    self._logger.error(
                        f"Console error: {resp.get('text')} (page: {resp['page_url']})"
                    )
                else:
                    self._logger.error("Captured issue: %s", resp)
            raise AssertionError(f"Invalid responses or errors found: {self.bad_responses}")
