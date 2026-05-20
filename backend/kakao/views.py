import os
from typing import Any

import httpx
from asgiref.sync import async_to_sync
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import normalize_kakao_item


KAKAO_BOOK_SEARCH_URL = "https://dapi.kakao.com/v3/search/book"
KAKAO_PAGE_SIZE = 50
KAKAO_MAX_PAGES = 50


async def search_kakao_books(
    query: str,
    client: httpx.AsyncClient | None = None,
    max_results: int = KAKAO_PAGE_SIZE,
) -> list[dict[str, Any]]:
    api_key = os.getenv("KAKAO_REST_API_KEY")
    if not api_key:
        raise ValueError("KAKAO_REST_API_KEY is not configured.")

    page_size = min(max_results, KAKAO_PAGE_SIZE)
    headers = {"Authorization": f"KakaoAK {api_key}"}

    async def fetch(active_client: httpx.AsyncClient) -> list[dict[str, Any]]:
        books: list[dict[str, Any]] = []
        for page in range(1, KAKAO_MAX_PAGES + 1):
            params = {
                "query": query,
                "sort": "accuracy",
                "page": page,
                "size": page_size,
            }
            response = await active_client.get(
                KAKAO_BOOK_SEARCH_URL,
                params=params,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
            items = data.get("documents", [])
            start_index = len(books)
            books.extend(
                normalize_kakao_item(item, start_index + index)
                for index, item in enumerate(items)
            )
            meta = data.get("meta", {})
            if meta.get("is_end") or len(items) < page_size:
                break
        return books

    if client is not None:
        return await fetch(client)

    async with httpx.AsyncClient(timeout=10.0) as active_client:
        return await fetch(active_client)


class KakaoSearchView(APIView):
    def post(self, request):
        query = str(request.data.get("query", "")).strip()
        if not query:
            return Response(
                {"detail": "query is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            return Response(async_to_sync(search_kakao_books)(query))
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except httpx.HTTPError as exc:
            status_code = getattr(getattr(exc, "response", None), "status_code", "unknown")
            return Response(
                {"detail": f"Kakao API request failed with status {status_code}."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
