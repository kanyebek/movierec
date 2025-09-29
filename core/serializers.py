from rest_framework import serializers
from core.models import Movie, Rating, Tag

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ['id', 'movie_id', 'title', 'genres', 'overview', 'poster_path']

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['user_id', 'movie', 'rating']