"""Module Logger."""


from __future__ import annotations

import logging
import sys


class Logger:
    """Interface representing logger utilities."""

    def __init__(self: Logger, *, debug: bool = False) -> None:
        logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)

    def debug_(self: Logger, msg: str) -> None:
        """Log a message with severity 'DEBUG'."""
        logging.debug(msg=msg)

    def warn_(self: Logger, msg: str) -> None:
        """Log a message with severity 'WARN'."""
        logging.warning(msg=msg)

    def info_(self: Logger, msg: str) -> None:
        """Log a message with severity 'INFO'."""
        logging.info(msg=msg)

    def error_(self: Logger, msg: str) -> None:
        """Log a message with severity 'ERROR'."""
        logging.error(msg=msg)

    def critical_(self: Logger, msg: str) -> None:
        """Log a message with severity 'CRITICAL'."""
        logging.critical(msg=msg)

    def trace_(self: Logger, msg: str | None = None) -> None:
        """Log a message with severity 'DEBUG' tracing the called function."""
        function = sys._getframe(1).f_code.co_name  # noqa: SLF001

        self.debug_(msg=f"CALL function {function}. {msg}")


logger = Logger()
