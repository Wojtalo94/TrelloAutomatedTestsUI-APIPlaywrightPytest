import re
import calendar
from typing import List
from datetime import date
from dateutil.relativedelta import relativedelta


def refresh_and_wait(page):
    page.reload()
    page.wait_for_load_state("networkidle")


def date_months_back_with_slash(months_back: int) -> str:
    target_date = date.today() - relativedelta(months=months_back)
    return target_date.strftime('%d/%m/%Y')


def date_months_forward_with_slash(months_forward: int) -> str:
    target_date = date.today() + relativedelta(months=months_forward)
    return target_date.strftime('%d/%m/%Y')


def date_months_back_with_dot(months_back: int) -> str:
    target_date = date.today() - relativedelta(months=months_back)
    return target_date.strftime('%d.%m.%Y')


def date_months_forward_with_dot(months_forward: int) -> str:
    target_date = date.today() + relativedelta(months=months_forward)
    return target_date.strftime('%d.%m.%Y')


def normalize_string(s: str) -> str:
    s = s.strip()
    s = re.sub(r"\s*-\s*", "-", s)
    s = re.sub(r"\s+", " ", s)
    return s


def normalize_list(s: str) -> List[str]:
    """
    Normalizes a comma-separated list of elements.
    - splits after commas,
    - removes leading/trailing whitespaces from each element,
    - skips empty elements (e.g., resulting from “, ,”),
    - returns the list while preserving the order.
    """
    if s is None:
        return []
    return [part.strip() for part in s.split(",") if part.strip()]


def first_day_current_month() -> str:
    today = date.today()
    first = date(today.year, today.month, 1)
    return first.strftime("%d.%m.%Y")


def last_day_current_month() -> str:
    today = date.today()
    last_day = calendar.monthrange(today.year, today.month)[1]
    last = date(today.year, today.month, last_day)
    return last.strftime("%d.%m.%Y")