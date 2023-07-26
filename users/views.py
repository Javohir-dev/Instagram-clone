from django.utils.datetime_safe import datetime
from django.shortcuts import render

from rest_framework.exceptions import ValidationError
from rest_framework import permissions
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import permission_classes

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from shared.utility import send_email

from .serializers import (
    check_email_or_phone,
    ChangeUserPhotoSerializer,
    SignUpSerializer,
    ChangeUserInformation,
    LoginSerializer,
    LoginRefreshSerializer,
    LogOutSerializer,
    ForgotPasswordSerializer,
)
from .models import (
    VIA_EMAIL,
    CODE_VERIFIES,
    NEW,
    VIA_PHONE_NUMBER,
    User,
)


class CreateUserView(CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = SignUpSerializer


class VerifyAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        code = self.request.data.get("code")

        self.check_verify(user, code)
        return Response(
            data={
                "success": True,
                "auth_status": user.auth_status,
                "access": user.token()["access"],
                "refresh": user.token()["refresh_token"],
            }
        )

    @staticmethod
    def check_verify(user, code):
        verifies = user.verify_codes.filter(
            expiration_time__gte=datetime.now(), code=code, is_confirmed=False
        )
        print(verifies)
        if not verifies.exists():
            data = {"message": "Bu kod xato yoki eskirgan!"}
            raise ValidationError(data)
        else:
            verifies.update(is_confirmed=True)
        if user.auth_status == NEW:
            user.auth_status = CODE_VERIFIES
            user.save()
        return True


class GetNewVerification(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        self.check_verification(user)
        if user.auth_type == VIA_EMAIL:
            code = user.create_verify_code(VIA_EMAIL)
            send_email(user.email, code)
        elif user.auth_type == VIA_PHONE_NUMBER:
            code = user.create_verify_code(VIA_PHONE_NUMBER)
            send_email(user.phone_number, code)
        else:
            data = {
                "message": "Email yoki Telefon raqamingiz xato yozilgan bo'lishi mumkin."
            }
            raise ValidationError(data)

        return Response(
            {
                "success": True,
                "message": "Tasdiqlash kodingiz qayta yuborildi.",
            }
        )

    @staticmethod
    def check_verification(user):
        verifies = user.verify_codes.filter(
            expiration_time__gte=datetime.now(), is_confirmed=False
        )
        if verifies.exists():
            data = {"message": "Sizda kod mavjud, biroz kuting..."}
            raise ValidationError(data)


class ChangeUserInformationView(UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangeUserInformation
    http_method_names = ["patch", "put"]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        super(ChangeUserInformationView, self).update(request, *args, **kwargs)
        data = {
            "success": True,
            "message": "User updated successfully",
            "auth_status": self.request.user.auth_status,
        }

        return Response(data, status=200)

    def partial_update(self, request, *args, **kwargs):
        super(ChangeUserInformationView, self).partial_update(request, *args, **kwargs)
        data = {
            "success": True,
            "message": "User updated successfully",
            "auth_status": self.request.user.auth_status,
        }

        return Response(data, status=200)


class ChangeUserPhotoView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def put(self, request, *args, **kwargs):
        serializer = ChangeUserPhotoSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            serializer.update(user, serializer.validated_data)
            return Response(
                {"message": "Rasm muvaffaqiyatli o'zgartirildi"}, status=200
            )
        return Response(serializer.errors, status=400)


class LogInView(TokenObtainPairView):
    serializer_class = LoginSerializer


class LogInRefreshView(TokenRefreshView):
    serializer_class = LoginRefreshSerializer


class LogOutView(APIView):
    serializer_class = LogOutSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refresh_token = self.request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            data = {
                "success": True,
                "message": "You have successfully logged out.",
            }

            return Response(data, status=205)
        except TokenError:
            return Response(status=400)


class ForgotPasswordView(APIView):
    serializer_class = ForgotPasswordSerializer
    permission_classes = [
        AllowAny,
    ]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        email_or_phone = serializer.validated_data.get("email_or_phone")
        user = serializer.validated_data.get("user")
        if check_email_or_phone(email_or_phone) == "phone":
            code = user.create_verify_code(VIA_PHONE_NUMBER)
            send_email(email_or_phone, code)
        elif check_email_or_phone(email_or_phone) == "email":
            code = user.create_verify_code(VIA_EMAIL)
            send_email(email_or_phone, code)

        return Response(
            {
                "success": True,
                "message": "Verify's code has been successfully sent.",
                "access": user.token()["access"],
                "refresh": user.token()["refresh_token"],
                "user_status": user.auth_status,
            },
            status=200,
        )
