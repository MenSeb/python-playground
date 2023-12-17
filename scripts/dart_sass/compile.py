"""Module Dart SASS."""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

from tools import logger

if TYPE_CHECKING:
    from pathlib import Path


def create_options_flags(
    options: dict[str, str | None],
) -> str:
    """Create CLI flags from the options keys and values.

    The format of a flag is --{option_key}={option_val}.

    For a flag without value, the format is --{option_key}.

    Parameters
    ----------
    options : dict[str, str]
       The options flags.

    Returns
    -------
    str
        The flags joined together.
    """
    flags = []

    for key, val in options.items():
        flag = f"--{key}"

        if val is not None and val != "":
            flag += f"={val}"

        flags.append(flag)

    return " ".join(flags)


def compile_dart_sass(
    path_in: str | Path,
    path_out: str | Path,
    options: dict[str, str | None] | None = None,
) -> None:
    """Compile SASS/SCSS files using Dart SASS.

    Dart SASS must be installed and found in the PATH environment.

    The script will call => sass {path_in} {path_out} {flags}

    Parameters
    ----------
    path_in : str | Path
        The input path to the SCSS/SASS file.
    path_out : str | Path
        The output path to the CSS file.
    options : dict[str, str]
        The options flags.
    """
    try:
        flags = "" if options is None else create_options_flags(options)

        if "watch" in options:
            logger.info_("Dart SASS watching files!")

        process = subprocess.run(
            f"sass {path_in}:{path_out} {flags}",
            check=False,
            capture_output=True,
            text=True,
            shell=True,  # noqa: S602
        )

        if process.stderr:
            logger.warn_("Dart SASS compile FAILURE!")
            logger.error_(process.stderr)
        else:
            logger.info_("Dart SASS compile SUCCESS!")
            logger.info_(f"From {path_in}")
            logger.info_(f"To {path_out}")
    except KeyboardInterrupt:
        logger.info_("Dart SASS interrupted correctly!")
    except Exception as err:  # noqa: BLE001
        logger.error_(err)
