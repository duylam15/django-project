from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db import transaction
from rest_framework.parsers import MultiPartParser, FormParser

from core.models import User
from core.serializers import UserSerializer, UserSearchSerializer
from core.helper.permissions import IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly

from rest_framework.decorators import action
from core.helper.aws_s3 import upload_file_to_s3, delete_file_from_s3, generate_unique_filename
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from django.core.cache import cache
import time

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    # def get_permissions(self):
    #     if self.action in ['list', 'retrieve']:
    #         return [AllowAny()]
    #     return [IsAuthenticated()]

    def get_permissions(self):
        return [AllowAny()]

    @action(detail=True, methods=['post'], url_path='upload-avatar')
    def upload_avatar(self, request, pk=None):
        user = self.get_object()

        if user != request.user:
            return Response({"error": "Bạn không có quyền chỉnh sửa avatar người khác"}, status=status.HTTP_403_FORBIDDEN)

        avatar_file = request.FILES.get('avatar_file')
        if not avatar_file:
            return Response({"error": "Không có file được gửi lên"}, status=status.HTTP_400_BAD_REQUEST)

        # Xóa avatar cũ nếu có
        if user.avatar:
            delete_file_from_s3(user.avatar)

        # Upload file mới
        key = generate_unique_filename(avatar_file.name)
        success = upload_file_to_s3(avatar_file, key)
        if not success:
            return Response({"error": "Upload thất bại"}, status=status.HTTP_400_BAD_REQUEST)

        user.avatar = key
        user.save()

        return Response({"message": "Cập nhật avatar thành công", "avatar_key": key}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'], url_path='delete-avatar')
    def delete_avatar(self, request, pk=None):
        user = self.get_object()

        if user != request.user:
            return Response({"error": "Bạn không có quyền xoá avatar người khác"}, status=status.HTTP_403_FORBIDDEN)

        if user.avatar:
            delete_file_from_s3(user.avatar)
            user.avatar = None
            user.save()
            return Response({"message": "Xoá avatar thành công"}, status=status.HTTP_200_OK)
        return Response({"error": "Người dùng chưa có avatar"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        query = request.GET.get('q', '').strip()
        limit = int(request.GET.get('limit', 5))  # nhận limit động

        CACHE_KEY = f"user_search:{query}:limit:{limit}"
        CACHE_TIMEOUT = 60 * 10

        cached_data = cache.get(CACHE_KEY)
        if cached_data:
            return Response(cached_data)

        users = User.objects.values("id", "username", "email", "avatar")
        if query:
            users = users.filter(
                Q(username__icontains=query) |
                Q(email__icontains=query) |
                Q(phone_number__icontains=query)
            )

        users = users[:limit]  # ✅ sửa chỗ này

        serializer = UserSearchSerializer(users, many=True)
        response_data = {"results": serializer.data}

        cache.set(CACHE_KEY, response_data, CACHE_TIMEOUT)
        return Response(response_data)
