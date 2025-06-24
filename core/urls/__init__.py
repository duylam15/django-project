from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import (
    UserViewSet,
    PostViewSet,
    CommentViewSet,
    MessageViewSet,
    NotificationViewSet,
    FriendViewSet,
    PostEmotionViewSet,
    ConversationViewSet,
    ConversationMemberViewSet,
    FriendRequestViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'posts', PostViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'messages', MessageViewSet)
router.register(r'notifications', NotificationViewSet)
router.register(r'friends', FriendViewSet)
router.register(r'post-emotions', PostEmotionViewSet)
router.register(r'conversations', ConversationViewSet)
router.register(r'conversation-members', ConversationMemberViewSet)
router.register(r'friend-requests', FriendRequestViewSet, basename='friend-request')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('core.urls.auth')),
]
