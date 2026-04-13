from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Book(models.Model):
    isbn = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    publication_year = models.IntegerField(null=True, blank=True)
    publisher = models.CharField(max_length=255, blank=True)
    average_rating = models.FloatField(default=0.0)
    ratings_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-average_rating']

    def __str__(self):
        return f"{self.title} by {self.author}"

    def update_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            self.average_rating = sum(r.rating for r in reviews) / reviews.count()
            self.ratings_count = reviews.count()
            self.save()


class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    user_name = models.CharField(max_length=100)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user_name} rated '{self.book.title}' {self.rating}/5"

