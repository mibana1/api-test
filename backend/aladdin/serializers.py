from html import unescape
import re
from typing import Any


TAG_RE = re.compile(r"<[^>]+>")
TRUNCATED_RE = re.compile("(?:\\.{2,}|\\u2026|\\u22ef)\\s*$")
TAG_SPLIT_RE = re.compile(r"\s*(?:>|/)\s*")


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    return TAG_RE.sub("", unescape(str(value))).strip()


def clean_description(value: Any) -> str | None:
    description = clean_text(value)
    if not description or TRUNCATED_RE.search(description):
        return None
    return description


def normalize_tags(value: Any) -> list[str]:
    if not value:
        return []

    raw_tags = value if isinstance(value, list) else [value]
    tags: list[str] = []
    for raw_tag in raw_tags:
        for tag in TAG_SPLIT_RE.split(clean_text(raw_tag)):
            if tag and tag not in tags:
                tags.append(tag)
    return tags


def normalize_aladdin_item(item: dict[str, Any], index: int) -> dict[str, Any]:
    isbn = clean_text(item.get("isbn13")) or clean_text(item.get("isbn")) or None
    return {
        "id": f"aladin_{isbn or index}",
        "source": "aladin",
        "sources": ["aladin"],
        "title": clean_text(item.get("title")),
        "author": clean_text(item.get("author")),
        "publisher": clean_text(item.get("publisher")),
        "pubDate": clean_text(item.get("pubDate")),
        "cover": item.get("coverSmallUrl") or item.get("cover") or None,
        "isbn": isbn,
        "description": clean_description(item.get("description")),
        "link": item.get("link") or None,
        "tags": normalize_tags(item.get("categoryName")),
    }
