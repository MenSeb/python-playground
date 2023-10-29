"""Module Logger."""


from __future__ import annotations

import logging
import sys


class Logger:
    """Interface representing logger utilities."""

    def __init__(
        self: Logger,
        *,
        debugging: bool = False,
        tracing: bool = False,
        newline: bool = True,
    ) -> None:
        formatter = "%(name)s:%(levelname)s => %(msg)s" + "\n" if newline else ""
        handler = logging.StreamHandler()
        handler.setFormatter(fmt=logging.Formatter(fmt=formatter))
        logger = logging.getLogger(name="LOG")
        logger.addHandler(hdlr=handler)
        logger.setLevel(level=logging.DEBUG if debugging else logging.INFO)

        self.logger = logger
        self.debugging = debugging
        self.tracing = tracing
        self.newline = newline

    def debug_(self: Logger, msg: str) -> None:
        """Log a message with severity 'DEBUG'."""
        self.logger.debug(msg=msg)

    def warn_(self: Logger, msg: str) -> None:
        """Log a message with severity 'WARN'."""
        self.logger.warning(msg=msg)

    def info_(self: Logger, msg: str) -> None:
        """Log a message with severity 'INFO'."""
        self.logger.info(msg=msg)

    def error_(self: Logger, msg: str) -> None:
        """Log a message with severity 'ERROR'."""
        self.logger.error(msg=msg)

    def critical_(self: Logger, msg: str) -> None:
        """Log a message with severity 'CRITICAL'."""
        self.logger.critical(msg=msg)

    def trace_(self: Logger, msg: str | None = None) -> None:
        """Log a message with severity 'DEBUG' tracing the called function."""
        if not self.tracing:
            return

        frame = sys._getframe(1)  # noqa: SLF001

        message = "TRACE"

        if "self" in frame.f_locals:
            message += f" - CLASS {frame.f_locals['self'].__class__.__name__}"

        message += f" - FUNCTION {frame.f_code.co_name}"

        if msg is not None:
            message += f" - {msg}"

        self.info_(msg=f"{message}")


logger = Logger(tracing=True)
