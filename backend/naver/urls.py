from django.urls import path

from .views import NaverSearchView


urlpatterns = [
    path("search", NaverSearchView.as_view(), name="naver-search-noslash"),
    path("search/", NaverSearchView.as_view(), name="naver-search"),
]
