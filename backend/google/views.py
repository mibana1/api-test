import asyncio
import os
from typing import Any

import httpx
from asgiref.sync import async_to_sync
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import normalize_google_item


GOOGLE_BOOKS_SEARCH_URL = "https://www.googleapis.com/books/v1/volumes"
GOOGLE_TRANSIENT_ERROR = "API key expired"
GOOGLE_PAGE_SIZE = 40
GOOGLE_MAX_RESULTS = 1000


async def search_google_books(
    query: str,
    client: httpx.AsyncClient | None = None,
    max_results: int = GOOGLE_PAGE_SIZE,
) -> list[dict[str, Any]]:
    api_key = os.getenv("GOOGLE_BOOKS_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_BOOKS_API_KEY is not configured.")

    page_size = min(max_results, GOOGLE_PAGE_SIZE)

    async def fetch(active_client: httpx.AsyncClient) -> list[dict[str, Any]]:
        books: list[dict[str, Any]] = []
        start_index = 0
        while start_index < GOOGLE_MAX_RESULTS:
            params = {
                "q": query,
                "maxResults": page_size,
                "startIndex": start_index,
                "key": api_key,
            }
            response: httpx.Response | None = None
            for attempt in range(5):
                response = await active_client.get(GOOGLE_BOOKS_SEARCH_URL, params=params)
                if (
                    response.status_code == 400
                    and GOOGLE_TRANSIENT_ERROR in response.text
                    and attempt < 4
                ):
                    await asyncio.sleep(0.35 * (attempt + 1))
                    continue
                break

            if response is None:
                return books

            if response.status_code == 400 and GOOGLE_TRANSIENT_ERROR in response.text:
                return books

            response.raise_for_status()
            data = response.json()
            items = data.get("items", [])
            books.extend(
                normalize_google_item(item, start_index + index)
                for index, item in enumerate(items)
            )
            total_items = int(data.get("totalItems") or 0)
            start_index += len(items)
            if len(items) < page_size or (total_items and start_index >= total_items):
                break
        return books

    if client is not None:
        return await fetch(client)

    async with httpx.AsyncClient(timeout=10.0) as active_client:
        return await fetch(active_client)


class GoogleSearchView(APIView):
    def post(self, request):
        query = str(request.data.get("query", "")).strip()
        if not query:
            return Response(
                {"detail": "query is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            return Response(async_to_sync(search_google_books)(query))
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except httpx.HTTPError as exc:
            status_code = getattr(getattr(exc, "response", None), "status_code", "unknown")
            return Response(
                {"detail": f"Google Books API request failed with status {status_code}."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
