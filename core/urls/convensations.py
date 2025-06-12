from rest_framework.routers import DefaultRouter
from core.views.conversation import ConversationViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')

urlpatterns = [
    path('', include(router.urls)),
]	
