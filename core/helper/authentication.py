# core/authentication.py
from rest_framework_simplejwt.authentication import JWTAuthentication

class JWTAuthenticationFromCookie(JWTAuthentication):
    def authenticate(self, request):
        # Lấy token từ header trước (chuẩn)
        header = self.get_header(request)
        if header is not None:
            return super().authenticate(request)
        # Nếu không có header, thử lấy từ cookie
        raw_token = request.COOKIES.get("access_token")
        if raw_token is not None:
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token
        return None
