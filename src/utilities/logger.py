"""Module Logger."""


from __future__ import annotations

import logging
import sys


class Logger:
    """Interface representing logger utilities."""

    def __init__(
        self: Logger,
        name: str = "LOG",
        formatter: str = "%(name)s:%(levelname)s => %(msg)s",
        debugging: bool = False,
        tracing: bool = False,
        newline: bool = True,
    ) -> None:
        """Initiate a logger.

        Parameters
        ----------
        name : str, optional
            The name of the the logger, by default "LOG"
        formatter: str, optional
            The logger format, by default "%(name)s:%(levelname)s => %(msg)s"
        debugging : bool, optional
            Set logging level to DEBUG otherwise INFO, by default False
        tracing : bool, optional
            Trace method calls when using _trace, by default False
        newline : bool, optional
            Add a new line between logs, by default True
        """
        if newline:
            formatter += "\n"

        handler = logging.StreamHandler()
        handler.setFormatter(fmt=logging.Formatter(fmt=formatter))

        logger = logging.getLogger(name=name)
        logger.addHandler(hdlr=handler)
        logger.setLevel(level=logging.DEBUG if debugging else logging.INFO)

        self.logger = logger
        self.debugging = debugging
        self.tracing = tracing
        self.newline = newline

    def debug_(self: Logger, msg: str) -> None:
        """Log a message with severity DEBUG.

        Parameters
        ----------
        msg : str
            The message to display.
        """
        self.logger.debug(msg=msg)

    def warn_(self: Logger, msg: str) -> None:
        """Log a message with severity WARN.

        Parameters
        ----------
        msg : str
            The message to display.
        """
        self.logger.warning(msg=msg)

    def info_(self: Logger, msg: str) -> None:
        """Log a message with severity INFO.

        Parameters
        ----------
        msg : str
            The message to display.
        """
        self.logger.info(msg=msg)

    def error_(self: Logger, msg: str) -> None:
        """Log a message with severity ERROR.

        Parameters
        ----------
        msg : str
            The message to display.
        """
        self.logger.error(msg=msg)

    def critical_(self: Logger, msg: str) -> None:
        """Log a message with severity CRITICAL.

        Parameters
        ----------
        msg : str
            The message to display.
        """
        self.logger.critical(msg=msg)

    def trace_(self: Logger, msg: str | None = None) -> None:
        """Log a message with severity 'DEBUG' to trace methods call.

        Parameters
        ----------
        msg : str | None, optional
            The message to display, by default None.
        """
        if not self.tracing:
            return

        frame = sys._getframe(1)  # noqa: SLF001

        message = "TRACE"

        # Trace class name if method is from a class
        if "self" in frame.f_locals:
            message += f" - CLASS {frame.f_locals['self'].__class__.__name__}"

        # Trace method name
        message += f" - METHOD {frame.f_code.co_name}"

        if msg is not None:
            message += f" - {msg}"

        self.info_(msg=f"{message}")
