from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status
from core.models import Post
from core.models import PostMedia
from core.serializers import PostSerializer
from django.utils.dateparse import parse_date
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
import boto3
import io
import boto3
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from core.models import Post
from core.serializers import PostSerializer

import uuid
import os

def generate_unique_filename(filename):
    ext = os.path.splitext(filename)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    return f"post_media/{filename}-{unique_name}"

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            post = serializer.save()  # Tạo post trước để có id

            files = request.FILES.getlist('media')  # Hỗ trợ nhiều file upload

            if files:
                s3_client = boto3.client(
                    's3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_S3_REGION_NAME
                )

                for file_obj in files:
                    key = generate_unique_filename(file_obj.name)

                    file_content = io.BytesIO(file_obj.read())
                    file_content.seek(0)

                    s3_client.upload_fileobj(file_content, settings.AWS_STORAGE_BUCKET_NAME, key)

                    # Tạo bản ghi PostMedia liên kết post
                    PostMedia.objects.create(post=post, media=key)

            serializer = self.get_serializer(post)  # serialize lại post để trả về
            data = serializer.data
            return Response(data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def update(self, request, *args, **kwargs):
            partial = kwargs.pop('partial', False)
            instance = self.get_object()

            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            if serializer.is_valid():
                post = serializer.save()

                files = request.FILES.getlist('media')

                s3_client = boto3.client(
                    's3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_S3_REGION_NAME
                )

                if files:
                    # Nếu muốn xóa ảnh cũ khi update, xóa các PostMedia cũ đi:
                    old_medias = PostMedia.objects.filter(post=post)
                    for media in old_medias:
                        if media.media:
                            key = media.media.name
                            try:
                                s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)
                            except Exception as e:
                                print(f"Lỗi xóa file cũ trên S3: {e}")
                        media.delete()

                    # Upload ảnh mới
                    for file_obj in files:
                        key = generate_unique_filename(file_obj.name)
                        file_content = io.BytesIO(file_obj.read())
                        file_content.seek(0)
                        s3_client.upload_fileobj(file_content, settings.AWS_STORAGE_BUCKET_NAME, key)

                        # Tạo record mới trong PostMedia
                        PostMedia.objects.create(post=post, media=key)

                return Response(self.get_serializer(post).data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )

        # Xóa tất cả file media liên quan trong PostMedia
        from core.models import PostMedia
        medias = PostMedia.objects.filter(post=instance)

        for media in medias:
            if media.media:
                key = media.media.name  # đường dẫn file trên bucket
                try:
                    s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)
                except Exception as e:
                    print(f"Lỗi khi xóa file S3: {e}")
            media.delete()

        # Xóa post
        self.perform_destroy(instance)
        return Response({"content": "Xóa thành công"}, status=status.HTTP_200_OK)
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

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
