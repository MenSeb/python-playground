"""Module Judge."""


from __future__ import annotations

"""
Implement a way of judding each proxy by requesting them via
an endpoint and check which one are available at the moment.
Return that list of valid proxies and use them to fecth the urls
from other methods or programs.

SEE https://www.proxynova.com/proxy-articles/list-of-proxy-judges/
AND https://github.com/ricerati/proxy-checker-python/blob/master/proxy_checker/proxy_checker.py
"""


class Judge:
    """Interface representing the judge utilities."""

    def __init__(self: Judge) -> None:
        pass
