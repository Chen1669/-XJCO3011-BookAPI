import csv
import os
from django.core.management.base import BaseCommand
from api.models import Book


class Command(BaseCommand):
    help = 'Import books from a CSV file into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='data/books.csv',
            help='Path to the CSV file'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=500,
            help='Maximum number of books to import'
        )

    def handle(self, *args, **options):
        filepath = options['file']
        limit = options['limit']

        if not os.path.exists(filepath):
            self.stderr.write(self.style.ERROR(f'File not found: {filepath}'))
            return

        imported = 0
        skipped = 0

        with open(filepath, encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if imported >= limit:
                    break
                try:
                    # 清理数据
                    isbn = row.get('isbn', '').strip()
                    title = row.get('title', '').strip()[:255]
                    author = row.get('authors', row.get('author', '')).strip()[:255]
                    publisher = row.get('publisher', '').strip()[:255]

                    # 处理出版年份
                    year_str = row.get('original_publication_year',
                                row.get('publication_year',
                                row.get('  num_pages', ''))).strip()
                    try:
                        year = int(float(year_str)) if year_str else None
                    except (ValueError, TypeError):
                        year = None

                    # 处理评分
                    try:
                        avg_rating = float(row.get('average_rating', 0) or 0)
                        ratings_count = int(row.get('ratings_count', 0) or 0)
                    except (ValueError, TypeError):
                        avg_rating = 0.0
                        ratings_count = 0

                    if not isbn or not title:
                        skipped += 1
                        continue

                    Book.objects.get_or_create(
                        isbn=isbn,
                        defaults={
                            'title': title,
                            'author': author,
                            'publication_year': year,
                            'publisher': publisher,
                            'average_rating': avg_rating,
                            'ratings_count': ratings_count,
                        }
                    )
                    imported += 1

                    if imported % 100 == 0:
                        self.stdout.write(f'  Imported {imported} books...')

                except Exception as e:
                    skipped += 1
                    continue

        self.stdout.write(
            self.style.SUCCESS(
                f'\nDone! Imported: {imported} books, Skipped: {skipped} rows.'
            )
        )
