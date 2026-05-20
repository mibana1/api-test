from django.urls import path

from .views import KakaoSearchView


urlpatterns = [
    path("search", KakaoSearchView.as_view(), name="kakao-search-noslash"),
    path("search/", KakaoSearchView.as_view(), name="kakao-search"),
]
