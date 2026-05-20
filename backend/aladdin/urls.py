from django.urls import path

from .views import AladdinSearchView


urlpatterns = [
    path("search", AladdinSearchView.as_view(), name="aladdin-search-noslash"),
    path("search/", AladdinSearchView.as_view(), name="aladdin-search"),
]
