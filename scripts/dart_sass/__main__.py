"""Main Dart Sass."""

from pathlib import Path

from compile import compile_dart_sass

if __name__ == "__main__":
    path_in = Path().cwd() / "src/test.scss"
    path_out = Path().cwd() / "src/test.css"

    compile_dart_sass(
        path_in=path_in,
        path_out=path_out,
        options={
            "style": "compressed",
            "embed-source-map": None,
            "watch": None,
        },
    )
