#!/usr/bin/env python3

import os
import sys
from loguru import logger

from cjsc_ml.setup import logging, webserver_port

is_run_fatal = False

LOGGING_LEVEL: str = logging.validate_logging_level(
    os.getenv("CJSC_ML_LOGGING_LEVEL")
)

WEBSERVER_HOST: str = os.getenv(
    "CJSC_ML_WEBSERVER_HOST",
    "0.0.0.0"
)

WEBSERVER_PORT, IS_WEBSERVER_PORT_DEFAULT = webserver_port.validate_webserver_port(  # noqa: E501
    os.getenv("CJSC_ML_WEBSERVER_PORT")
)

MONGO_URL: str = os.getenv("CJSC_ML_MONGO_URL", "")
if MONGO_URL == "":
    logger.critical("MongoDB URL is not specified.")
    is_run_fatal = True

MONGO_ML_DB: str = os.getenv("CJSC_ML_MONGO_ML_DB", "")
if MONGO_ML_DB == "":
    logger.critical("MongoDB ML Database is not specified.")
    is_run_fatal = True

MONGO_ASSETS_DB: str = os.getenv("CJSC_ML_MONGO_ASSETS_DB", "")
if MONGO_ASSETS_DB == "":
    logger.critical("MongoDB Assets Database is not specified.")
    is_run_fatal = True

# Local services


########
if is_run_fatal:
    sys.exit(1)
