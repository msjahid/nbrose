"""tests/test_converter.py"""
import json, tempfile
from pathlib import Path
import pytest
from nbrose import convert
from nbrose.converter import highlight_python, markdown_to_html, build_toc

def make_nb(cells):
    return {"nbformat":4,"nbformat_minor":5,
            "metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"}},
            "cells":cells}

def write_nb(nb, path): path.write_text(json.dumps(nb), encoding="utf-8")

# ── highlight_python ──────────────────────────────────────────────────────
def test_highlight_keyword():
    result = highlight_python("def foo():")
    assert 'color:#c4a7e7' in result   # iris = keyword color

def test_highlight_string():
    result = highlight_python('"hello"')
    assert 'color:#f6c177' in result   # gold = string color

def test_highlight_comment():
    result = highlight_python("# a comment")
    assert 'color:#6e6a86' in result   # muted = comment color

def test_highlight_builtin():
    result = highlight_python("print(x)")
    assert 'color:#eb6f92' in result   # love = builtin color

def test_highlight_number():
    result = highlight_python("x = 42")
    assert 'color:#9ccfd8' in result   # foam = number color

def test_highlight_function_call():
    result = highlight_python("df.head()")
    assert 'color:#ebbcba' in result   # rose = function color

# ── markdown_to_html ──────────────────────────────────────────────────────
def test_markdown_heading():
    html = markdown_to_html("# Hello World")
    assert "<h1" in html and "Hello World" in html

def test_markdown_bold():
    html = markdown_to_html("**bold text**")
    assert "<strong>bold text</strong>" in html

def test_markdown_code_inline():
    html = markdown_to_html("`code`")
    assert "<code>code</code>" in html

def test_markdown_list():
    html = markdown_to_html("- item one\n- item two")
    assert "<ul>" in html and "<li>" in html

# ── build_toc ─────────────────────────────────────────────────────────────
def test_toc_built_from_headings():
    cells = [
        {"cell_type":"markdown","source":["# Introduction"]},
        {"cell_type":"markdown","source":["## Methods"]},
    ]
    toc = build_toc(cells)
    assert "Introduction" in toc and "Methods" in toc

def test_toc_empty_when_no_headings():
    cells = [{"cell_type":"code","source":["x=1"],"outputs":[],"execution_count":1}]
    assert build_toc(cells) == ""

# ── convert ───────────────────────────────────────────────────────────────
def test_convert_basic():
    nb = make_nb([
        {"cell_type":"markdown","source":["# Test\n\nHello."]},
        {"cell_type":"code","source":["print('hi')"],"execution_count":1,
         "outputs":[{"output_type":"stream","name":"stdout","text":["hi\n"]}]},
    ])
    with tempfile.TemporaryDirectory() as tmp:
        nb_path = Path(tmp)/"test.ipynb"; out = Path(tmp)/"test.html"
        write_nb(nb, nb_path)
        result = convert(nb_path, out)
        assert result == out and out.exists()
        content = out.read_text()
        assert "Test" in content and "#191724" in content

def test_convert_default_output_path():
    nb = make_nb([{"cell_type":"markdown","source":["# Hello"]}])
    with tempfile.TemporaryDirectory() as tmp:
        nb_path = Path(tmp)/"mynotebook.ipynb"; write_nb(nb, nb_path)
        result = convert(nb_path)
        assert result == nb_path.with_suffix(".html") and result.exists()

def test_convert_custom_title():
    nb = make_nb([])
    with tempfile.TemporaryDirectory() as tmp:
        nb_path = Path(tmp)/"test.ipynb"; write_nb(nb, nb_path)
        content = convert(nb_path, title="Custom Title").read_text()
        assert "Custom Title" in content

def test_convert_file_not_found():
    with pytest.raises(FileNotFoundError): convert("nonexistent.ipynb")

def test_convert_wrong_extension():
    with pytest.raises(ValueError): convert("notebook.txt")