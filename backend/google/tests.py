from django.test import TestCase

from .serializers import normalize_google_item


class GooglePlaceholderTests(TestCase):
    def test_normalize_google_item_includes_category_tags(self):
        book = normalize_google_item(
            {
                "id": "volume-id",
                "volumeInfo": {
                    "title": "Test Book",
                    "categories": ["Fiction / Mystery", "Fiction"],
                },
            },
            0,
        )

        self.assertEqual(book["tags"], ["Fiction", "Mystery"])
