"""
nbrose
======
Convert Jupyter notebooks to beautiful HTML with the Rosé Pine dark theme.

Quick start
-----------
    # Python API
    from nbrose import convert
    convert("my_notebook.ipynb")           # → my_notebook.html
    convert("my_notebook.ipynb", "out.html")

    # CLI
    $ nbrose my_notebook.ipynb
    $ nbrose my_notebook.ipynb -o report.html --title "My Analysis"
"""

from .converter import convert

__all__ = ["convert"]
__version__ = "0.0.1"
__author__ = "Jahid Hasan"
__email__ = "msjahid.ai@gmail.com"
