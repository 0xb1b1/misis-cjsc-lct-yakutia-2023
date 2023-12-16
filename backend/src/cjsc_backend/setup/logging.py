#!/usr/bin/env python3

def validate_logging_level(logging_level: str) -> str:
    """
    This function validates the logging level and,
    if it's valid, returns the string in the correct
    (upper-case) format. If logging_level is NoneType,
    logging level defaults to DEBUG.

    Args:
        logging_level (str): Logging level string value.

    Returns:
        str: Formatted logging level.

    Raises:
        ValueError: The logging level string does not adhere to the convention.
    """

    LOGGING_LEVELS = [
        "TRACE",
        "DEBUG",
        "INFO",
        "SUCCESS",
        "WARNING",
        "ERROR",
        "CRITICAL"
    ]

    if logging_level is None:
        return "DEBUG"

    llvl = logging_level.upper()

    if llvl not in LOGGING_LEVELS:
        raise ValueError("The logging level string is incorrect.")

    return llvl
