import asyncio
from typing import Any, Awaitable, Callable

import httpx
from asgiref.sync import async_to_sync
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from aladdin.views import search_aladdin_books
from center.views import search_center_books
from google.views import search_google_books
from kakao.views import search_kakao_books
from naver.views import search_naver_books

from .serializers import merge_duplicate_books


ProviderSearch = Callable[[str, httpx.AsyncClient | None], Awaitable[list[dict[str, Any]]]]


async def safe_provider_search(
    provider: ProviderSearch,
    query: str,
    client: httpx.AsyncClient,
) -> list[dict[str, Any]]:
    try:
        return await provider(query, client)
    except (ValueError, httpx.HTTPError):
        return []


async def unified_search_books(query: str) -> list[dict[str, Any]]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        results = await asyncio.gather(
            safe_provider_search(search_aladdin_books, query, client),
            safe_provider_search(search_center_books, query, client),
            safe_provider_search(search_google_books, query, client),
            safe_provider_search(search_kakao_books, query, client),
            safe_provider_search(search_naver_books, query, client),
        )

    merged = [book for provider_books in results for book in provider_books]
    return merge_duplicate_books(merged)


class UnifiedSearchView(APIView):
    def post(self, request):
        query = str(request.data.get("query", "")).strip()
        if not query:
            return Response(
                {"detail": "query is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(async_to_sync(unified_search_books)(query))
