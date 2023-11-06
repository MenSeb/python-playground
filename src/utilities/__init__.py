"""Package Utilities."""


from .logger import Logger

__all__ = ["Logger"]

logger = Logger(tracing=True)
