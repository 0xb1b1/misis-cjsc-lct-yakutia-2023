#!/usr/bin/env python3
from yandexfreetranslate import YandexFreeTranslate

yt = YandexFreeTranslate(api="ios")


def translate(text: str, source: str = "en", target: str = "ru") -> str:
    return yt.translate(
        source=source,
        target=target,
        text=text,
    )
