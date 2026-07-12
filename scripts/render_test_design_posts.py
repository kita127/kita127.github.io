#!/usr/bin/env python3
import re
import sys
from html import escape
from html import unescape
from pathlib import Path

import markdown
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import ClassNotFound, TextLexer, get_lexer_by_name
from pygments.token import Token

REPO_ROOT = Path(__file__).resolve().parent.parent
TEST_DESIGN_ROOT = REPO_ROOT / "test_design"


def color_for_token(token_type: tuple) -> str:
    if token_type in {Token.Keyword, Token.Keyword.Declaration, Token.Keyword.Type}:
        return "#c084fc"
    if token_type in {Token.Name.Class, Token.Name.Function, Token.Name.Builtin, Token.Name.Namespace}:
        return "#7dd3fc"
    if token_type in {Token.String, Token.String.Single, Token.String.Double, Token.String.Symbol}:
        return "#86efac"
    if token_type in {Token.Comment, Token.Comment.Single, Token.Comment.Multiline, Token.Comment.Preproc}:
        return "#94a3b8"
    if token_type in {Token.Punctuation, Token.Operator}:
        return "#f8fafc"
    return "#f8fafc"


def render_code_block(language: str, code: str) -> str:
    language_name = language.lower()
    try:
        lexer = get_lexer_by_name(language_name, stripall=True)
    except ClassNotFound:
        lexer = TextLexer()

    source = code
    skip_prefix = False
    if language_name == "php" and not code.lstrip().startswith(("<?php", "<?")):
        source = f"<?php\n{code}"
        skip_prefix = True

    parts: list[str] = []
    for token_type, value in lexer.get_tokens(source):
        if skip_prefix and value in {"<?php", "<?"}:
            continue
        if skip_prefix and value == "\n" and not parts:
            continue
        if value == "\n":
            parts.append("\n")
            continue
        if not value:
            continue
        color = color_for_token(token_type)
        escaped = escape(value)
        parts.append(f'<span style="color: {color};">{escaped}</span>')

    return f'<div class="codehilite"><pre><code>{"".join(parts)}</code></pre></div>'


def highlight_code_blocks(html: str) -> str:
    def repl(match: re.Match[str]) -> str:
        language = match.group(1)
        code = unescape(match.group(2))
        return render_code_block(language, code)

    return re.sub(
        r'<pre><code class="language-([^"]+)">(.+?)</code></pre>',
        repl,
        html,
        flags=re.DOTALL,
    )


def render_markdown(markdown_text: str) -> str:
    html = markdown.markdown(
        markdown_text,
        extensions=["fenced_code", "sane_lists"],
    )
    return highlight_code_blocks(html)


def determine_title(markdown: str) -> str:
    for line in markdown.splitlines():
        if line.startswith("#"):
            return line.lstrip("#").strip()
    return "Article"


def build_html(markdown: str, source_path: Path) -> str:
    title = determine_title(markdown)
    body = render_markdown(markdown)
    style_defs = HtmlFormatter().get_style_defs('.codehilite')
    return f"""<!DOCTYPE html>
<html lang=\"ja\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>{escape(title)}</title>
  <style>
    :root {{ color-scheme: light; }}
    body {{ font-family: \"Inter\", \"Segoe UI\", Roboto, -apple-system, BlinkMacSystemFont, sans-serif; line-height: 1.8; max-width: 860px; margin: 0 auto; padding: 3rem 1.25rem 4rem; color: #0f172a; background: linear-gradient(180deg, #f8fafc 0%, #fefefe 100%); }}
    article {{ background: #ffffff; border: 1px solid #e2e8f0; border-radius: 18px; box-shadow: 0 12px 30px rgba(15, 23, 42, 0.06); padding: 2.2rem 2.2rem 2.6rem; }}
    h1, h2, h3, h4 {{ line-height: 1.3; margin-top: 2rem; color: #0f172a; }}
    h1 {{ font-size: 2rem; margin-top: 0; padding-bottom: 0.7rem; border-bottom: 2px solid #e2e8f0; }}
    h2 {{ font-size: 1.45rem; }}
    h3 {{ font-size: 1.2rem; }}
    p {{ margin: 1rem 0; color: #0f172a; }}
    ul {{ padding-left: 1.3rem; color: #475569; }}
    code {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; background: #f1f5f9; color: #0f172a; padding: 0.12rem 0.38rem; border-radius: 0.3rem; font-size: 0.95em; }}
    pre {{ background: #111827; color: #f8fafc; padding: 1rem 1.1rem; overflow-x: auto; border-radius: 0.75rem; border: 1px solid #334155; }}
    pre code {{ background: transparent; padding: 0; color: inherit; }}
    .codehilite {{ margin: 1rem 0; }}
    .codehilite pre {{ padding: 1rem 1.1rem; }}
    {style_defs}
  </style>
</head>
<body>
  <article>
    {body}
  </article>
</body>
</html>
"""


def render_file(markdown_path: Path) -> Path:
    markdown = markdown_path.read_text(encoding="utf-8")
    html_path = markdown_path.with_suffix(".html")
    html_path.write_text(build_html(markdown, markdown_path), encoding="utf-8")
    return html_path


def main() -> int:
    if not TEST_DESIGN_ROOT.exists():
        print(f"Not found: {TEST_DESIGN_ROOT}", file=sys.stderr)
        return 1

    markdown_files = sorted(TEST_DESIGN_ROOT.rglob("*.md"))
    if not markdown_files:
        print("No markdown files found under test_design.")
        return 0

    for markdown_path in markdown_files:
        output_path = render_file(markdown_path)
        print(f"Generated {output_path.relative_to(REPO_ROOT)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
