from rest_framework import serializers
from .models import Book, Review


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'user_name', 'rating', 'comment', 'created_at']
        read_only_fields = ['created_at']


class BookSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Book
        fields = [
            'id', 'isbn', 'title', 'author',
            'publication_year', 'publisher',
            'average_rating', 'ratings_count',
            'reviews', 'created_at', 'updated_at'
        ]
        read_only_fields = ['average_rating', 'ratings_count', 'created_at', 'updated_at']


class BookListSerializer(serializers.ModelSerializer):
    """用于列表页的轻量序列化器（不包含评价详情）"""
    class Meta:
        model = Book
        fields = ['id', 'isbn', 'title', 'author', 'publication_year', 'average_rating', 'ratings_count']
