from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/aladdin/", include("aladdin.urls")),
    path("api/center/", include("center.urls")),
    path("api/google/", include("google.urls")),
    path("api/kakao/", include("kakao.urls")),
    path("api/naver/", include("naver.urls")),
    path("api/search", include("search.urls")),
    path("api/search/", include("search.urls")),
    path("api/recommender/", include("recommender.urls")),
    path("api/vision/", include("vision.urls")),
]
