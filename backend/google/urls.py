from django.urls import path

from .views import GoogleSearchView


urlpatterns = [
    path("search", GoogleSearchView.as_view(), name="google-search-noslash"),
    path("search/", GoogleSearchView.as_view(), name="google-search"),
]
