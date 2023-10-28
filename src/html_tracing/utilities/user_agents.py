"""Module User Agents."""

from __future__ import annotations


class UserAgents:
    """Interface representing user agents utilities.

    MDN Web Docs:
    -
    The User-Agent request header is a characteristic string that lets servers and
    network peers identify the application, operating system, vendor, and/or version
    of the requesting user agent.

    Wikepedia:
    -
    The user agent plays the role of the client in a client-server system. The HTTP
    User-Agent header is intended to clearly identify the agent to the server. This
    header can be omitted/spoofed, so some websites use other agent detection methods.
    """

    def __init__(self: UserAgents) -> None:
        pass
