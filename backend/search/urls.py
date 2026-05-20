from django.urls import path

from .views import UnifiedSearchView


urlpatterns = [
    path("", UnifiedSearchView.as_view(), name="unified-search"),
]
