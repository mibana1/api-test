import os
from typing import Any

import httpx
from asgiref.sync import async_to_sync
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import normalize_aladdin_item


ALADIN_SEARCH_URL = "http://www.aladin.co.kr/ttb/api/ItemSearch.aspx"
ALADIN_PAGE_SIZE = 50
ALADIN_MAX_PAGES = 50


async def search_aladdin_books(
    query: str,
    client: httpx.AsyncClient | None = None,
    max_results: int = ALADIN_PAGE_SIZE,
) -> list[dict[str, Any]]:
    api_key = os.getenv("ALADIN_API_KEY")
    if not api_key:
        raise ValueError("ALADIN_API_KEY is not configured.")

    page_size = min(max_results, ALADIN_PAGE_SIZE)

    async def fetch(active_client: httpx.AsyncClient) -> list[dict[str, Any]]:
        books: list[dict[str, Any]] = []
        for page in range(1, ALADIN_MAX_PAGES + 1):
            params = {
                "TTBKey": api_key,
                "Query": query,
                "QueryType": "Keyword",
                "MaxResults": page_size,
                "Start": page,
                "output": "js",
                "Version": "20131101",
            }
            response = await active_client.get(ALADIN_SEARCH_URL, params=params)
            response.raise_for_status()
            data = response.json()
            items = data.get("item", [])
            start_index = len(books)
            books.extend(
                normalize_aladdin_item(item, start_index + index)
                for index, item in enumerate(items)
            )
            total_results = int(data.get("totalResults") or 0)
            if len(items) < page_size or (total_results and len(books) >= total_results):
                break
        return books

    if client is not None:
        return await fetch(client)

    async with httpx.AsyncClient(timeout=10.0) as active_client:
        return await fetch(active_client)


class AladdinSearchView(APIView):
    def post(self, request):
        query = str(request.data.get("query", "")).strip()
        if not query:
            return Response(
                {"detail": "query is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            return Response(async_to_sync(search_aladdin_books)(query))
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except httpx.HTTPError as exc:
            status_code = getattr(getattr(exc, "response", None), "status_code", "unknown")
            return Response(
                {"detail": f"Aladin API request failed with status {status_code}."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
