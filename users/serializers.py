from rest_framework.fields import empty

from shared.utility import chack_email_or_phone
from .models import (
    User,
    UserConfirmation,
    VIA_EMAIL,
    VIA_PHONE_NUMBER,
    CODE_VERIFIES,
    NEW,
    DONE,
    PHOTO_STEP,
)
from rest_framework import exceptions
from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class SignUpSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    def __init__(self, *args, **kwargs):
        super(SignUpSerializer, self).__init__(*args, **kwargs)
        self.fields["email_phone_number"] = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ("id", "auth_type", "auth_status")
        extra_kwargs = {
            "auth_type": {"read_only": True, "required": False},
            "auth_status": {"read_only": True, "required": False},
        }

    def create(self, validated_data):
        user = super(SignUpSerializer, self).create(validated_data)
        print(user)
        if user.auth_type == VIA_EMAIL:
            code = user.create_verify_code(VIA_EMAIL)
            print(code)
            # send_mail(user.email, code)
        elif user.auth_type == VIA_PHONE_NUMBER:
            code = user.create_verify_code(VIA_PHONE_NUMBER)
            # send_phone_code(user.phone_number, code)
        user.save()

    def validate(self, data):
        super(SignUpSerializer, self).validate(data)
        data = self.auth_validate(data)

        return data

    @staticmethod
    def auth_validate(data):
        # print(data)
        user_input = str(data.get("email_phone_number")).lower()
        input_type = chack_email_or_phone(user_input)
        print("user_input", user_input)
        print("input_type", input_type)
        if input_type == "email":
            data = {
                "email": user_input,
                "auth_type": VIA_EMAIL,
            }
        elif input_type == "phone":
            data = {
                "phone_number": user_input,
                "auth_type": VIA_PHONE_NUMBER,
            }
        else:
            data = {
                "success": False,
                "message": "You must enter an email or phone number.",
            }
            raise ValidationError(data)
        # print("===========================================")
        # print("===========================================")
        # print("data: ", data)
        # print("===========================================")
        # print("===========================================")

        return data

    def validate_email_phone_number(self):
        value = value.lower()
        # to do!

        return value
