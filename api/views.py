from django.db.models import Avg, Count
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Book, Review
from .serializers import BookSerializer, BookListSerializer, ReviewSerializer


class BookViewSet(viewsets.ModelViewSet):
    """
    图书的完整 CRUD 接口。
    支持按书名、作者搜索，以及按出版年份过滤。
    """
    queryset = Book.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['publication_year', 'author']
    search_fields = ['title', 'author', 'isbn']
    ordering_fields = ['average_rating', 'ratings_count', 'publication_year', 'title']

    def get_serializer_class(self):
        if self.action == 'reviews':
            return ReviewSerializer
        if self.action == 'list':
            return BookListSerializer
        return BookSerializer



    @extend_schema(
        summary="获取某本书的所有评价",
        responses={200: ReviewSerializer(many=True)}
    )
    @action(detail=True, methods=['get', 'post'], url_path='reviews', serializer_class=ReviewSerializer)
    def reviews(self, request, pk=None):
        """获取某本书的所有评价，或为该书添加新评价"""
        book = self.get_object()

        if request.method == 'GET':
            reviews = book.reviews.all()
            serializer = ReviewSerializer(reviews, many=True)
            return Response(serializer.data)

        elif request.method == 'POST':
            serializer = ReviewSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(book=book)
                book.update_rating()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="获取评分最高的图书",
        parameters=[OpenApiParameter(name='limit', type=int, description='返回数量，默认10')]
    )
    @action(detail=False, methods=['get'], url_path='top-rated')
    def top_rated(self, request):
        """分析接口：返回评分最高的前 N 本书"""
        limit = int(request.query_params.get('limit', 10))
        books = Book.objects.filter(ratings_count__gt=0).order_by('-average_rating')[:limit]
        serializer = BookListSerializer(books, many=True)
        return Response({
            'count': len(serializer.data),
            'results': serializer.data
        })

    @extend_schema(summary="按作者统计图书数量和平均评分")
    @action(detail=False, methods=['get'], url_path='author-stats')
    def author_stats(self, request):
        """分析接口：按作者聚合统计出版书籍数量和平均评分"""
        stats = (
            Book.objects
            .values('author')
            .annotate(
                book_count=Count('id'),
                avg_rating=Avg('average_rating')
            )
            .order_by('-book_count')[:20]
        )
        return Response(list(stats))


class ReviewViewSet(viewsets.ModelViewSet):
    """
    评价的完整 CRUD 接口。
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def perform_create(self, serializer):
        review = serializer.save()
        review.book.update_rating()

    def perform_update(self, serializer):
        review = serializer.save()
        review.book.update_rating()

    def perform_destroy(self, instance):
        book = instance.book
        instance.delete()
        book.update_rating()
