from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from core.serializers.user import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework import status
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        serializer.save(is_active=True)



class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        identifier = request.data.get("email") or request.data.get("username")
        password = request.data.get("password")

        # Check missing fields
        if not identifier or not password:
            return Response(
                {
                    "status": 400,
                    "code": "missing_field",
                    "detail": "Vui lòng nhập tài khoản và mật khẩu."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check user existence
        try:
            user = User.objects.get(email=identifier)
        except User.DoesNotExist:
            try:
                user = User.objects.get(username=identifier)
            except User.DoesNotExist:
                return Response(
                    {
                        "status": 401,
                        "code": "user_not_found",
                        "detail": "Tài khoản không tồn tạii."
                    },
                    status=status.HTTP_401_UNAUTHORIZED
                )

        # Check password
        if not user.check_password(password):
            return Response(
                {
                    "status": 401,
                    "code": "invalid_password",
                    "detail": "Sai mật khẩu."
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Check active status
        if not user.is_active:
            return Response(
                {
                    "status": 403,
                    "code": "account_locked",
                    "detail": "Tài khoản đã bị khoá."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # Blacklist old tokens (logout all sessions)
        for token in OutstandingToken.objects.filter(user=user):
            try:
                BlacklistedToken.objects.get_or_create(token=token)
            except Exception:
                pass

        # Issue new tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        user_data = UserSerializer(user).data

        response = Response(
            {
                "status": 200,
                "code": "login_success",
                "detail": "Đăng nhập thành công.",
                "refresh": refresh_token,
                "access": access_token,
                "user": user_data,
            },
            status=status.HTTP_200_OK
        )

        # Set cookies
        response.set_cookie(
            key='access_token',
            value=access_token,
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=300  # 5 phút
        )
        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=86400  # 1 ngày
        )

        return response
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = (
            request.data.get("refresh") or
            request.COOKIES.get("refresh_token")
        )

        if not refresh_token:
            return Response({"detail": "Không tìm thấy refresh token."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response({"detail": "Token không hợp lệ hoặc đã bị thu hồi."}, status=status.HTTP_400_BAD_REQUEST)

        response = Response({"detail": "Đăng xuất thành công."}, status=status.HTTP_205_RESET_CONTENT)
        response.set_cookie(
            key='access_token',
            value="",
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=300
        )

        response.set_cookie(
            key='refresh_token',
            value="",
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=86400
        )
        return response

class RefreshTokenView(TokenRefreshView):
    def get(self, request, *args, **kwargs):
        # ✅ Lấy refresh token từ cookie
        refresh_token = request.COOKIES.get('refresh_token')
        if refresh_token is None:
            return Response({'detail': 'Không tìm thấy refresh token trong cookie'}, status=status.HTTP_401_UNAUTHORIZED)

        request.data['refresh'] = refresh_token  # Gắn vào request.data để TokenRefreshView xử lý

        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            access_token = response.data.get('access')
            new_refresh_token = response.data.get('refresh', refresh_token)

            # ✅ Set lại cookie mới
            response.set_cookie(
                'access_token',
                access_token,
                httponly=True,
                samesite='Lax',
                max_age=300  # 5 phút
            )

            response.set_cookie(
                'refresh_token',
                new_refresh_token,
                httponly=True,
                samesite='Lax',
                max_age=86400  # 1 ngày
            )

        return response