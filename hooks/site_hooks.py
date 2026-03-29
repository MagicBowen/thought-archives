from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Iterable


MEDIA_EXTENSIONS = {
    ".apng",
    ".avif",
    ".bmp",
    ".doc",
    ".docx",
    ".gif",
    ".ico",
    ".jpeg",
    ".jpg",
    ".key",
    ".m4a",
    ".m4v",
    ".mov",
    ".mp3",
    ".mp4",
    ".ogg",
    ".pdf",
    ".png",
    ".ppt",
    ".pptx",
    ".svg",
    ".txt",
    ".wav",
    ".webm",
    ".webp",
    ".xls",
    ".xlsx",
}

HTML_SRC_RE = re.compile(r'(<(?:img|source)\b[^>]*?\s(?:src|srcset)=["\'])([^"\']+)(["\'])', re.IGNORECASE)
HTML_HREF_RE = re.compile(r'(<a\b[^>]*?\shref=["\'])([^"\']+)(["\'])', re.IGNORECASE)
LEADING_H1_RE = re.compile(r"^\s*<h1\b[^>]*>.*?</h1>\s*", re.IGNORECASE | re.DOTALL)
HEADING_RE = re.compile(r"^\s*#\s+(.+?)\s*$", re.MULTILINE)
IMAGE_LINE_RE = re.compile(r"^\s*!?\[[^\]]*]\([^)]+\)\s*$")
HTML_TAG_RE = re.compile(r"<[^>]+>")
LINK_RE = re.compile(r"\[([^\]]+)]\([^)]+\)")
INLINE_CODE_RE = re.compile(r"`([^`]+)`")


def _is_external(target: str) -> bool:
    return (
        not target
        or target.startswith(("#", "/", "mailto:", "tel:"))
        or "://" in target
        or target.startswith("data:")
    )


def _looks_like_media(target: str) -> bool:
    clean = target.split("#", 1)[0].split("?", 1)[0]
    return Path(clean).suffix.lower() in MEDIA_EXTENSIONS


def _as_posix_relpath(target: PurePosixPath, current: PurePosixPath) -> str:
    return os.path.relpath(str(target), str(current)).replace(os.sep, "/")


def _rewrite_target(src_uri: str, target: str) -> str:
    if _is_external(target) or not _looks_like_media(target):
        return target

    source_path = PurePosixPath(src_uri)
    source_dir = source_path.parent
    target_path = PurePosixPath(os.path.normpath(str(source_dir / target)).replace("\\", "/"))
    current_output_dir = source_path.parent if source_path.name == "index.md" else source_path.with_suffix("")
    rewritten = _as_posix_relpath(target_path, current_output_dir)

    if "#" in target:
        rewritten += "#" + target.split("#", 1)[1]
    elif "?" in target:
        rewritten += "?" + target.split("?", 1)[1]
    return rewritten


def _rewrite_html_attrs(html: str, src_uri: str) -> str:
    def replace_src(match: re.Match[str]) -> str:
        prefix, target, suffix = match.groups()
        rewritten = ", ".join(
            _rewrite_target(src_uri, chunk.strip())
            for chunk in target.split(",")
        ) if "," in target and " " not in target else _rewrite_target(src_uri, target)
        return f"{prefix}{rewritten}{suffix}"

    html = HTML_SRC_RE.sub(replace_src, html)

    def replace_href(match: re.Match[str]) -> str:
        prefix, target, suffix = match.groups()
        return f"{prefix}{_rewrite_target(src_uri, target)}{suffix}"

    return HTML_HREF_RE.sub(replace_href, html)


def _extract_title(markdown: str, fallback: str) -> str:
    match = HEADING_RE.search(markdown)
    return match.group(1).strip() if match else fallback


def _extract_excerpt(markdown: str) -> str:
    chunks = re.split(r"\n\s*\n", markdown)
    for chunk in chunks:
        text = chunk.strip()
        if not text:
            continue
        if text.startswith("#") or text.startswith("---") or text == "[TOC]":
            continue
        if IMAGE_LINE_RE.match(text):
            continue
        if text.startswith("<div") or text.startswith("<img"):
            continue
        clean = HTML_TAG_RE.sub("", text)
        clean = LINK_RE.sub(r"\1", clean)
        clean = INLINE_CODE_RE.sub(r"\1", clean)
        clean = " ".join(clean.split())
        if clean:
            return clean[:180] + ("..." if len(clean) > 180 else "")
    return ""


def _fallback_mtime(path: Path) -> datetime:
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)


def _section_label(src_uri: str) -> str:
    parts = PurePosixPath(src_uri).parts
    if len(parts) <= 1:
        return ""
    if len(parts) == 2:
        return parts[0]
    return " / ".join(parts[:-1])


def _collect_pages(nav_items: Iterable) -> Iterable:
    for item in nav_items:
        if getattr(item, "is_page", False):
            yield item
        children = getattr(item, "children", None)
        if children:
            yield from _collect_pages(children)


def on_page_markdown(markdown, page, config, files):
    return _rewrite_html_attrs(markdown, page.file.src_uri)


def on_page_content(html, page, config, files):
    if not page.is_homepage:
        html = LEADING_H1_RE.sub("", html, count=1)
    return html


def on_nav(nav, config, files):
    docs_root = Path(config.docs_dir)
    posts = []

    for page in _collect_pages(nav.items):
        if page.is_homepage:
            continue

        src_uri = page.file.src_uri
        source_path = docs_root / src_uri
        markdown = source_path.read_text(encoding="utf-8")
        updated_at = _fallback_mtime(source_path)
        date_label = updated_at.astimezone().strftime("%Y-%m-%d %H:%M")
        excerpt = _extract_excerpt(markdown)
        title = page.title or _extract_title(markdown, page.file.name)
        section = _section_label(src_uri)

        page.meta["resolved_date"] = date_label
        page.meta["resolved_section"] = section
        page.meta["resolved_excerpt"] = excerpt

        posts.append(
            {
                "title": title,
                "url": page.url,
                "date": updated_at,
                "date_label": date_label,
                "section": section,
                "src_uri": src_uri,
                "excerpt": excerpt,
            }
        )

    posts.sort(key=lambda item: item["date"], reverse=True)
    config.extra["archive_posts"] = posts
    return nav
