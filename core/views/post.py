from django.db import transaction
from django.utils.dateparse import parse_date

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from core.models import Post, PostMedia
from core.serializers import PostSerializer
from core.helper.aws_s3 import upload_file_to_s3, delete_file_from_s3, generate_unique_filename
from core.helper.permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly, IsAuthenticatedOrReadOnly
from django.core.cache import cache

from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from django.core.cache import cache
import time
import json

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_serializer_context(self):
        return {'request': self.request}

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            post = serializer.save()
            files = request.FILES.getlist('media')
            for file_obj in files:
                key = generate_unique_filename(file_obj.name)
                success = upload_file_to_s3(file_obj, key)
                if not success:
                    transaction.set_rollback(True)
                    return Response({"error": "Upload file thất bại"}, status=status.HTTP_400_BAD_REQUEST)
                PostMedia.objects.create(post=post, media=key)
            return Response(self.get_serializer(post).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            post = serializer.save()

            # ✅ Lấy danh sách media cũ cần giữ lại từ client
            media_keep_raw = request.data.get('media_keep', '[]')
            try:
                media_keep_ids = json.loads(media_keep_raw)
            except json.JSONDecodeError:
                media_keep_ids = []

            # ✅ Xoá media không còn giữ lại
            old_medias = PostMedia.objects.filter(post=post)
            for media in old_medias:
                if media.id not in media_keep_ids:
                    if media.media:
                        delete_file_from_s3(media.media.name)
                    media.delete()

            # ✅ Upload media mới nếu có
            files = request.FILES.getlist('media')
            for file_obj in files:
                key = generate_unique_filename(file_obj.name)
                success = upload_file_to_s3(file_obj, key)
                if not success:
                    transaction.set_rollback(True)
                    return Response({"error": "Upload file thất bại"}, status=status.HTTP_400_BAD_REQUEST)
                PostMedia.objects.create(post=post, media=key)

            return Response(self.get_serializer(post).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        medias = PostMedia.objects.filter(post=instance)
        for media in medias:
            if media.media:
                delete_file_from_s3(media.media.name)
            media.delete()
        self.perform_destroy(instance)
        return Response({"content": "Xóa thành công"}, status=status.HTTP_200_OK)
    
    def get_queryset(self):
        queryset = Post.objects.all()
        sort_param = self.request.query_params.get('sort')
        # Ví dụ client gửi sort=-created_at,like_count
        if sort_param:
            fields = []
            for f in sort_param.split(','):
                f = f.strip()
                if f.lstrip('-') in ['created_at', 'like_count', 'comment_count']:  # chỉ cho phép sắp xếp các trường này
                    fields.append(f)
            if fields:
                queryset = queryset.order_by(*fields)
        else:
            queryset = queryset.order_by('-created_at')
        return queryset


    @action(detail=False, methods=['get'], url_path='filter')
    def filter_by_date(self, request):
        from_date = request.query_params.get('from')
        to_date = request.query_params.get('to')

        if not from_date or not to_date:
            return Response({"error": "Thiếu from hoặc to"}, status=status.HTTP_400_BAD_REQUEST)

        from_date = parse_date(from_date)
        to_date = parse_date(to_date)

        if not from_date or not to_date:
            return Response({"error": "Sai định dạng ngày (YYYY-MM-DD)"}, status=status.HTTP_400_BAD_REQUEST)

        posts = Post.objects.filter(created_at__date__gte=from_date, created_at__date__lte=to_date)
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='hot')
    def get_hot_posts(self, request):
        CACHE_KEY = 'hot_posts'
        CACHE_TIMEOUT = 60 * 5

        hot_posts = cache.get(CACHE_KEY)
        if hot_posts is not None:
            print("🔥 Lấy hot posts từ cache!")
            return Response(hot_posts)

        print("⚡ Truy vấn DB và set cache!")
        posts = Post.objects.order_by('number_emotion')[:10]
        serializer = self.get_serializer(posts, many=True)
        hot_posts = serializer.data
        cache.set(CACHE_KEY, hot_posts, CACHE_TIMEOUT)
        return Response(hot_posts)


    @action(detail=False, methods=['get'], url_path='search')
    def search_posts(self, request):
        query = request.GET.get('q', '').strip()
        page_number = request.GET.get('page', '1')
        posts = Post.objects.all()

        if query:
            posts = posts.filter(
                Q(content__icontains=query)
            ).order_by('-created_at')

        paginator = PageNumberPagination()
        paginator.page_size = 10
        page = paginator.paginate_queryset(posts, request)
        serializer = self.get_serializer(page, many=True)
        search_results = serializer.data

        # 👇 Gợi ý bài viết thêm nếu kết quả ít hoặc không có
        if len(search_results) < 5:
            suggested_posts = Post.objects.exclude(id__in=[p['id'] for p in search_results]).order_by('-number_emotion')[:3]
            suggested_serializer = self.get_serializer(suggested_posts, many=True)

            return Response({
                "results": search_results,
                "suggested": suggested_serializer.data
            })

        return paginator.get_paginated_response(search_results)
