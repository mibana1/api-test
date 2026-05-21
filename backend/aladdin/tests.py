from django.test import TestCase

from .serializers import normalize_aladdin_item


class AladdinPlaceholderTests(TestCase):
    def test_normalize_aladdin_item_includes_category_tags(self):
        book = normalize_aladdin_item(
            {
                "isbn13": "9780000000001",
                "title": "Test Book",
                "categoryName": "국내도서>소설/시/희곡>한국소설",
            },
            0,
        )

        self.assertEqual(book["tags"], ["국내도서", "소설", "시", "희곡", "한국소설"])
