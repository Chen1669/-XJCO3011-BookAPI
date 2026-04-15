from django.db.models import Avg, Count, Min, Max
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
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['publication_year', 'author']
    search_fields = ['title', 'author', 'isbn']
    ordering_fields = ['average_rating', 'ratings_count', 'publication_year', 'title']

    def get_queryset(self):
        queryset = Book.objects.all()
        min_rating = self.request.query_params.get('min_rating')
        max_rating = self.request.query_params.get('max_rating')
        if min_rating is not None:
            queryset = queryset.filter(average_rating__gte=float(min_rating))
        if max_rating is not None:
            queryset = queryset.filter(average_rating__lte=float(max_rating))
        return queryset




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

    @extend_schema(summary="获取数据库整体统计摘要")
    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        """分析接口：返回图书数据库的整体统计摘要"""
        total_books = Book.objects.count()
        total_reviews = Review.objects.count()
        rating_stats = Book.objects.filter(ratings_count__gt=0).aggregate(
            avg=Avg('average_rating'),
            highest=Max('average_rating'),
            lowest=Min('average_rating')
        )
        return Response({
            'total_books': total_books,
            'total_reviews': total_reviews,
            'average_rating_across_all_books': round(rating_stats['avg'] or 0, 2),
            'highest_rated_book_score': rating_stats['highest'],
            'lowest_rated_book_score': rating_stats['lowest'],
        })
    
    @extend_schema(summary="获取相似书籍推荐（同作者或同年代）")
    @action(detail=True, methods=['get'], url_path='similar')
    def similar(self, request, pk=None):
        """推荐接口：优先推荐同一作者的其他书籍，不足时补充同年代高分书籍"""
        book = self.get_object()
        # 第一层：同作者的其他书籍
        same_author = Book.objects.filter(
            author=book.author
        ).exclude(id=book.id).order_by('-average_rating')[:5]

        results = list(same_author)

        # 第二层：若同作者不足3本，补充同年代（±5年）高分书籍
        if len(results) < 3 and book.publication_year:
            year_range = Book.objects.filter(
                publication_year__gte=book.publication_year - 5,
                publication_year__lte=book.publication_year + 5,
            ).exclude(id=book.id).exclude(
                id__in=[b.id for b in results]
            ).order_by('-average_rating')[:5 - len(results)]
            results += list(year_range)

        serializer = BookListSerializer(results, many=True)
        return Response({
            'book_id': book.id,
            'title': book.title,
            'similar_books': serializer.data
        })




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
