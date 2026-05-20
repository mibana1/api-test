from html import unescape
import re
from typing import Any


TAG_RE = re.compile(r"<[^>]+>")
TRUNCATED_RE = re.compile("(?:\\.{2,}|\\u2026|\\u22ef)\\s*$")


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    return TAG_RE.sub("", unescape(str(value))).strip()


def clean_description(value: Any) -> str | None:
    description = clean_text(value)
    if not description or TRUNCATED_RE.search(description):
        return None
    return description


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
    }
