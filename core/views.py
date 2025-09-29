from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from core.models import Movie, Rating
from .serializers import MovieSerializer, RatingSerializer
from core.recommender.content import recommend_for_user
from core.recommender.content import build_index

@api_view(["GET"])
def recommend_view(request):
    try:
        user_id = int(request.GET.get("user_id"))
    except (TypeError, ValueError):
        return Response({"detail": "user_id is required and must be int"}, status=400)
    k = int(request.GET.get("k", 20))
    recs = recommend_for_user(user_id, top_k=k)
    return Response(recs)

@api_view(["GET"])
def search_movies(request):
    q = request.GET.get("q", "")
    qs = Movie.objects.filter(title__icontains=q)[:50]
    return Response(MovieSerializer(qs, many=True).data)

@api_view(["POST"])
def rate_movie(request):
    data = request.data.copy()
    ser = RatingSerializer(data=data)
    ser.is_valid(raise_exception=True)
    ser.save()
    build_index()
    return Response(ser.data, status=status.HTTP_201_CREATED)
# Create your views here.
