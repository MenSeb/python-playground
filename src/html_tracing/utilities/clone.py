"""Module Clone."""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

from bs4 import BeautifulSoup, ResultSet, Tag

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
        self.path.mkdir(
            exist_ok=True,
            parents=True,
        )
        (self.path / self.path_assets).mkdir(exist_ok=True)

    def save_html(
        self: Clone,
    ) -> int:
        """Save the HTML clone."""
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
        images = self.soup.find_all(name="img")

        for image in images:
            source = image["src"]
            filename = Path(source).name
            image["src"] = self.path_assets / filename
            self.assets.append(filename)
            response = session.request(url=self.domain + source)

            if response is not None:
                self.save_asset(
                    data=response.content,
                    filename=filename,
                )

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
        stylesheets = self.soup.find_all(name="link")

        for stylesheet in stylesheets:
            source: str = stylesheet["href"]

            if source.startswith("https"):
                continue

            path = Path(source)
            index = path.suffix.find("?")
            filename = path.name if index < 0 else path.stem + path.suffix[0:index]
            self.assets.append(filename)
            stylesheet["href"] = self.path_assets / filename
            response = session.request(url=self.domain + source)

            if response is not None:
                self.save_asset(
                    data=response.content,
                    filename=filename,
                )

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
            filename = path.stem + path.suffix[0 : path.suffix.find("?")]
            self.assets.append(filename)
            script["src"] = self.path_assets / filename
            response = session.request(url=self.domain + source)

            if response is not None:
                self.save_asset(
                    data=response.content,
                    filename=filename,
                )

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

            sources: list[str] = re.findall(r"src: ?url\(([^)]+)\)", string=content)

            for source in sources:
                url = source.replace('"', "")
                response = session.request(self.domain + url)

                if response is not None:
                    path = Path(url)
                    filename = path.stem + path.suffix[0 : path.suffix.find("?")]
                    self.assets.append(filename)
                    path_stylesheet.write_text(data=content.replace(url, filename))
                    self.save_asset(
                        data=response.content,
                        filename=filename,
                    )
