# app/core/logging.py
import logging
import sys

import structlog


def configure_logging(level: str = 'INFO') -> None:
    numeric = logging.getLevelNamesMapping()[level.upper()]
    logging.basicConfig(format='%(message)s', stream=sys.stdout, level=numeric)
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt='iso', utc=True),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(numeric),
        cache_logger_on_first_use=True,
    )