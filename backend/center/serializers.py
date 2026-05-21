from html import unescape
import re
from typing import Any


TAG_RE = re.compile(r"<[^>]+>")
TRUNCATED_RE = re.compile("(?:\\.{2,}|\\u2026|\\u22ef)\\s*$")
TAG_SPLIT_RE = re.compile(r"\s*(?:>|/|;|,)\s*")


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    return TAG_RE.sub("", unescape(str(value))).strip()


def clean_description(value: Any) -> str | None:
    description = clean_text(value)
    if not description or TRUNCATED_RE.search(description):
        return None
    return description


def normalize_tags(*values: Any) -> list[str]:
    tags: list[str] = []
    for value in values:
        if not value:
            continue
        raw_tags = value if isinstance(value, list) else [value]
        for raw_tag in raw_tags:
            for tag in TAG_SPLIT_RE.split(clean_text(raw_tag)):
                if tag and tag not in tags:
                    tags.append(tag)
    return tags


def normalize_center_item(item: dict[str, Any], index: int) -> dict[str, Any]:
    isbn = clean_text(item.get("isbn") or item.get("isbn13")) or None
    link = item.get("link") or item.get("detail_link") or None
    if isinstance(link, str) and link.startswith("/"):
        link = f"https://www.nl.go.kr{link}"

    cover = item.get("bookImageURL") or item.get("cover") or item.get("image_url") or None
    if cover == "http://cover.nl.go.kr/":
        cover = None

    return {
        "id": f"center_{isbn or index}",
        "source": "center",
        "sources": ["center"],
        "title": clean_text(item.get("title") or item.get("title_info")),
        "author": clean_text(item.get("author") or item.get("author_info")),
        "publisher": clean_text(item.get("publisher") or item.get("pub_info")),
        "pubDate": clean_text(item.get("pubDate") or item.get("pubdate") or item.get("pub_year_info")),
        "cover": cover,
        "isbn": isbn,
        "description": clean_description(item.get("description") or item.get("contents")),
        "link": link,
        "tags": normalize_tags(
            item.get("category"),
            item.get("categoryName"),
            item.get("className"),
            item.get("class_nm"),
            item.get("subject"),
            item.get("subject_info"),
        ),
    }
