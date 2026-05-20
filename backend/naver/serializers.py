from html import unescape
import re
from typing import Any


TAG_RE = re.compile(r"<[^>]+>")
TRUNCATED_RE = re.compile("(?:\\.{2,}|\\u2026|\\u22ef)\\s*$")


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    return TAG_RE.sub("", unescape(str(value))).strip()


def get_isbn(value: Any) -> str | None:
    isbns = [clean_text(part) for part in str(value or "").split()]
    for isbn in isbns:
        if len(isbn) == 13:
            return isbn
    return isbns[0] if isbns else None


def clean_description(value: Any) -> str | None:
    description = clean_text(value)
    if not description or TRUNCATED_RE.search(description):
        return None
    return description


def normalize_naver_item(item: dict[str, Any], index: int) -> dict[str, Any]:
    isbn = get_isbn(item.get("isbn"))
    return {
        "id": f"naver_{isbn or index}",
        "source": "naver",
        "sources": ["naver"],
        "title": clean_text(item.get("title")),
        "author": clean_text(item.get("author")),
        "publisher": clean_text(item.get("publisher")),
        "pubDate": clean_text(item.get("pubdate")),
        "cover": item.get("image") or None,
        "isbn": isbn,
        "description": clean_description(item.get("description")),
        "link": item.get("link") or None,
    }
