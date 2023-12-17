#!/usr/bin/env python3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.exceptions import RequestValidationError
# from fastapi.responses import JSONResponse
from loguru import logger
import uvicorn
import sys

from cjsc_backend import config


def run() -> None:
    # Set up Loguru
    logger.remove()
    logger.add(sys.stderr, level=config.LOGGING_LEVEL)
    logger.critical(f"Logging level set to {config.LOGGING_LEVEL}.")

    # Sentry
    import sentry_sdk
    from sentry_sdk.integrations.pymongo import PyMongoIntegration
    from sentry_sdk.integrations.loguru import LoguruIntegration
    sentry_sdk.init(
        dsn="https://504cad1b6c754661b2fb793b9162359c@glitchtip.seizure.icu/2",
        enable_tracing=True,
        integrations=[
            PyMongoIntegration(),
            LoguruIntegration(),
        ],
    )
    logger.info("Initialized Sentry.")

    from cjsc_backend.http.routers.messages import router as msg_router
    from cjsc_backend.http.routers.utils import router as utils_router
    from cjsc_backend.http.routers.users import router as users_mouter

    from cjsc_backend.http.routers.signals import router as sig_router

    app = FastAPI()

    # CORS Policy
    origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(msg_router)
    app.include_router(utils_router)
    app.include_router(users_mouter)

    app.include_router(sig_router)

    logger.info(f"Starting FastAPI on port {config.WEBSERVER_PORT}.")
    if config.IS_WEBSERVER_PORT_DEFAULT:
        logger.warning("Running webserver on standard port.")
    uvicorn.run(
        app,
        host=config.WEBSERVER_HOST,
        port=config.WEBSERVER_PORT
    )


if __name__ == "__main__":
    run()
