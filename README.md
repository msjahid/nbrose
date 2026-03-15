# 🌸 nbrose

> Convert Jupyter notebooks to beautiful, self-contained HTML with the [Rosé Pine](https://rosepinetheme.com/) dark theme.

[![PyPI version](https://img.shields.io/pypi/v/nbrose?color=c4a7e7&labelColor=191724)](https://pypi.org/project/nbrose/)
[![Python](https://img.shields.io/pypi/pyversions/nbrose?color=9ccfd8&labelColor=191724)](https://pypi.org/project/nbrose/)
[![License: MIT](https://img.shields.io/badge/license-MIT-eb6f92?labelColor=191724)](LICENSE)

---

## ✨ Features

- 🎨 **Rosé Pine dark theme** — full color palette applied to every element
- 🖍️ **Python syntax highlighting** — keywords, builtins, strings, comments, decorators, all inline-styled
- 📖 **Auto-generated TOC** — sidebar with scroll-spy active state
- 👤 **Author footer** — reads a special `## Author` cell and renders SVG icon links
- 👁️ **Show / Hide code** — per-cell toggle and global "Code ▾" dropdown
- 📱 **Fully responsive** — mobile-friendly layout with slide-in TOC
- 🔒 **Self-contained HTML** — favicon embedded as base64, no external dependencies required for offline use
- ⚡ **Zero dependencies** — pure Python stdlib only

---

## 📦 Installation

```bash
pip install nbrose
```

---

## 🚀 Usage

### CLI

```bash
# Basic usage
nbrose notebook.ipynb

# Custom output path and title
nbrose notebook.ipynb -o report.html --title "My Analysis"
```

### Python API

```python
from nbrose import convert

# Simple conversion
convert("notebook.ipynb")

# Custom output and title
convert("notebook.ipynb", output_path="report.html", title="My Analysis")
```

---

## 👤 Author Cell

Add a special markdown cell anywhere in your notebook to generate a footer with social links:

```markdown
## Author
- **Name:** Jahid Hasan
- **Site:** https://msjahid.github.io
- **GitHub:** https://github.com/msjahid
- **LinkedIn:** https://linkedin.com/in/msjahid
- **Kaggle:** https://kaggle.com/msjahid
- **Twitter:** https://x.com/msjahids
- **Email:** msjahid.ai@gmail.com
```

The `## Author` cell is automatically hidden from the rendered output and displayed as a clean footer with SVG icon buttons.

---

## 🗂️ Project Structure

```
nbrose/
├── nbrose/
│   ├── __init__.py
│   ├── converter.py      ← core converter
│   ├── cli.py            ← command-line interface
│   └── favicon.png       ← embedded favicon
├── tests/
│   └── test_converter.py
├── pyproject.toml
├── README.md
└── LICENSE
```

---

## 🎨 Theme Colors

| Name    | Hex       | Usage                        |
|---------|-----------|------------------------------|
| Base    | `#191724` | Page background              |
| Surface | `#1f1d2e` | Code cell background         |
| Overlay | `#26233a` | Code header, inline code     |
| Iris    | `#c4a7e7` | Keywords, titles, links      |
| Foam    | `#9ccfd8` | Numbers, builtins            |
| Gold    | `#f6c177` | Strings, strong text         |
| Rose    | `#ebbcba` | Function calls               |
| Love    | `#eb6f92` | Errors, email icon           |
| Pine    | `#31748f` | Decorators, headings         |
| Muted   | `#6e6a86` | Comments, metadata           |

---

## 🛠️ Development

```bash
git clone https://github.com/msjahid/nbrose.git
cd nbrose
pip install -e .

# Run tests
python -m pytest tests/
```

---

## 📄 License

MIT © [Jahid Hasan](https://github.com/msjahid)

---

<p align="center">
  Maintained with ❤ by <a href="https://github.com/msjahid">CodeX</a>
</p>
