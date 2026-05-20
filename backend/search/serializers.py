import re
from typing import Any


TRUNCATED_RE = re.compile("(?:\\.{2,}|\\u2026|\\u22ef)\\s*$")

MERGE_FIELDS = [
    "title",
    "author",
    "publisher",
    "pubDate",
    "cover",
    "isbn",
    "description",
    "link",
]


def has_value(value: Any) -> bool:
    return value not in (None, "", [], {})


def completeness_score(book: dict[str, Any]) -> int:
    return sum(1 for field in MERGE_FIELDS if has_value(book.get(field)))


def is_truncated_text(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    return bool(TRUNCATED_RE.search(value))


def better_description(current: Any, candidate: Any) -> Any:
    if not has_value(current):
        return None if is_truncated_text(candidate) else candidate
    if not has_value(candidate):
        return None if is_truncated_text(current) else current

    current_text = str(current).strip()
    candidate_text = str(candidate).strip()
    current_truncated = is_truncated_text(current_text)
    candidate_truncated = is_truncated_text(candidate_text)

    if current_truncated and candidate_truncated:
        return None
    if current_truncated:
        return candidate
    if candidate_truncated:
        return current
    return candidate if len(candidate_text) > len(current_text) else current


def merge_duplicate_books(books: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_isbn: dict[str, dict[str, Any]] = {}
    no_isbn: list[dict[str, Any]] = []

    for book in books:
        isbn = book.get("isbn")
        if not isbn:
            if is_truncated_text(book.get("description")):
                book = {**book, "description": None}
            no_isbn.append(book)
            continue

        key = str(isbn).strip()
        existing = by_isbn.get(key)
        if existing is None:
            description = book.get("description")
            by_isbn[key] = {
                **book,
                "description": None if is_truncated_text(description) else description,
                "sources": list(dict.fromkeys(book.get("sources", []))),
            }
            continue

        sources = list(
            dict.fromkeys([*existing.get("sources", []), *book.get("sources", [])])
        )
        best = book if completeness_score(book) > completeness_score(existing) else existing
        merged = {**best, "sources": sources}
        for field in MERGE_FIELDS:
            if field == "description":
                merged[field] = better_description(existing.get(field), book.get(field))
                continue
            if not has_value(merged.get(field)):
                merged[field] = existing.get(field) or book.get(field)
        by_isbn[key] = merged

    return [*by_isbn.values(), *no_isbn]
