from django.urls import path

from .views import CenterSearchView


urlpatterns = [
    path("search", CenterSearchView.as_view(), name="center-search-noslash"),
    path("search/", CenterSearchView.as_view(), name="center-search"),
]
