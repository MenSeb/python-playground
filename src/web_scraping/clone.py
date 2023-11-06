"""Module Clone."""

from __future__ import annotations

import re
from pathlib import Path
from types import SimpleNamespace
from typing import TYPE_CHECKING

from bs4 import BeautifulSoup, ResultSet, Tag
from utilities import logger

if TYPE_CHECKING:
    from .session import Session


class ClonePaths(SimpleNamespace):
    """Interface representing clone directory paths."""

    def __init__(
        self: ClonePaths,
        directory: str | Path,
        folder: str,
        filename: str,
    ) -> None:
        directory = Path(directory)
        path = directory / folder

        self.directory = directory
        self.folder = folder
        self.filename = filename
        self.fonts = path / "fonts"
        self.images = path / "images"
        self.pages = path / "pages"
        self.scripts = path / "scripts"
        self.styles = path / "styles"

        if not path.exists():
            path.mkdir(parents=True)
            self.fonts.mkdir()
            self.images.mkdir()
            self.pages.mkdir()
            self.scripts.mkdir()
            self.styles.mkdir()


class Clone:
    """Interface representing clone utilities."""

    def __init__(
        self: Clone,
        directory: str | Path,
        filename: str | Path,
        markup: str | bytes,
        url: str,
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
        logger.trace_(msg=url)

        domain = url[url.find("//") + 2 : -1]

        self.paths = ClonePaths(
            directory=directory,
            filename=filename,
            folder=domain,
        )
        self.url = url
        self.soup = BeautifulSoup(markup=markup, features="html5lib")
        self.source_attributes = ["src", "href", "data-cfsrc"]

    def save_html(
        self: Clone,
    ) -> int:
        """Save the HTML clone."""
        logger.trace_(msg=self.paths.filename)

        return (self.paths.pages / self.paths.filename).write_text(
            data=self.soup.prettify(),
            encoding="utf-8",
        )

    def save_asset(
        self: Clone,
        data: bytes,
        path: Path,
    ) -> None:
        """Save an asset file.

        Args:
        ----
            data (bytes):
                The asset data.
            path (Path):
                The asset path.
        """
        logger.trace_(msg=f"ASSET {path}")

        path.write_bytes(data=data)

    def create_path_asset(
        self: Clone,
        source: str,
        folder: Path,
    ) -> Path:
        """Create a path to an asset.

        Args:
        ----
            source (str): The asset source.
            folder (Path): The asset folder.

        Returns
        -------
            Path: The asset path.
        """
        path = Path(source)
        index = path.suffix.find("?")
        filename = path.name if index < 0 else path.stem + path.suffix[0:index]
        return folder / filename

    def create_path_source(
        self: Clone,
        filename: str,
        folder: Path,
    ) -> str:
        """Create a path to a ressource.

        Args:
        ----
            filename (str): The ressource filename.
            folder (Path): The ressource folder.

        Returns
        -------
            str: The ressource path.
        """
        return Path("..", folder.name, filename).as_posix()

    def find_source_attribute(
        self: Clone,
        tag: Tag,
    ) -> str | None:
        """Find the HTML element source attribute.

        Args:
        ----
            tag (Tag): The HTML element.

        Returns
        -------
            str | None: The source attribute.
        """
        for source_attribute in self.source_attributes:
            if source_attribute in tag.attrs:
                return source_attribute

        return None

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
            attribute = self.find_source_attribute(tag=image)

            if attribute is None or image[attribute].startswith("https"):
                continue

            source = image.get(key=attribute)
            path = self.create_path_asset(source=source, folder=self.paths.images)
            image["src"] = self.create_path_source(
                filename=path.name,
                folder=self.paths.images,
            )

            if path.exists():
                continue

            response = session.request(url=self.url + source)

            if response is not None:
                self.save_asset(data=response.content, path=path)

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
            attribute = self.find_source_attribute(tag=link)

            if attribute is None or link[attribute].startswith("https"):
                continue

            source = link.get(key=attribute)

            if source.startswith("https"):
                continue

            if source.startswith("//"):
                link["href"] = "https:" + source
                continue

            folder = (
                self.paths.styles
                if link.get(key="rel")[0] == "stylesheet"
                else self.paths.images
            )
            path = self.create_path_asset(source=source, folder=folder)
            link["href"] = self.create_path_source(filename=path.name, folder=folder)

            if path.exists():
                continue

            response = session.request(url=self.url + source)

            if response is not None:
                self.save_asset(data=response.content, path=path)

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
            attribute = self.find_source_attribute(tag=script)

            if nosync or attribute is None or script[attribute].startswith("https"):
                script.extract()
                continue

            source = script.get(key=attribute)
            path = self.create_path_asset(source=source, folder=self.paths.scripts)
            script["src"] = self.create_path_source(
                filename=path.name,
                folder=self.paths.scripts,
            )

            if path.exists():
                continue

            response = session.request(url=self.url + source)

            if response is not None:
                self.save_asset(data=response.content, path=path)

    def sync_fonts(
        self: Clone,
        session: Session,
    ) -> None:
        """Sync the fonts from the cloned website.

        Args:
            session (Session):
                The requests session.
        """
        for path_stylesheet in list(self.paths.styles.iterdir()):
            stylesheet = path_stylesheet.read_text()
            urls: list[str] = re.findall(pattern=r"url\(([^)]+)\)", string=stylesheet)
            fonts = filter(lambda url: url.find("woff") > -1, urls)

            for font in fonts:
                source = font.replace('"', "")
                path = self.create_path_asset(source=source, folder=self.paths.fonts)

                if path.exists():
                    continue

                response = session.request(url=self.url + source)

                if response is not None:
                    self.save_asset(
                        data=response.content,
                        path=path,
                    )
                    stylesheet = stylesheet.replace(
                        source,
                        self.create_path_source(
                            file=path.name,
                            folder=self.paths.fonts,
                        ),
                    )

            path_stylesheet.write_text(data=stylesheet)
