"""
nbrose.cli
~~~~~~~~~~
Command-line interface for nbrose.

Usage
-----
    nbrose notebook.ipynb
    nbrose notebook.ipynb -o output.html
    nbrose notebook.ipynb -o output.html --title "My Report"
    nbrose --version
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .converter import convert


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="nbrose",
        description="Convert Jupyter notebooks to styled HTML with the Rosé Pine theme.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  nbrose analysis.ipynb
  nbrose analysis.ipynb -o report.html
  nbrose analysis.ipynb --title "Sales Analysis 2024"
        """,
    )

    parser.add_argument(
        "input",
        metavar="NOTEBOOK",
        help="path to the .ipynb file",
    )
    parser.add_argument(
        "-o", "--output",
        metavar="OUTPUT",
        default=None,
        help="output .html file path (default: same name as input)",
    )
    parser.add_argument(
        "--title",
        metavar="TITLE",
        default=None,
        help="custom page title (default: notebook filename)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"nbrose {__version__}",
    )

    args = parser.parse_args()

    try:
        out = convert(
            input_path=args.input,
            output_path=args.output,
            title=args.title,
        )
        print(f"✓ Converted → {out}")
    except FileNotFoundError as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
