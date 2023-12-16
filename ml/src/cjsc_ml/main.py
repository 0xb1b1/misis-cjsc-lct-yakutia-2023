#!/usr/bin/env python3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.exceptions import RequestValidationError
# from fastapi.responses import JSONResponse
from loguru import logger
import uvicorn
import sys

from cjsc_ml import config


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
        dsn="https://7d8c78f5e21c4f168304a451fa130dbf@glitchtip.seizure.icu/3",
        enable_tracing=True,
        integrations=[
            PyMongoIntegration(),
            LoguruIntegration(),
        ],
    )
    logger.info("Initialized Sentry.")

    from cjsc_ml.http.routers.messages import router as msg_router

    from cjsc_ml.http.routers.signals import router as sig_router

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
    app.include_router(sig_router)

    logger.info(f"Starting FastAPI on port {config.WEBSERVER_PORT}.")
    if config.IS_WEBSERVER_PORT_DEFAULT:
        logger.warning("Running webserver on standard port.")
    uvicorn.run(
        app,
        host=config.WEBSERVER_HOST,
        port=config.WEBSERVER_PORT,
        log_level="debug"
    )


if __name__ == "__main__":
    run()
