"""Module Web Driver."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from threading import Thread
from typing import TYPE_CHECKING, NamedTuple

from selenium import webdriver
from selenium.webdriver import (
    ChromeOptions,
    ChromeService,
    EdgeOptions,
    EdgeService,
    FirefoxOptions,
    FirefoxService,
    IeOptions,
    IeService,
    SafariOptions,
    SafariService,
)
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from webdriver_manager.opera import OperaDriverManager
from win32api import EnumDisplayMonitors, GetMonitorInfo, GetSystemMetrics

from src.utilities import logger

if TYPE_CHECKING:
    from _typeshed import DataclassInstance
    from selenium.webdriver.chrome.webdriver import WebDriver


class BrowserBreakpoint(NamedTuple):
    """Interface representing a browser breakpoint."""

    name: str
    value: float


@dataclass
class BrowserBreakpoints:
    """Interface representing the browser breakpoints."""

    mobile: BrowserBreakpoint = field(
        default=BrowserBreakpoint(name="mobile", value=480),
    )
    tablet: BrowserBreakpoint = field(
        default=BrowserBreakpoint(name="tablet", value=768),
    )
    laptop: BrowserBreakpoint = field(
        default=BrowserBreakpoint(name="laptop", value=1024),
    )
    desktop: BrowserBreakpoint = field(
        default=BrowserBreakpoint(name="desktop", value=1536),
    )


class BrowserDevice(NamedTuple):
    """Interface representing a browser device."""

    name: str
    width: float
    height: float


@dataclass
class BrowserDevices:
    """Interface representing the browser devices."""

    galaxy_s8: BrowserDevice = field(
        default=BrowserDevice(name="Galaxy S8", width=360, height=740),
    )
    galaxy_s20: BrowserDevice = field(
        default=BrowserDevice(name="Galaxy S20", width=412, height=915),
    )
    galaxy_fold: BrowserDevice = field(
        default=BrowserDevice(name="Galaxy Fold", width=280, height=653),
    )
    ipad_mini: BrowserDevice = field(
        default=BrowserDevice(name="iPad Mini", width=768, height=1024),
    )
    ipad_air: BrowserDevice = field(
        default=BrowserDevice(name="iPad Air", width=820, height=1180),
    )
    ipad_pro: BrowserDevice = field(
        default=BrowserDevice(name="iPad Pro", width=1024, height=1366),
    )
    iphone_se: BrowserDevice = field(
        default=BrowserDevice(name="iPhone SE", width=375, height=667),
    )
    iphone_xr: BrowserDevice = field(
        default=BrowserDevice(name="iPhone XR", width=414, height=896),
    )
    nest_hub: BrowserDevice = field(
        default=BrowserDevice(name="Nest Hub", width=1024, height=600),
    )
    nest_hub_max: BrowserDevice = field(
        default=BrowserDevice(name="Nest Hub Max", width=1280, height=800),
    )
    surface_duo: BrowserDevice = field(
        default=BrowserDevice(name="Surface Duo", width=540, height=720),
    )
    surface_pro: BrowserDevice = field(
        default=BrowserDevice(name="Surface Pro", width=912, height=1368),
    )


class BrowserDrivers:
    """Interface representing the browser drivers."""

    def __init__(self: BrowserDrivers) -> None:
        pass


class BrowserStack:
    """Interface representing the selenium web driver."""

    def __init__(self: BrowserStack) -> None:
        self.driver: WebDriver = None
        self.drivers = BrowserDrivers()
        self.browsers = [
            "chrome",
            "edge",
            "explorer",
            "firefox",
            # "opera",
            # "safari",
        ]

        self.thread = None

    def launch(
        self: BrowserStack,
        browser: str,
    ) -> WebDriver:
        match browser:
            case "chrome":
                return self.chrome_driver()
            case "edge":
                return self.edge_driver()
            case "explorer":
                return self.explorer_driver()
            case "firefox":
                return self.firefox_driver()
            case "opera":
                return self.opera_driver()
            case "safari":
                return self.safari_driver()
            case _:
                logger.warn_(msg=f"Invalid Browser '{browser}' provided.")
                logger.info_(msg=f"Should be one of {self.browsers}.")
                logger.info_(msg="Launching browser using Chrome instead...")
                return self.chrome_driver()

    def maximise(
        self: BrowserStack,
    ) -> None:
        if self.driver is not None:
            self.driver.maximize_window()

    def resize(
        self: BrowserStack,
        height: float,
        width: float,
    ) -> None:
        if self.driver is not None:
            self.driver.set_window_size(height=height, width=width)

    def start(
        self: BrowserStack,
        browser: str,
        url: str,
        host: str,
        port: str,
        height: str,
        width: str,
        **options,
    ) -> None:
        if url == "":
            url = f"http://{host}:{port}"

        self.driver = self.launch(browser=browser)

        self.thread = Thread(target=self.driver.get, args=(url,))

        if "breakpoint" in options:
            width = options.get("breakpoint")
            height = min(GetSystemMetrics(1) - 100, 800)
            self.resize(height=height, width=width)
            self.driver.set_window_position(
                *position_window_center(height=height, width=width),
            )
        elif height == "" and width == "":
            self.maximise()
        else:
            self.resize(height=height, width=width)
            self.driver.set_window_position(
                *position_window_center(height=height, width=width),
            )

        # self.driver.get(url=url)  # noqa: ERA001

        self.thread.start()

    def stop(
        self: BrowserStack,
    ) -> None:
        if self.driver is not None:
            if self.driver.name == "internet explorer":
                logger.info_(msg="INTERNET EXPLORER")
                try:
                    self.driver.service.process.kill()
                    # self.driver.service.process.terminate()  # noqa: ERA001
                    # os.kill(self.driver.service.process.pid, signal.SIGTERM)  # noqa: ERA001
                except Exception:  # noqa: BLE001
                    logger.warn_(msg="ERROR KILL")
            else:
                self.driver.quit()
                if self.thread.is_alive:
                    logger.info_(msg="JOIN THREAD")
                try:
                    self.thread.join()
                    self.thread = None
                except Exception:  # noqa: BLE001
                    logger.warn_(msg="ERROR THREAD")

            # self.driver = None  # noqa: ERA001

    def chrome_driver(self: BrowserStack) -> WebDriver:
        manager = ChromeDriverManager()
        options = ChromeOptions()
        service = ChromeService(manager.install())
        return webdriver.Chrome(options=options, service=service)

    def edge_driver(self: BrowserStack) -> WebDriver:
        manager = EdgeChromiumDriverManager()
        options = EdgeOptions()
        service = EdgeService(manager.install())

        return webdriver.Edge(options=options, service=service)

    def firefox_driver(self: BrowserStack) -> WebDriver:
        manager = GeckoDriverManager()
        options = FirefoxOptions()
        service = FirefoxService(manager.install())
        return webdriver.Firefox(options=options, service=service)

    # NEED TO FIND WHY IT DOES NOT CLOSE ON QUIT COMMAND
    def explorer_driver(self: BrowserStack) -> WebDriver:
        # manager = IEDriverManager()  # noqa: ERA001
        options = IeOptions()
        # service = IeService(manager.install())  # noqa: ERA001
        path = r"C:/Users/sebas/Downloads/IEDriverServer_x64_4.14.0/IEDriverServer.exe"
        service = IeService(executable_path=path)

        return webdriver.Ie(options=options, service=service)

    # SEEMS LIKE IT IS NOT SUPPORTED BY SELENIUM ANYMORE
    # https://www.selenium.dev/documentation/webdriver/troubleshooting/errors/driver_location/#download-the-driver
    def opera_driver(self: BrowserStack) -> WebDriver:
        # ERRORS PREVENT FROM USING OPERA

        # [16280:14960:1224/113206.362:ERROR:partner_bookmarks_utils.cc(270)]
        # Unable to read partner speeddials file.

        # [16280:12696:1224/113207.256:ERROR:CONSOLE(0)]
        # "Unchecked runtime.lastError: Could not establish connection.
        # Receiving end does not exist.", source: chrome://startpage/ (0)

        # [16280:12696:1224/113207.491:ERROR:CONSOLE(0)]
        # "Unchecked runtime.lastError: Could not establish connection.
        # Receiving end does not exist.", source: chrome://rich-wallpaper/ (0)
        manager = OperaDriverManager()
        options = ChromeOptions()
        service = ChromeService(manager.install())

        options.add_argument("allow-elevated-browser")
        options.add_argument("disable-infobars")
        options.add_experimental_option(name="w3c", value=True)
        options.binary_location = "C:/Users/sebas/AppData/Local/Programs/Operaopera.exe"

        service.start()

        return webdriver.Remote(command_executor=service.service_url, options=options)

    # FIND HOW TO USE USING SUBPROCESS INSTEAD?
    # OR SETUP USING A VIRTUAL MACHINE AND MACOS IMAGE WITH Safari 10+
    def safari_driver(self: BrowserStack) -> WebDriver:
        # manager = GeckoDriverManager()  # noqa: ERA001
        options = SafariOptions()
        service = SafariService(
            executable_path="C:/Program Files (x86)/Safari/Safari.exe",
        )
        # service = SafariService(manager.install())  # noqa: ERA001
        return webdriver.Safari(options=options, service=service)


def aslist(obj: DataclassInstance):
    return list(asdict(obj).items())


def position_window_center(height: str, width: str):
    window_height = int(height)
    window_width = int(width)

    screen_width = GetSystemMetrics(0)
    screen_height = GetSystemMetrics(1)

    x = screen_width / 2 - window_width / 2
    y = screen_height / 2 - window_height / 2

    return x, y


def test_window():
    enum = EnumDisplayMonitors()

    logger.info_(msg=f"ENUM {enum}")

    handle1, handle2, rest = enum[0]

    logger.info_(f"HANDLE1 {handle1}")
    logger.info_(f"MONITOR2 {GetMonitorInfo(handle1)}")
    logger.info_(f"REST {rest}")

    for e in enum:
        logger.info_(msg=f"E {e}")
        info = GetMonitorInfo(e[0])
        logger.info_(msg=f"INFO {info}")
