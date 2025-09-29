from django.contrib import admin
from django.urls import path, include
from .views import recommend_view,search_movies,rate_movie

urlpatterns = [
    path('recommendations/', recommend_view),
    path('movies/search/', search_movies),
    path('ratings/', rate_movie),
]