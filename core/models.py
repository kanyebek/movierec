from django.db import models

class Movie(models.Model):
    movie_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    genres = models.CharField(max_length=255, blank=True, null=True)
    overview = models.TextField(blank=True, null=True)
    poster_path = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return self.title if self.title else f"Movie {self.movie_id}"
    
class Tag(models.Model):
    movie = models.ForeignKey(Movie, related_name='tags', on_delete=models.CASCADE)
    tag = models.CharField(max_length=100)
    
    def __str__(self):
        return self.tag
    
class Rating(models.Model):
    movie = models.ForeignKey(Movie, related_name='ratings', on_delete=models.CASCADE)
    user_id = models.IntegerField()
    rating = models.FloatField()
    
    class Meta:
        indexes = [models.Index(fields=['movie', 'user_id'])]  
        unique_together = ('movie', 'user_id')
    
    def __str__(self):
        return f"Rating {self.rating} by User {self.user_id} for Movie {self.movie.movie_id}"
# Create your models here.

class RecommendationHistory(models.Model):
    user_id = models.IntegerField()
    movie_id = models.IntegerField()
    recommended_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["user_id", "movie_id"])]
        unique_together = ("user_id", "movie_id")

    def __str__(self):
        return f"User {self.user_id} recommended Movie {self.movie_id}"
