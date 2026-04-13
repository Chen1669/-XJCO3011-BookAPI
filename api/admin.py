from django.contrib import admin
from .models import Book, Review


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'publication_year', 'average_rating', 'ratings_count']
    search_fields = ['title', 'author', 'isbn']
    list_filter = ['publication_year']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['book', 'user_name', 'rating', 'created_at']
    list_filter = ['rating']

