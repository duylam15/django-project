from rest_framework import viewsets
from core.models import Notification
from core.serializers import NotificationSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all().order_by('-created_at')
    serializer_class = NotificationSerializer
    pagination_class = None  # ← Tắt phân trang chỉ ở view này

    def get_queryset(self):
        # Chỉ lấy thông báo của user hiện tại
        return Notification.objects.filter(receiver=self.request.user).order_by('-created_at')
