from django.test import TestCase

from .serializers import merge_duplicate_books


class MergeDuplicateBooksTests(TestCase):
    def test_merge_duplicate_books_combines_unique_tags(self):
        books = [
            {
                "id": "aladin_9780000000001",
                "source": "aladin",
                "sources": ["aladin"],
                "title": "Test Book",
                "author": "",
                "publisher": "",
                "pubDate": "",
                "cover": None,
                "isbn": "9780000000001",
                "description": None,
                "link": None,
                "tags": ["국내도서", "한국소설"],
            },
            {
                "id": "google_9780000000001",
                "source": "google",
                "sources": ["google"],
                "title": "Test Book",
                "author": "",
                "publisher": "",
                "pubDate": "",
                "cover": None,
                "isbn": "9780000000001",
                "description": None,
                "link": None,
                "tags": ["한국소설", "Fiction"],
            },
        ]

        merged = merge_duplicate_books(books)

        self.assertEqual(merged[0]["tags"], ["국내도서", "한국소설", "Fiction"])
