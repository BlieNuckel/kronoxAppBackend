from typing import Dict
from fastapi import Response
import re

from src.util.schools_info import SCHOOL_BASE_URLS, VALID_SCHOOLS
from src.kronox_scraper.kronox_scrape import runKronoxSearch


def searchSchedules(school: str, search: str | None) -> Dict | Response:
    if search is None:
        return Response(content="Illegal search query", status_code=404)
    if school not in VALID_SCHOOLS:
        return Response(content="Invalid school query", status_code=404)

    try:
        year = re.search(r"[1-9]\d{3,}", search).group()
        search = search.replace(year, "")
    except AttributeError:
        year = ""

    fullResults = runKronoxSearch(search, year, SCHOOL_BASE_URLS[school])
    # filteredResults = await sortValid(fullResults, SCHOOL_BASE_URLS[school])

    return {"requestedSchedule": fullResults}
