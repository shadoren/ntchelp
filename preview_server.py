#!/usr/bin/env python3
"""Local preview server for NTCHELP (static files + lightweight Markdown/layout)."""

from __future__ import annotations

import html
import re
import urllib.parse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PORT = 6969


def parse_front_matter(text: str) -> tuple[str, str]:
    title = "NTCHELP, INC."
    body = text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            fm, body = parts[1], parts[2]
            m = re.search(r"^title:\s*(.+)$", fm, re.M)
            if m:
                title = m.group(1).strip().strip("\"'")
    return title, body.lstrip("\n")


def inline_md(text: str) -> str:
    # Escape first, then reintroduce intentional HTML from markdown
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        r'<a href="\2">\1</a>',
        text,
    )
    return text


def md_to_html(md: str) -> str:
    """Small Markdown subset + pass-through of raw HTML blocks."""
    lines = md.splitlines()
    out: list[str] = []
    i = 0
    in_ul = False
    in_ol = False
    para: list[str] = []

    def close_lists() -> None:
        nonlocal in_ul, in_ol
        if in_ul:
            out.append("</ul>")
            in_ul = False
        if in_ol:
            out.append("</ol>")
            in_ol = False

    def flush_para() -> None:
        nonlocal para
        if para:
            out.append("<p>" + " ".join(para) + "</p>")
            para = []

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Raw HTML block (div, blockquote, etc.)
        if stripped.startswith("<") and not stripped.startswith("</"):
            flush_para()
            close_lists()
            # collect until blank line after closing tag, or single-line tags
            block = [line]
            if not re.search(r"</\w+>\s*$", stripped) and not stripped.endswith("/>"):
                i += 1
                while i < len(lines):
                    block.append(lines[i])
                    if re.search(r"</(div|blockquote|table|ul|ol|nav|section|article)>", lines[i], re.I):
                        break
                    i += 1
            out.append("\n".join(block))
            i += 1
            continue

        if not stripped:
            flush_para()
            close_lists()
            i += 1
            continue

        if stripped.startswith("### "):
            flush_para()
            close_lists()
            out.append(f"<h3>{inline_md(stripped[4:])}</h3>")
            i += 1
            continue
        if stripped.startswith("## "):
            flush_para()
            close_lists()
            out.append(f"<h2>{inline_md(stripped[3:])}</h2>")
            i += 1
            continue
        if stripped.startswith("# "):
            flush_para()
            close_lists()
            out.append(f"<h1>{inline_md(stripped[2:])}</h1>")
            i += 1
            continue

        m_ul = re.match(r"^[-*]\s+(.+)$", stripped)
        if m_ul:
            flush_para()
            if in_ol:
                out.append("</ol>")
                in_ol = False
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{inline_md(m_ul.group(1))}</li>")
            i += 1
            continue

        m_ol = re.match(r"^(\d+)\.\s+(.+)$", stripped)
        if m_ol:
            flush_para()
            if in_ul:
                out.append("</ul>")
                in_ul = False
            if not in_ol:
                out.append("<ol>")
                in_ol = True
            out.append(f"<li>{inline_md(m_ol.group(2))}</li>")
            i += 1
            continue

        # Already-HTML heading from source (e.g. <h1 align="center">)
        if stripped.startswith("<h") or stripped.startswith("<p") or stripped.startswith("<a "):
            flush_para()
            close_lists()
            out.append(line)
            i += 1
            continue

        close_lists()
        para.append(inline_md(stripped))
        i += 1

    flush_para()
    close_lists()
    return "\n".join(out)


def apply_layout(title: str, content: str) -> str:
    nav_path = ROOT / "_includes" / "nav.html"
    nav = nav_path.read_text(encoding="utf-8") if nav_path.exists() else ""
    safe_title = html.escape(title)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{safe_title}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="stylesheet" href="/styles.css">
</head>
<body>
{nav}
{content}
</body>
</html>
"""


def resolve_path(url_path: str) -> Path | None:
    """Map request path to a file under ROOT."""
    path = urllib.parse.unquote(url_path.split("?", 1)[0])
    if path.startswith("/"):
        path = path[1:]
    if ".." in path.split("/"):
        return None

    candidate = ROOT / path if path else ROOT

    if candidate.is_file():
        return candidate

    # Directory → index.md / index.html
    if candidate.is_dir() or path == "":
        directory = candidate if path else ROOT
        for name in ("index.html", "index.md"):
            idx = directory / name
            if idx.is_file():
                return idx
        return None

    # Extensionless → try .html then .md
    if not candidate.suffix:
        for ext in (".html", ".md"):
            alt = Path(str(candidate) + ext)
            if alt.is_file():
                return alt

    return None


class PreviewHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, fmt: str, *args) -> None:
        print(f"[{self.log_date_time_string()}] {args[0]}")

    def do_GET(self) -> None:
        target = resolve_path(self.path)
        if target is None:
            # Fall back to default static handling (404 if missing)
            return super().do_GET()

        if target.suffix.lower() == ".md":
            raw = target.read_text(encoding="utf-8")
            title, body = parse_front_matter(raw)
            content = md_to_html(body)
            page = apply_layout(title, content)
            data = page.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)
            return

        # Static files via parent (correct MIME types)
        # Rewrite path relative to ROOT for SimpleHTTPRequestHandler
        rel = target.relative_to(ROOT).as_posix()
        self.path = "/" + rel
        return super().do_GET()


def main() -> None:
    server = ThreadingHTTPServer(("0.0.0.0", PORT), PreviewHandler)
    print(f"NTCHELP preview → http://127.0.0.1:{PORT}/")
    print(f"Serving {ROOT}")
    print("Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        server.server_close()


if __name__ == "__main__":
    main()
