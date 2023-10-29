"""Module Clone."""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

from bs4 import BeautifulSoup, ResultSet, Tag
from utilities.logger import logger

if TYPE_CHECKING:
    from utilities.session import Session


class Clone:
    """Interface representing clone utilities."""

    def __init__(
        self: Clone,
        domain: str,
        markup: str | bytes,
        folder: str = "temp",
        directory: Path = Path(__file__).parent,
    ) -> None:
        """Interface representing clone utilities.

        Args:
        ----
            domain (str):
                The website domain to clone.
            markup (str | bytes):
                The website markup to clone.
            folder (str, optional):
                The clone folder. Defaults to "temp".
            directory (Path, optional):
                The clone directory. Defaults to Path(__file__).parent.
        """
        self.assets: list[str] = []
        self.domain = domain
        self.soup = BeautifulSoup(markup=markup, features="html5lib")
        self.path = directory / folder / domain[domain.index("//") + 2 : -1]
        self.path_assets = Path("assets")
        self.setup()

    def setup(
        self: Clone,
    ) -> None:
        """Create the directory and folders for the cloned website."""
        logger.trace_()

        self.path.mkdir(exist_ok=True, parents=True)
        (self.path / self.path_assets).mkdir(exist_ok=True)

    def save_html(
        self: Clone,
    ) -> int:
        """Save the HTML clone."""
        logger.trace_()

        return (self.path / "index.html").write_text(
            data=self.soup.prettify(),
            encoding="utf-8",
        )

    def save_asset(
        self: Clone,
        data: bytes,
        filename: str,
    ) -> None:
        """Save an asset file.

        Args:
        ----
            data (bytes):
                The asset data.
            filename (str):
                The asset filename.
        """
        logger.trace_(msg=filename)

        (self.path / self.path_assets / filename).write_bytes(data=data)

    def sync_images(
        self: Clone,
        session: Session,
    ) -> None:
        """Sync the images from the cloned website.

        Args:
        ----
            session (Session):
                The requests session.
        """
        images: ResultSet[Tag] = self.soup.find_all(name="img")

        for image in images:
            with_src = "src" in image.attrs
            with_data = "data-cfsrc" in image.attrs

            if (
                not (with_src or with_data)
                or with_src
                and image["src"].startswith("https")
            ):
                continue

            source = image["src"] if with_src else image["data-cfsrc"]
            path = Path(source)
            index = path.suffix.find("?")
            filename = path.name if index < 0 else path.stem + path.suffix[0:index]
            image["src"] = self.path_assets / filename

            if (self.path / self.path_assets / filename).exists():
                self.assets.append(filename)
                continue

            response = session.request(url=self.domain + source)

            if response is not None:
                self.save_asset(
                    data=response.content,
                    filename=filename,
                )
                self.assets.append(filename)

    def sync_links(
        self: Clone,
        session: Session,
    ) -> None:
        """Sync the links from the cloned website.

        Args:
        ----
            session (Session):
                The requests session.
        """
        links: ResultSet[Tag] = self.soup.find_all(name="link")

        for link in links:
            if "href" not in link.attrs or link["href"].startswith("https"):
                continue

            source: str = link["href"]

            if source.startswith("//"):
                link["href"] = "https:" + source
                continue

            path = Path(source)
            index = path.suffix.find("?")
            filename = path.name if index < 0 else path.stem + path.suffix[0:index]
            link["href"] = self.path_assets / filename

            if (self.path / self.path_assets / filename).exists():
                self.assets.append(filename)
                continue

            response = session.request(url=self.domain + source)

            if response is not None:
                self.save_asset(
                    data=response.content,
                    filename=filename,
                )
                self.assets.append(filename)

    def sync_scripts(
        self: Clone,
        session: Session,
        *,
        nosync: bool = True,
    ) -> None:
        """Sync the scripts from the cloned website.

        Args:
        ----
            session (Session):
                The requests session.
            nosync (bool, optional):
                If true, remove the scripts. Defaults to True.
        """
        noscripts: ResultSet[Tag] = self.soup.find_all(name="noscript")
        for noscript in noscripts:
            noscript.extract()

        scripts: ResultSet[Tag] = self.soup.find_all(name="script")
        for script in scripts:
            if nosync or "src" not in script.attrs or script["src"].startswith("https"):
                script.extract()
                continue

            source: str = script["src"]
            path = Path(source)
            index = path.suffix.find("?")
            filename = path.name if index < 0 else path.stem + path.suffix[0:index]
            script["src"] = self.path_assets / filename

            if (self.path / self.path_assets / filename).exists():
                self.assets.append(filename)
                continue

            response = session.request(url=self.domain + source)

            if response is not None:
                self.save_asset(
                    data=response.content,
                    filename=filename,
                )
                self.assets.append(filename)

    def sync_fonts(
        self: Clone,
        session: Session,
    ) -> None:
        """Sync the fonts from the cloned website.

        Args:
            session (Session):
                The requests session.
        """
        stylesheets = list(
            filter(lambda filename: filename.endswith("css"), self.assets),
        )

        for stylesheet in stylesheets:
            path_stylesheet = self.path / self.path_assets / stylesheet
            content = path_stylesheet.read_text()

            sources: list[str] = re.findall(r"url\(([^)]+)\)", string=content)

            for source in sources:
                url = source.replace('"', "")
                path = Path(url)
                index = path.suffix.find("?")
                filename = path.name if index < 0 else path.stem + path.suffix[0:index]

                if (self.path / self.path_assets / filename).exists():
                    self.assets.append(filename)
                    continue

                response = session.request(url=self.domain + url, delay=2)

                if response is not None:
                    self.save_asset(
                        data=response.content,
                        filename=filename,
                    )
                    content = content.replace(url, filename)
                    self.assets.append(filename)

            path_stylesheet.write_text(data=content)
