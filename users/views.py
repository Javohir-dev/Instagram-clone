from django.utils.datetime_safe import datetime
from django.shortcuts import render

from rest_framework.exceptions import ValidationError
from rest_framework import permissions, status
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import permission_classes

from shared.utility import send_email

from .serializers import SignUpSerializer
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
