import os
import xml.etree.ElementTree as ET
from typing import Any

import httpx
from asgiref.sync import async_to_sync
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import normalize_center_item


CENTER_SEARCH_URL = "https://www.nl.go.kr/NL/search/openApi/search.do"
CENTER_PAGE_SIZE = 50
CENTER_MAX_PAGES = 50


def extract_center_items(data: dict[str, Any]) -> list[dict[str, Any]]:
    candidates = [
        data.get("result"),
        data.get("docs"),
        data.get("items"),
        data.get("item"),
    ]
    for candidate in candidates:
        if isinstance(candidate, list):
            return candidate
        if isinstance(candidate, dict):
            for key in ("result", "docs", "items", "item"):
                nested = candidate.get(key)
                if isinstance(nested, list):
                    return nested
    return []


def extract_center_xml_items(text: str) -> list[dict[str, Any]]:
    root = ET.fromstring(text)
    return [
        {child.tag: child.text or "" for child in item}
        for item in root.findall(".//result/item")
    ]


async def search_center_books(
    query: str,
    client: httpx.AsyncClient | None = None,
    max_results: int = CENTER_PAGE_SIZE,
) -> list[dict[str, Any]]:
    api_key = os.getenv("NL_API_KEY")
    if not api_key:
        raise ValueError("NL_API_KEY is not configured.")

    page_size = min(max_results, CENTER_PAGE_SIZE)

    async def fetch(active_client: httpx.AsyncClient) -> list[dict[str, Any]]:
        books: list[dict[str, Any]] = []
        for page in range(1, CENTER_MAX_PAGES + 1):
            params = {
                "key": api_key,
                "srchTarget": "total",
                "kwd": query,
                "pageSize": page_size,
                "pageNum": page,
                "format": "json",
            }
            response = await active_client.get(CENTER_SEARCH_URL, params=params)
            response.raise_for_status()
            content_type = response.headers.get("content-type", "")
            if "xml" in content_type or response.text.lstrip().startswith("<"):
                items = extract_center_xml_items(response.text)
            else:
                items = extract_center_items(response.json())
            start_index = len(books)
            books.extend(
                normalize_center_item(item, start_index + index)
                for index, item in enumerate(items)
            )
            if len(items) < page_size:
                break
        return books

    if client is not None:
        return await fetch(client)

    async with httpx.AsyncClient(timeout=10.0) as active_client:
        return await fetch(active_client)


class CenterSearchView(APIView):
    def post(self, request):
        query = str(request.data.get("query", "")).strip()
        if not query:
            return Response(
                {"detail": "query is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            return Response(async_to_sync(search_center_books)(query))
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except httpx.HTTPError as exc:
            status_code = getattr(getattr(exc, "response", None), "status_code", "unknown")
            return Response(
                {"detail": f"National Library API request failed with status {status_code}."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
