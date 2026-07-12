#!/usr/bin/env python3
import re
import sys
from html import escape
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEST_DESIGN_ROOT = REPO_ROOT / "test_design"


def render_inline(text: str) -> str:
    text = text.replace("<br>", "__BR__")
    text = escape(text)
    text = text.replace("__BR__", "<br>")
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    return text


def render_code_block(code: str, language: str) -> str:
    highlighted = escape(code)
    normalized_language = language.strip().lower()

    if normalized_language in {"php", "php7", "php8"}:
        keyword_pattern = re.compile(
            r"\b(abstract|and|array|as|break|callable|case|catch|class|clone|const|continue|declare|default|do|echo|else|elseif|empty|enddeclare|endfor|endforeach|endif|endswitch|endwhile|eval|exit|extends|final|finally|fn|for|foreach|function|global|goto|if|implements|include|include_once|instanceof|insteadof|interface|isset|list|match|namespace|new|or|print|private|protected|public|readonly|require|require_once|return|static|switch|throw|trait|try|unset|use|var|while|xor|yield|yield from)\b"
        )
        parts: list[str] = []
        last_index = 0
        for match in keyword_pattern.finditer(code):
            parts.append(escape(code[last_index:match.start()]))
            parts.append(f'<span class="token keyword">{escape(match.group(0))}</span>')
            last_index = match.end()
        parts.append(escape(code[last_index:]))
        highlighted = "".join(parts)

    return f'<pre><code class="language-{escape(normalized_language)}">{highlighted}</code></pre>'


def render_markdown(markdown: str) -> str:
    lines = markdown.splitlines()
    blocks: list[str] = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped == "---":
            blocks.append("<hr>")
            i += 1
            continue

        if stripped.startswith("```"):
            language = stripped[3:].strip()
            code_lines: list[str] = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            if i < len(lines):
                i += 1
            code_block = "\n".join(code_lines)
            blocks.append(render_code_block(code_block, language))
            continue

        heading_match = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if heading_match:
            level = len(heading_match.group(1))
            text = render_inline(heading_match.group(2))
            blocks.append(f"<h{level}>{text}</h{level}>")
            i += 1
            continue

        bullet_match = re.match(r"^-\s+(.*)$", stripped)
        if bullet_match:
            items: list[str] = []
            while i < len(lines):
                current = lines[i].strip()
                current_match = re.match(r"^-\s+(.*)$", current)
                if not current_match:
                    break
                items.append(render_inline(current_match.group(1)))
                i += 1
            blocks.append("<ul>" + "".join(f"<li>{item}</li>" for item in items) + "</ul>")
            continue

        paragraph_lines: list[str] = []
        while i < len(lines):
            current = lines[i].strip()
            if not current:
                break
            if current.startswith("```"):
                break
            if re.match(r"^(#{1,6})\s+", current) or re.match(r"^-\s+", current):
                break
            paragraph_lines.append(current)
            i += 1

        if paragraph_lines:
            text = " ".join(paragraph_lines)
            blocks.append(f"<p>{render_inline(text)}</p>")
            continue

        i += 1

    return "\n".join(blocks)


def determine_title(markdown: str) -> str:
    match = re.search(r"^(#{1,6})\s+(.+)$", markdown, flags=re.MULTILINE)
    if match:
        return match.group(2).strip()
    return "Article"


def build_html(markdown: str, source_path: Path) -> str:
    title = determine_title(markdown)
    body = render_markdown(markdown)
    return f"""<!DOCTYPE html>
<html lang=\"ja\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>{escape(title)}</title>
  <style>
    :root {{ color-scheme: light; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", sans-serif; line-height: 1.7; max-width: 860px; margin: 0 auto; padding: 2rem 1.25rem 3rem; color: #1f2937; }}
    h1, h2, h3, h4 {{ line-height: 1.3; margin-top: 2rem; }}
    h1 {{ font-size: 2rem; border-bottom: 1px solid #e5e7eb; padding-bottom: 0.4rem; }}
    h2 {{ font-size: 1.5rem; }}
    h3 {{ font-size: 1.2rem; }}
    p {{ margin: 1rem 0; }}
    ul {{ padding-left: 1.2rem; }}
    code {{ font-family: ui-monospace, SFMono-Regular, monospace; background: #f3f4f6; padding: 0.1rem 0.35rem; border-radius: 0.25rem; }}
    pre {{ background: #111827; color: #f9fafb; padding: 1rem; overflow-x: auto; border-radius: 0.5rem; }}
    pre code {{ background: transparent; padding: 0; color: inherit; }}
    .token.keyword {{ color: #c084fc; }}
    a {{ color: #2563eb; }}
  </style>
</head>
<body>
  <article>
    <h1>{escape(title)}</h1>
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
