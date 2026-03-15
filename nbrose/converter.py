"""
nbrose.converter
~~~~~~~~~~~~~~~~
Core .ipynb → styled HTML converter with Rosé Pine theme.
Uses inline style on highlight spans to guarantee colors render
regardless of CSS cascade or specificity issues.
"""

from __future__ import annotations

import json
import re
import html as html_module
from pathlib import Path
from typing import Optional


# ── Rosé Pine colors (used both in CSS vars and inline spans) ──────────────
RP = {
    "base":    "#191724",
    "surface": "#1f1d2e",
    "overlay": "#26233a",
    "muted":   "#6e6a86",
    "subtle":  "#908caa",
    "text":    "#e0def4",
    "love":    "#eb6f92",
    "gold":    "#f6c177",
    "rose":    "#ebbcba",
    "pine":    "#31748f",
    "foam":    "#9ccfd8",
    "iris":    "#c4a7e7",
    "hl_low":  "#21202e",
    "hl_med":  "#403d52",
    "hl_high": "#524f67",
}

ROSE_PINE_CSS = f"""
:root {{
  --base:    {RP['base']};
  --surface: {RP['surface']};
  --overlay: {RP['overlay']};
  --muted:   {RP['muted']};
  --subtle:  {RP['subtle']};
  --text:    {RP['text']};
  --love:    {RP['love']};
  --gold:    {RP['gold']};
  --rose:    {RP['rose']};
  --pine:    {RP['pine']};
  --foam:    {RP['foam']};
  --iris:    {RP['iris']};
  --hl-low:  {RP['hl_low']};
  --hl-med:  {RP['hl_med']};
  --hl-high: {RP['hl_high']};
}}

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

body {{
  font-family: "Source Code Pro", "Fira Code", monospace;
  background: var(--base);
  color: var(--text);
  line-height: 1.7;
  min-height: 100vh;
}}

html, body {{ margin: 0; padding: 0; }}

.nb-layout {{
  display: grid;
  grid-template-columns: 260px 1fr;
  align-items: start;
  min-height: 100vh;
}}

/* ── TOC ── */
#toc {{
  position: fixed;
  top: 0; left: 0;
  width: 260px;
  height: 100vh;
  background: var(--surface);
  border-right: 1px solid var(--hl-med);
  overflow-y: auto;
  padding: 24px 0;
  z-index: 100;
  transition: transform 0.3s;
}}
#toc h2 {{
  font-size: 0.7rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--muted);
  padding: 0 20px 12px;
  border-bottom: 1px solid var(--hl-med);
  margin-bottom: 12px;
}}
#toc ul {{ list-style: none; }}
#toc li a {{
  display: block;
  padding: 6px 20px;
  color: var(--subtle);
  text-decoration: none;
  font-size: 0.78rem;
  border-left: 2px solid transparent;
  transition: all 0.2s;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}}
#toc li a:hover, #toc li a.active {{
  color: var(--iris);
  border-left-color: var(--iris);
  background: var(--hl-low);
}}
#toc li.h3 a {{ padding-left: 36px; font-size: 0.73rem; }}
#toc li.h4 a {{ padding-left: 52px; font-size: 0.7rem; }}

/* ── Main ── */
#main {{
  grid-column: 2;
  width: 100%;
  max-width: 900px;
  justify-self: center;
  padding: 48px 40px 0;
}}

.nb-header {{
  margin-bottom: 48px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--hl-med);
}}
.nb-title {{
  font-size: 2rem;
  font-weight: 700;
  color: var(--iris);
  margin-bottom: 8px;
}}
.nb-meta {{
  font-size: 0.75rem;
  color: var(--muted);
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}}

/* ── Cells ── */
.cell {{ margin-bottom: 28px; }}

/* ── Markdown ── */
.cell-markdown {{ padding: 4px 0; }}
.cell-markdown h1, .cell-markdown h2,
.cell-markdown h3, .cell-markdown h4 {{
  color: var(--iris);
  margin: 1.6em 0 0.6em;
  font-weight: 700;
  scroll-margin-top: 24px;
}}
.cell-markdown h1 {{ font-size: 1.8rem; border-bottom: 2px solid var(--pine); padding-bottom: 8px; }}
.cell-markdown h2 {{ font-size: 1.4rem; border-bottom: 1px solid var(--hl-med); padding-bottom: 6px; }}
.cell-markdown h3 {{ font-size: 1.15rem; color: var(--foam); }}
.cell-markdown h4 {{ font-size: 1rem; color: var(--gold); }}
.cell-markdown p  {{ color: var(--subtle); margin-bottom: 0.9em; }}
.cell-markdown a  {{ color: var(--pine); text-decoration: underline; }}
.cell-markdown strong {{ color: var(--gold); font-weight: 700; }}
.cell-markdown em     {{ color: var(--rose); font-style: italic; }}
.cell-markdown ul, .cell-markdown ol {{
  margin: 0.6em 0 0.9em 1.6em;
  color: var(--subtle);
}}
.cell-markdown li {{ margin-bottom: 0.3em; }}
.cell-markdown blockquote {{
  border-left: 3px solid var(--pine);
  padding: 8px 16px;
  margin: 1em 0;
  background: var(--hl-low);
  border-radius: 0 6px 6px 0;
  color: var(--muted);
  font-style: italic;
}}
.cell-markdown code {{
  background: var(--overlay);
  color: var(--foam);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.88em;
}}
.cell-markdown pre {{
  background: var(--overlay);
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 1em 0;
  border: 1px solid var(--hl-med);
}}
.cell-markdown pre code {{ background: none; padding: 0; font-size: 0.85rem; }}
.cell-markdown table {{ width: 100%; border-collapse: collapse; margin: 1em 0; font-size: 0.85rem; }}
.cell-markdown th {{ background: var(--overlay); color: var(--iris); padding: 8px 12px; border: 1px solid var(--hl-med); }}
.cell-markdown td {{ padding: 7px 12px; border: 1px solid var(--hl-low); color: var(--subtle); }}
.cell-markdown tr:hover td {{ background: var(--hl-low); }}

/* ── Code cell ── */
.cell-code {{
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid var(--hl-med);
}}
.code-header {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 14px;
  background: var(--overlay);
  border-bottom: 1px solid var(--hl-med);
}}
.code-prompt {{ font-size: 0.68rem; color: var(--muted); letter-spacing: 0.06em; }}
.code-lang   {{ font-size: 0.65rem; color: var(--pine);  letter-spacing: 0.08em; text-transform: uppercase; }}
.code-source {{
  padding: 16px;
  overflow-x: auto;
  background: var(--surface);
}}
.code-source pre {{
  margin: 0;
  font-size: 0.84rem;
  line-height: 1.7;
  white-space: pre;
  color: var(--text);
}}

/* ── Outputs ── */
.cell-output {{
  background: var(--hl-low);
  border-top: 1px solid var(--hl-med);
  padding: 14px 16px;
  font-size: 0.83rem;
  color: var(--subtle);
  overflow-x: auto;
}}
.cell-output pre {{ margin: 0; white-space: pre-wrap; word-break: break-word; color: var(--subtle); }}
.output-error pre {{ color: var(--love) !important; }}
.output-image {{ padding: 16px; text-align: center; background: var(--hl-low); border-top: 1px solid var(--hl-med); }}
.output-image img {{ max-width: 100%; border-radius: 6px; }}
.output-html {{ padding: 14px 16px; background: var(--hl-low); border-top: 1px solid var(--hl-med); overflow-x: auto; font-size: 0.83rem; }}
.output-html table {{ border-collapse: collapse; font-size: 0.82rem; width: 100%; }}
.output-html th {{ background: var(--overlay); color: var(--iris); padding: 6px 10px; border: 1px solid var(--hl-med); }}
.output-html td {{ padding: 5px 10px; border: 1px solid var(--hl-low); color: var(--subtle); }}
.output-html tr:hover td {{ background: var(--hl-low); }}


/* ── Author footer ── */
.nb-footer {{
  margin-top: 28px;
  border-top: 1px solid var(--hl-med);
  padding: 10px 0 0;
}}

.nb-footer-inner {{
  padding: 8px 0 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}}

.nb-footer-credit {{
  font-size: 0.68rem;
  color: var(--muted);
  text-align: right;
}}

.nb-footer-author {{
  display: flex;
  flex-direction: column;
  gap: 4px;
}}

.nb-footer-name {{
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text);
}}

.nb-footer-tagline {{
  font-size: 0.75rem;
  color: var(--muted);
}}

.nb-footer-links {{
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}}

/* ── CHANGED: icon-only square buttons ── */
.nb-footer-link {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  text-decoration: none;
  border: 1px solid var(--hl-med);
  color: var(--subtle);
  background: var(--overlay);
  transition: all 0.2s;
}}

.nb-footer-link svg {{
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}}

.nb-footer-link:hover {{
  border-color: var(--iris);
  color: var(--iris);
  background: var(--hl-low);
  transform: translateY(-2px);
}}

.nb-footer-link.site   {{ border-color: var(--pine);  color: var(--foam); }}
.nb-footer-link.github {{ border-color: var(--muted); }}
.nb-footer-link.li     {{ border-color: var(--pine);  }}
.nb-footer-link.kaggle {{ border-color: var(--gold);  color: var(--gold); }}
.nb-footer-link.twitter{{ border-color: var(--foam);  color: var(--foam); }}
.nb-footer-link.email  {{ border-color: var(--love);  color: var(--love); }}

.nb-footer-link:hover {{ color: var(--iris) !important; border-color: var(--iris) !important; }}




.nb-footer-credit a {{
  color: var(--iris);
  text-decoration: none;
  font-weight: 600;
}}

.nb-footer-credit a:hover {{ color: var(--foam); }}

.nb-heart {{ color: var(--love); }}

.nb-footer-card-wrap {{
  display: flex;
  flex-direction: column;
  align-items: stretch;
  width: fit-content;
  max-width: 100%;
}}

/* ── Code toggle ── */
.code-toggle-btn {{
  background: none;
  border: 1px solid var(--hl-med);
  color: var(--muted);
  font-size: 0.65rem;
  font-family: inherit;
  padding: 2px 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  letter-spacing: 0.05em;
}}
.code-toggle-btn:hover {{
  border-color: var(--iris);
  color: var(--iris);
}}
.nb-global-toggle {{
  display: flex;
  align-items: center;
  gap: 6px;
  position: relative;
}}
.nb-global-toggle-btn {{
  background: none;
  border: 1px solid var(--iris);
  color: var(--iris);
  font-size: 0.72rem;
  font-family: inherit;
  padding: 4px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  letter-spacing: 0.05em;
}}
.nb-global-toggle-btn:hover {{
  background: var(--iris);
  color: var(--base);
}}
.nb-global-menu {{
  display: none;
  position: absolute;
  top: 110%;
  right: 0;
  background: var(--overlay);
  border: 1px solid var(--hl-med);
  border-radius: 8px;
  min-width: 140px;
  z-index: 50;
  overflow: hidden;
}}
.nb-global-menu.open {{ display: block; }}
.nb-global-menu button {{
  display: block;
  width: 100%;
  background: none;
  border: none;
  color: var(--subtle);
  font-family: inherit;
  font-size: 0.78rem;
  padding: 10px 16px;
  text-align: left;
  cursor: pointer;
  transition: background 0.15s;
}}
.nb-global-menu button:hover {{
  background: var(--hl-med);
  color: var(--text);
}}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: var(--surface); }}
::-webkit-scrollbar-thumb {{ background: var(--hl-high); border-radius: 3px; }}

/* ── Responsive ── */
@media (max-width: 768px) {{
  .nb-layout {{ grid-template-columns: 1fr; }}
  #toc {{ transform: translateX(-260px); position: fixed; }}
  #toc.open {{ transform: translateX(0); }}
  #main {{ grid-column: 1; padding: 64px 16px 40px; max-width: 100%; overflow-x: hidden; }}
  .nb-footer-credit {{
    position: static;
    display: block;
    text-align: center;
    padding-top: 10px;
    font-size: 0.68rem;
  }}
  .nb-footer {{ width: 100%; overflow: hidden; }}
  .nb-footer-inner {{ padding: 12px 0; gap: 10px; flex-direction: column; align-items: center; width: 100%; max-width: 100%; }}
  .nb-footer-author {{ width: 100%; text-align: center; }}
  .nb-footer-links {{ flex-wrap: wrap; justify-content: center; gap: 8px; width: 100%; }}
  .nb-footer-link {{ width: 36px; height: 36px; padding: 0; justify-content: center; }}
  .nb-footer-link svg {{ width: 17px; height: 17px; }}
  .nb-footer-name {{ font-size: 0.95rem; text-align: center; }}
  .cell-code {{ overflow: hidden; }}
  .code-source {{ overflow-x: scroll; -webkit-overflow-scrolling: touch; }}
  .code-source pre {{ white-space: pre; font-size: 0.72rem; min-width: max-content; }}
  .cell-output {{ overflow-x: scroll; -webkit-overflow-scrolling: touch; }}
  .cell-output pre {{ font-size: 0.72rem; white-space: pre; min-width: max-content; }}
  .cell-markdown p, .cell-markdown li {{ font-size: 0.85rem; word-break: break-word; overflow-wrap: break-word; }}
  .nb-title {{ font-size: 1.3rem; word-break: break-word; }}
  .nb-meta {{ flex-direction: column; gap: 4px; font-size: 0.68rem; }}
  .nb-header {{ margin-bottom: 24px; }}
  #toc-toggle {{
    display: flex !important;
    position: fixed;
    top: 12px; left: 12px;
    width: 38px; height: 38px;
    background: var(--iris);
    color: var(--base);
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    cursor: pointer;
    align-items: center;
    justify-content: center;
    z-index: 200;
    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
  }}
}}
#toc-toggle {{ display: none; }}
"""


# ── Inline color map for highlight spans ─────────────────────────────────
# Using inline style= guarantees color regardless of CSS cascade
SPAN = {
    "kw": f'style="color:{RP["iris"]};font-weight:600"',   # keyword   → iris
    "bi": f'style="color:{RP["love"]}"',                   # builtin   → love
    "st": f'style="color:{RP["gold"]}"',                   # string    → gold
    "cm": f'style="color:{RP["muted"]};font-style:italic"',# comment   → muted
    "nm": f'style="color:{RP["foam"]}"',                   # number    → foam
    "fn": f'style="color:{RP["rose"]}"',                   # function  → rose
    "op": f'style="color:{RP["subtle"]}"',                 # operator  → subtle
    "dc": f'style="color:{RP["pine"]}"',                   # decorator → pine
    "cl": f'style="color:{RP["foam"]}"',                   # class     → foam
}


# ── Python keyword / builtin sets ─────────────────────────────────────────
KEYWORDS = frozenset({
    "False","None","True","and","as","assert","async","await",
    "break","class","continue","def","del","elif","else","except",
    "finally","for","from","global","if","import","in","is",
    "lambda","nonlocal","not","or","pass","raise","return","try",
    "while","with","yield",
})

BUILTINS = frozenset({
    "abs","all","any","bin","bool","bytes","callable","chr",
    "dict","dir","divmod","enumerate","eval","exec","filter",
    "float","format","frozenset","getattr","globals","hasattr",
    "hash","help","hex","id","input","int","isinstance",
    "issubclass","iter","len","list","locals","map","max",
    "min","next","object","oct","open","ord","pow","print",
    "property","range","repr","reversed","round","set","setattr",
    "slice","sorted","staticmethod","str","sum","super","tuple",
    "type","vars","zip",
})


# ── Tokeniser ─────────────────────────────────────────────────────────────
def _tokenise(code: str):
    """Yield (token_type, raw_text) from raw Python source."""
    i, n = 0, len(code)
    while i < n:
        # comment
        if code[i] == "#":
            end = code.find("\n", i)
            end = end if end != -1 else n
            yield ("cm", code[i:end]); i = end; continue
        # triple-quoted string
        for q in ('"""', "'''"):
            if code[i:i+3] == q:
                end = code.find(q, i+3)
                end = (end + 3) if end != -1 else n
                yield ("st", code[i:end]); i = end; break
        else:
            # single/double quoted string with optional prefix
            m = re.match(r'[fFbBrRuU]{0,2}(["\'])(?:(?!\1)(?:\\.|[^\\]))*\1', code[i:])
            if m:
                yield ("st", m.group(0)); i += m.end(); continue
            # decorator
            if code[i] == "@":
                m2 = re.match(r'@[\w.]+', code[i:])
                if m2:
                    yield ("dc", m2.group(0)); i += m2.end(); continue
            # number
            m3 = re.match(r'0[xXoObB][\da-fA-F_]+|\d+\.?\d*(?:[eE][+-]?\d+)?[jJ]?', code[i:])
            if m3:
                yield ("nm", m3.group(0)); i += m3.end(); continue
            # identifier
            m4 = re.match(r'[A-Za-z_]\w*', code[i:])
            if m4:
                yield ("id", m4.group(0)); i += m4.end(); continue
            # anything else
            yield (None, code[i]); i += 1


def highlight_python(code: str) -> str:
    """Tokenise raw Python source → HTML with inline-styled spans."""
    tokens = list(_tokenise(code))
    parts = []
    for idx, (ttype, text) in enumerate(tokens):
        esc = html_module.escape(text)
        if ttype is None:
            parts.append(esc)
        elif ttype == "id":
            if text in KEYWORDS:
                parts.append(f'<span {SPAN["kw"]}>{esc}</span>')
            elif text in BUILTINS:
                parts.append(f'<span {SPAN["bi"]}>{esc}</span>')
            else:
                # peek ahead for '(' → function call
                j = idx + 1
                while j < len(tokens) and tokens[j][0] is None and tokens[j][1] in " \t":
                    j += 1
                if j < len(tokens) and tokens[j][1] == "(":
                    parts.append(f'<span {SPAN["fn"]}>{esc}</span>')
                else:
                    parts.append(esc)
        else:
            parts.append(f'<span {SPAN[ttype]}>{esc}</span>')
    return "".join(parts)


# ── Markdown → HTML ────────────────────────────────────────────────────────
def markdown_to_html(text: str) -> str:
    lines = text.split("\n")
    out, in_ul, in_ol, in_code = [], False, False, False
    code_buf, code_lang = [], ""

    def close_list():
        nonlocal in_ul, in_ol
        if in_ul: out.append("</ul>"); in_ul = False
        if in_ol: out.append("</ol>"); in_ol = False

    def inline(s: str) -> str:
        s = html_module.escape(s)
        s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
        s = re.sub(r'\*(.+?)\*',     r'<em>\1</em>', s)
        s = re.sub(r'`([^`]+)`',     r'<code>\1</code>', s)
        s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', s)
        return s

    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            if not in_code:
                close_list(); in_code = True
                code_lang = line[3:].strip() or "python"; code_buf = []
            else:
                in_code = False
                raw = "\n".join(code_buf)
                body = highlight_python(raw) if "python" in code_lang.lower() or code_lang == "" else html_module.escape(raw)
                out.append(f'<pre><code>{body}</code></pre>')
                code_buf = []
            i += 1; continue
        if in_code: code_buf.append(line); i += 1; continue
        m = re.match(r'^(#{1,6})\s+(.*)', line)
        if m:
            close_list(); level = len(m.group(1))
            content = inline(m.group(2))
            slug = re.sub(r'[^a-z0-9-]', '', m.group(2).lower().replace(' ', '-'))
            out.append(f'<h{level} id="{slug}">{content}</h{level}>'); i += 1; continue
        if line.startswith("> "):
            close_list(); out.append(f'<blockquote><p>{inline(line[2:])}</p></blockquote>'); i += 1; continue
        if re.match(r'^[-*+]\s', line):
            if not in_ul: close_list(); out.append("<ul>"); in_ul = True
            out.append(f'<li>{inline(line[2:].strip())}</li>'); i += 1; continue
        if re.match(r'^\d+\.\s', line):
            if not in_ol: close_list(); out.append("<ol>"); in_ol = True
            out.append(f'<li>{inline(re.sub(r"^\d+\.\s","",line).strip())}</li>'); i += 1; continue
        if re.match(r'^[-*_]{3,}$', line.strip()):
            close_list(); out.append("<hr>"); i += 1; continue
        if not line.strip(): close_list(); out.append(""); i += 1; continue
        close_list(); out.append(f'<p>{inline(line)}</p>'); i += 1

    close_list()
    return "\n".join(out)


# ── Output renderers ──────────────────────────────────────────────────────
def render_output(output: dict) -> str:
    otype = output.get("output_type", "")
    if otype == "stream":
        text = html_module.escape("".join(output.get("text", [])))
        cls = "output-error" if output.get("name") == "stderr" else ""
        return f'<div class="cell-output {cls}"><pre>{text}</pre></div>'
    if otype in ("execute_result", "display_data"):
        data = output.get("data", {})
        for mime in ("image/png", "image/jpeg", "image/svg+xml"):
            if mime in data:
                img = "".join(data[mime]) if isinstance(data[mime], list) else data[mime]
                if mime == "image/svg+xml":
                    return f'<div class="output-image">{img}</div>'
                return f'<div class="output-image"><img src="data:{mime};base64,{img}" alt="output"/></div>'
        if "text/html" in data:
            return f'<div class="output-html">{"".join(data["text/html"])}</div>'
        if "text/plain" in data:
            return f'<div class="cell-output"><pre>{html_module.escape("".join(data["text/plain"]))}</pre></div>'
    if otype == "error":
        tb = re.sub(r'\x1b\[[0-9;]*m', '', "\n".join(output.get("traceback", [])))
        return f'<div class="cell-output output-error"><pre>{html_module.escape(tb)}</pre></div>'
    return ""


def render_markdown_cell(cell: dict) -> str:
    source = "".join(cell.get("source", []))
    return f'<div class="cell cell-markdown">{markdown_to_html(source)}</div>\n'


def render_code_cell(cell: dict, index: int, kernel: str) -> str:
    source = "".join(cell.get("source", []))
    exec_count = cell.get("execution_count") or " "
    body = highlight_python(source) if "python" in kernel.lower() else html_module.escape(source)
    parts = [
        '<div class="cell cell-code">',
        '  <div class="code-header">',
        f'    <span class="code-prompt">In [{exec_count}]</span>',
        f'    <span style="display:flex;align-items:center;gap:8px;"><span class="code-lang">{html_module.escape(kernel)}</span><button class="code-toggle-btn" onclick="toggleCode(this)">Hide</button></span>',
        '  </div>',
        f'  <div class="code-source"><pre>{body}</pre></div>',
    ]
    for out in cell.get("outputs", []):
        parts.append(render_output(out))
    parts.append("</div>")
    return "\n".join(parts) + "\n"



# ── Author info parser ────────────────────────────────────────────────────
# Reads a special markdown cell that looks like:
#
#   ## Author
#   - **Name:** Jahid Hasan
#   - **Site:** https://msjahid.github.io
#   - **GitHub:** https://github.com/msjahid
#   - **LinkedIn:** https://linkedin.com/in/msjahid
#   - **Kaggle:** https://kaggle.com/msjahid
#   - **Twitter:** https://x.com/msjahids
#   - **Email:** msjahid.ai@gmail.com

AUTHOR_KEYS = {
    "name":     ("name",    "name"),
    "site":     ("site",    "🌐"),
    "website":  ("site",    "🌐"),
    "github":   ("github",  "GitHub"),
    "linkedin": ("li",      "LinkedIn"),
    "kaggle":   ("kaggle",  "Kaggle"),
    "twitter":  ("twitter", "Twitter / X"),
    "x":        ("twitter", "Twitter / X"),
    "email":    ("email",   "✉ Email"),
}

LINK_ICONS = {
    "site":    "🌐",
    "github":  "⚙",
    "li":      "in",
    "kaggle":  "K",
    "twitter": "𝕏",
    "email":   "✉",
}


def parse_author_cell(cells: list) -> dict:
    """
    Find a markdown cell containing ## Author and extract key-value pairs.
    Returns a dict like:
      {'name': 'Jahid Hasan', 'site': 'https://...', 'github': 'https://...', ...}
    Returns empty dict if no author cell found.
    """
    for cell in cells:
        if cell.get("cell_type") != "markdown":
            continue
        source = "".join(cell.get("source", []))
        # Must contain a heading with "author" (case-insensitive)
        if not re.search(r"#{1,4}\s+author", source, re.IGNORECASE):
            continue
        info = {}
        for line in source.split("\n"):
            line = line.strip()
            line = re.sub(r'^[-*]\s+', '', line)
            m = re.match(r'\*{0,2}([\w /]+?)\*{0,2}:\s*\*{0,2}\s*(.+?)\s*\*{0,2}$', line)
            if m:
                key   = m.group(1).strip().lower()
                value = m.group(2).strip()
                if key in AUTHOR_KEYS:
                    info[AUTHOR_KEYS[key][0]] = value
        if info:
            return info
    return {}


def build_footer(author: dict) -> str:
    """Build the HTML footer from parsed author info."""
    if not author:
        return ""

    name     = author.get("name", "")
    tagline  = ""

    links_html = ""

    # ── CHANGED: SVG icons, no text labels ──
    SVG = {
        "site":    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>',
        "github":  '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0 1 12 6.844a9.59 9.59 0 0 1 2.504.337c1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.02 10.02 0 0 0 22 12.017C22 6.484 17.522 2 12 2z"/></svg>',
        "li":      '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>',
        "kaggle":  '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M18.825 23.859c-.022.092-.117.141-.281.141h-3.139c-.187 0-.351-.082-.492-.248l-5.178-6.589-1.448 1.374v5.111c0 .235-.117.352-.351.352H5.505c-.236 0-.354-.117-.354-.352V.353c0-.233.118-.353.354-.353h2.431c.234 0 .351.12.351.353v14.343l6.203-6.272c.165-.165.33-.246.495-.246h3.239c.144 0 .236.06.285.18.046.149.034.255-.036.315l-6.555 6.344 6.836 8.507c.095.104.117.208.07.334"/></svg>',
        "twitter": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>',
        "email":   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>',
    }
    link_order = ["site", "github", "li", "kaggle", "twitter", "email"]

    for key in link_order:
        if key not in author:
            continue
        href = author[key]
        if key == "email" and not href.startswith("mailto:"):
            href = f"mailto:{href}"
        links_html += (
            f'<a href="{href}" target="_blank" class="nb-footer-link {key}" title="{key}">'
            f'{SVG[key]}</a>'
        )

    if not name and not links_html:
        return ""

    tagline_html = f'<div class="nb-footer-tagline">{tagline}</div>' if tagline else ''
    return f"""
<div class="nb-footer">
  <div class="nb-footer-inner">
    <div class="nb-footer-author">
      <div class="nb-footer-name">{html_module.escape(name)}</div>
      {tagline_html}
    </div>
    <div class="nb-footer-links">
      {links_html}
    </div>
  </div>
</div>
"""


# ── TOC ────────────────────────────────────────────────────────────────────
def build_toc(cells: list) -> str:
    items = []
    for cell in cells:
        if cell.get("cell_type") != "markdown":
            continue
        for line in "".join(cell.get("source", [])).split("\n"):
            m = re.match(r'^(#{1,4})\s+(.*)', line)
            if m:
                level = len(m.group(1))
                title = re.sub(r'[*_`]', '', m.group(2)).strip()
                slug  = re.sub(r'[^a-z0-9-]', '', title.lower().replace(' ', '-'))
                css   = f"h{level}" if level > 1 else ""
                items.append(f'<li class="{css}"><a href="#{slug}">{html_module.escape(title)}</a></li>')
    if not items:
        return ""
    return '<nav id="toc"><h2>Contents</h2><ul>' + "\n".join(items) + "</ul></nav>"


# ── HTML template ──────────────────────────────────────────────────────────
HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>__TITLE__</title>
<link rel="icon" type="image/png" href="../favicon.png"/>
<link href="https://fonts.googleapis.com/css2?family=Source+Code+Pro:wght@300;400;500;600;700&display=swap" rel="stylesheet"/>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"/>
<style>
__CSS__
</style>
</head>
<body>
<div class="nb-layout">
__TOC__
<div id="main">
  <div class="nb-header">
    <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:16px;">
      <div>
        <div class="nb-title">__TITLE__</div>
        <div class="nb-meta">
          <span>&#x1F40D; __KERNEL__</span>
          <span>&#x1F4D3; __CELL_COUNT__ cells</span>
          <span>&#x1F4BB; __CODE_COUNT__ code &middot; &#x1F4DD; __MD_COUNT__ markdown</span>
        </div>
      </div>
      <div class="nb-global-toggle">
        <button class="nb-global-toggle-btn" onclick="toggleGlobalMenu()">Code &#9660;</button>
        <div class="nb-global-menu" id="globalMenu">
          <button onclick="showAllCode()">Show All Code</button>
          <button onclick="hideAllCode()">Hide All Code</button>
        </div>
      </div>
    </div>
  </div>
__CELLS__
__FOOTER__
</div>
</div>
<button id="toc-toggle" onclick="document.getElementById('toc').classList.toggle('open')">&#9776;</button>
<div class="nb-footer-credit">
  Maintained with <span class="nb-heart">&#10084;</span> by
  <a href="https://github.com/msjahid/nbrose" target="_blank">𝓂𝓈𝒿𝒶𝒽𝒾𝒹</a>
</div>
<script>
const headings = document.querySelectorAll('h1[id],h2[id],h3[id],h4[id]');
const tocLinks = document.querySelectorAll('#toc a');
const observer = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      tocLinks.forEach(a => a.classList.remove('active'));
      const a = document.querySelector('#toc a[href="#' + e.target.id + '"]');
      if (a) a.classList.add('active');
    }
  });
}, { rootMargin: '-10% 0px -80% 0px' });
headings.forEach(h => observer.observe(h));

function toggleGlobalMenu() {
  document.getElementById('globalMenu').classList.toggle('open');
}
document.addEventListener('click', function(e) {
  if (!e.target.closest('.nb-global-toggle')) {
    document.getElementById('globalMenu').classList.remove('open');
  }
});
function showAllCode() {
  document.querySelectorAll('.code-source').forEach(el => el.style.display = '');
  document.querySelectorAll('.code-toggle-btn').forEach(btn => btn.textContent = 'Hide');
  document.getElementById('globalMenu').classList.remove('open');
}
function hideAllCode() {
  document.querySelectorAll('.code-source').forEach(el => el.style.display = 'none');
  document.querySelectorAll('.code-toggle-btn').forEach(btn => btn.textContent = 'Show');
  document.getElementById('globalMenu').classList.remove('open');
}
function toggleCode(btn) {
  const src = btn.closest('.cell-code').querySelector('.code-source');
  if (src.style.display === 'none') {
    src.style.display = '';
    btn.textContent = 'Hide';
  } else {
    src.style.display = 'none';
    btn.textContent = 'Show';
  }
}
</script>
</body>
</html>
"""


# ── Public API ─────────────────────────────────────────────────────────────
def convert(
    input_path: "str | Path",
    output_path: "Optional[str | Path]" = None,
    title: "Optional[str]" = None,
) -> Path:
    """
    Convert a Jupyter notebook (.ipynb) to a styled HTML file.

    Parameters
    ----------
    input_path  : path to the .ipynb file
    output_path : destination .html path (default: same dir, same stem)
    title       : custom page title (default: notebook filename stem)

    Returns
    -------
    Path to the generated HTML file.

    Example
    -------
    >>> from nbrose import convert
    >>> convert("analysis.ipynb")
    PosixPath('analysis.html')
    """
    input_path = Path(input_path)
    if input_path.suffix.lower() != ".ipynb":
        raise ValueError(f"Expected a .ipynb file, got: {input_path}")
    if not input_path.exists():
        raise FileNotFoundError(f"Notebook not found: {input_path}")

    if output_path is None:
        output_path = input_path.with_suffix(".html")
    output_path = Path(output_path)

    nb         = json.loads(input_path.read_text(encoding="utf-8"))
    kernel     = nb.get("metadata", {}).get("kernelspec", {}).get("display_name", "Python 3")
    cells      = nb.get("cells", [])
    page_title = title or input_path.stem.replace("-", " ").replace("_", " ").title()

    cell_count = len(cells)
    code_count = sum(1 for c in cells if c.get("cell_type") == "code")
    md_count   = sum(1 for c in cells if c.get("cell_type") == "markdown")

    toc_html   = build_toc(cells)
    author     = parse_author_cell(cells)
    footer_html= build_footer(author)
    def _render_cell(i, c):
        ctype = c.get("cell_type", "")
        if ctype == "markdown":
            src = "".join(c.get("source", []))
            if re.search(r"#{1,4}\s+[Aa]uthor", src):
                return ""   # hide author cell — shown as footer
            return render_markdown_cell(c)
        if ctype == "code":
            return render_code_cell(c, i, kernel)
        return ""

    cells_html = "".join(_render_cell(i, c) for i, c in enumerate(cells))

    html = (HTML_TEMPLATE
        .replace("__TITLE__",      html_module.escape(page_title))
        .replace("__KERNEL__",     html_module.escape(kernel))
        .replace("__CELL_COUNT__", str(cell_count))
        .replace("__CODE_COUNT__", str(code_count))
        .replace("__MD_COUNT__",   str(md_count))
        .replace("__CSS__",        ROSE_PINE_CSS)
        .replace("__TOC__",        toc_html)
        .replace("__CELLS__",      cells_html)
        .replace("__FOOTER__",     footer_html)
    )

    output_path.write_text(html, encoding="utf-8")
    return output_path