from django.db import models
from movie.models import Movie

class Recommendation(models.Model):
    prompt = models.TextField()
    recommended_movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Recomendación para: {self.prompt}"