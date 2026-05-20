import os
from typing import Any

import httpx
from asgiref.sync import async_to_sync
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import normalize_naver_item


NAVER_BOOK_SEARCH_URL = "https://openapi.naver.com/v1/search/book.json"
NAVER_PAGE_SIZE = 100
NAVER_MAX_START = 1000


async def search_naver_books(
    query: str,
    client: httpx.AsyncClient | None = None,
    max_results: int = NAVER_PAGE_SIZE,
) -> list[dict[str, Any]]:
    client_id = os.getenv("NAVER_CLIENT_ID")
    client_secret = os.getenv("NAVER_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise ValueError("NAVER_CLIENT_ID and NAVER_CLIENT_SECRET are not configured.")

    page_size = min(max_results, NAVER_PAGE_SIZE)
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
    }

    async def fetch(active_client: httpx.AsyncClient) -> list[dict[str, Any]]:
        books: list[dict[str, Any]] = []
        start = 1
        while start <= NAVER_MAX_START:
            params = {
                "query": query,
                "display": page_size,
                "start": start,
                "sort": "sim",
            }
            response = await active_client.get(
                NAVER_BOOK_SEARCH_URL,
                params=params,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
            items = data.get("items", [])
            books.extend(
                normalize_naver_item(item, start - 1 + index)
                for index, item in enumerate(items)
            )
            total = int(data.get("total") or 0)
            if len(items) < page_size or (total and len(books) >= total):
                break
            start += page_size
        return books

    if client is not None:
        return await fetch(client)

    async with httpx.AsyncClient(timeout=10.0) as active_client:
        return await fetch(active_client)


class NaverSearchView(APIView):
    def post(self, request):
        query = str(request.data.get("query", "")).strip()
        if not query:
            return Response(
                {"detail": "query is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            return Response(async_to_sync(search_naver_books)(query))
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except httpx.HTTPError as exc:
            status_code = getattr(getattr(exc, "response", None), "status_code", "unknown")
            return Response(
                {"detail": f"Naver API request failed with status {status_code}."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
