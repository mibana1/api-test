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


def get_isbn(volume_info: dict[str, Any]) -> str | None:
    identifiers = volume_info.get("industryIdentifiers") or []
    for identifier in identifiers:
        if identifier.get("type") == "ISBN_13":
            return clean_text(identifier.get("identifier")) or None
    for identifier in identifiers:
        if identifier.get("type") == "ISBN_10":
            return clean_text(identifier.get("identifier")) or None
    return None


def normalize_google_item(item: dict[str, Any], index: int) -> dict[str, Any]:
    volume_info = item.get("volumeInfo", {})
    isbn = get_isbn(volume_info)
    authors = volume_info.get("authors") or []
    image_links = volume_info.get("imageLinks") or {}
    return {
        "id": f"google_{isbn or item.get('id') or index}",
        "source": "google",
        "sources": ["google"],
        "title": clean_text(volume_info.get("title")),
        "author": ", ".join(clean_text(author) for author in authors if author),
        "publisher": clean_text(volume_info.get("publisher")),
        "pubDate": clean_text(volume_info.get("publishedDate")),
        "cover": image_links.get("thumbnail") or image_links.get("smallThumbnail") or None,
        "isbn": isbn,
        "description": clean_description(volume_info.get("description")),
        "link": volume_info.get("infoLink") or None,
        "tags": normalize_tags(volume_info.get("categories")),
    }
