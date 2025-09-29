from django.contrib import admin
from .models import Movie, Tag, Rating

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("id", "movie_id", "title", "genres")
    search_fields = ("title", "genres")

admin.site.register(Tag)
admin.site.register(Rating)