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

        try:
            user = User.objects.get(email=identifier)
        except User.DoesNotExist:
            try:
                user = User.objects.get(username=identifier)
            except User.DoesNotExist:
                return Response({"detail": "Tài khoản không tồn tại"}, status=401)

        if not user.check_password(password):
            return Response({"detail": "Sai mật khẩu"}, status=401)

        if not user.is_active:
            return Response({"detail": "Tài khoản đã bị khoá"}, status=403)

        # Thu hồi token cũ (blacklist)
        from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
        for token in OutstandingToken.objects.filter(user=user):
            try:
                BlacklistedToken.objects.get_or_create(token=token)
            except:
                pass

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response = Response({
            "refresh": refresh_token,
            "access": access_token,
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username
            }
        })

        response.set_cookie(
            key='access_token',
            value=access_token,
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=300
        )

        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=86400
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
    def post(self, request, *args, **kwargs):
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