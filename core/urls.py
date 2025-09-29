from django.urls import path

from .views import rate_movie, recommend_view, search_movies

urlpatterns = [
    path("recommendations/", recommend_view),
    path("movies/search/", search_movies),
    path("ratings/", rate_movie),
]
