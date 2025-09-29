import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import Movie, Rating, Tag


class Command(BaseCommand):
    help = "Load MovieLens CSVs from ./data (movies.csv, ratings.csv, tags.csv)"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        movies = pd.read_csv("ml-latest-small/movies.csv")
        ratings = pd.read_csv("ml-latest-small/ratings.csv")
        tags = pd.read_csv("ml-latest-small/tags.csv")

        Movie.objects.bulk_create(
            [
                Movie(
                    movie_id=int(r.movieId),
                    title=r.title,
                    genres=(r.genres if pd.notna(r.genres) else ""),
                )
                for r in movies.itertuples(index=False)
            ],
            ignore_conflicts=True,
        )

        movie_map = {m.movie_id: m.id for m in Movie.objects.only("id", "movie_id")}

        Tag.objects.bulk_create(
            [
                Tag(movie_id=movie_map[int(r.movieId)], tag=str(r.tag))
                for r in tags.itertuples(index=False)
                if int(r.movieId) in movie_map and pd.notna(r.tag)
            ],
            ignore_conflicts=True,
        )

        Rating.objects.bulk_create(
            [
                Rating(
                    user_id=int(r.userId),
                    movie_id=movie_map[int(r.movieId)],
                    rating=float(r.rating),
                )
                for r in ratings.itertuples(index=False)
                if int(r.movieId) in movie_map
            ],
            ignore_conflicts=True,
        )

        self.stdout.write(self.style.SUCCESS("Loaded MovieLens."))
