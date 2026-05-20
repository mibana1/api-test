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


def normalize_kakao_item(item: dict[str, Any], index: int) -> dict[str, Any]:
    authors = item.get("authors") or []
    isbn = get_isbn(item.get("isbn"))
    return {
        "id": f"kakao_{isbn or index}",
        "source": "kakao",
        "sources": ["kakao"],
        "title": clean_text(item.get("title")),
        "author": ", ".join(clean_text(author) for author in authors if author),
        "publisher": clean_text(item.get("publisher")),
        "pubDate": clean_text(item.get("datetime"))[:10],
        "cover": item.get("thumbnail") or None,
        "isbn": isbn,
        "description": clean_description(item.get("contents")),
        "link": item.get("url") or None,
    }
