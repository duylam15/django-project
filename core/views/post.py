from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status
from core.models import Post
from core.serializers import PostSerializer
from django.utils.dateparse import parse_date
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    parser_classes = [MultiPartParser, FormParser]  

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            post = serializer.save()
            print("post.media.name:", post.media.name)
            print("post.media.url:", post.media.url)
            return Response({
                'id': post.id,
                'content': post.content,
                'media_url': post.media.url if post.media else None,
                'created_at': post.created_at,
                'type_post': post.type_post,
                'visibility': post.visibility,
                'user': post.user.id
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
