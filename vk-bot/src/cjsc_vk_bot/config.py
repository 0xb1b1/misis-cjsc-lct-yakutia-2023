#!/usr/bin/env python3
import os
import sys
from loguru import logger

from cjsc_vk_bot.setup import logging

is_run_fatal = False

LOGGING_LEVEL: str = logging.validate_logging_level(
    os.getenv("CJSC_VK_BOT_LOGGING_LEVEL")
)

VK_TOKEN: str = os.getenv(
    "CJSC_VK_BOT_VK_TOKEN", ""
)
if VK_TOKEN == "":
    is_run_fatal = True
    logger.critical(
        "VK Token is not specified",
    )

ML_URL = os.getenv(
    "CJSC_VK_BOT_ML_URL", ""
)
if ML_URL == "":
    is_run_fatal = True
    logger.critical(
        "ML URL is not specified",
    )

BACKEND_URL = os.getenv(
    "CJSC_VK_BOT_BACKEND_URL", ""
)

if BACKEND_URL == "":
    is_run_fatal = True
    logger.critical(
        "Backend URL is not specified",
    )

########
if is_run_fatal:
    sys.exit(1)
