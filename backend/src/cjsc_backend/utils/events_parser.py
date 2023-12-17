#!/usr/bin/env python3
from bs4 import BeautifulSoup
from urllib import parse as urlparse
import requests
from loguru import logger

from cjsc_backend.http.schemas.event import \
    CityEvent


def parse_events() -> list[CityEvent]:
    logger.info("Parsing City Events")
    BASE_URL: str = "https://xn----8sba3afqixm5b9c.xn--p1ai/sobytiya"

    events_page = requests.get(BASE_URL)
    bs = BeautifulSoup(events_page.content, features="html.parser")
    all_events = bs.find_all("div", {"class": "news-item-lenta__descr-top"})

    events_collection: list[CityEvent] = []

    for index, event in enumerate(all_events):
        if index > 2:  # Parse 3 objects
            break
        # print(news)
        title_link = event.find("a")
        title = title_link.text
        link = urlparse.urljoin(
            BASE_URL,
            title_link["href"],
        )
        description = event.find("p").text

        events_collection.append(
            CityEvent(
                title=title,
                description=description,
                link=link,
            )
        )

    logger.info("Finished parsing City Events")

    return events_collection
