from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Cho phép chủ sở hữu sửa hoặc xóa, người khác chỉ đọc.
    """
    def has_object_permission(self, request, view, obj):
        # Cho phép các request đọc an toàn (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
        # Cho phép nếu là chủ sở hữu bài viết
        return obj.user == request.user

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Cho phép admin thao tác tất cả, người khác chỉ đọc.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    Cho phép tất cả xem, chỉ người đăng nhập mới thao tác được.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated
