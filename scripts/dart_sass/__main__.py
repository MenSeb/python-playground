"""Main Dart Sass."""

from pathlib import Path

from compile import compile_dart_sass

if __name__ == "__main__":
    path_in = Path().cwd() / "src/browser_stack/styles/index.scss"
    path_out = Path().cwd() / "src/browser_stack/static/styles/index.css"

    compile_dart_sass(
        path_in=path_in,
        path_out=path_out,
        options={
            "style": "compressed",
            "embed-source-map": None,
            "watch": None,
        },
    )
