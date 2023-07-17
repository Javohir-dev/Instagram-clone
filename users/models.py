from datetime import datetime, timedelta
import random
import uuid

from shared.models import BaseModel

from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import AbstractUser
from django.db import models

from rest_framework_simplejwt.tokens import RefreshToken


ORDINARY_USER, MANAGER, ADMIN = ("ordinary_user", "manager", "admin")
VIA_EMAIL, VIA_PHONE_NUMBER = ("via_email", "via_phone_number")
NEW, CODE_VERIFIES, DONE, PHOTO_STEP = ("new", "code_verified", "done", "photo_step")


class User(AbstractUser, BaseModel):
    USER_ROLES = (
        (ORDINARY_USER, ORDINARY_USER),
        (MANAGER, MANAGER),
        (ADMIN, ADMIN),
    )
    AUTH_TYPE_CHOICES = (
        (VIA_EMAIL, VIA_EMAIL),
        (VIA_PHONE_NUMBER, VIA_PHONE_NUMBER),
    )
    AUTH_STATUS = (
        (NEW, NEW),
        (CODE_VERIFIES, CODE_VERIFIES),
        (DONE, DONE),
        (PHOTO_STEP, PHOTO_STEP),
    )
    user_roles = models.CharField(
        max_length=31, choices=USER_ROLES, default=ORDINARY_USER
    )
    AUTH_TYPE = models.CharField(max_length=31, choices=AUTH_TYPE_CHOICES)
    AUTH_STATUS = models.CharField(max_length=31, choices=AUTH_STATUS, default=NEW)
    email = models.EmailField(null=True, unique=True)
    phone_number = models.CharField(max_length=14, null=True, unique=True)
    photo = models.ImageField(
        upload_to="user_photos/",
        null=True,
        blank=True,
        validators=FileExtensionValidator(
            allowed_extensions=["jpg", "jpeg", "png", "heic", "heif"]
        ),
    )

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def create_verify_code(self, verify_type):
        code = "".join([str(random.randint((0, 100) % 10)) for _ in range(4)])
        UserConfirmation.objects.create(
            user_id=self.id,
            verify_type=verify_type,
            code=code,
        )
        return code

    def check_username(self):
        if not self.username:
            tepm_username = f"instagram-{uuid.uuid4().__str__().split('-')[-1]}"
            while User.objects.filter(username=tepm_username):
                tepm_username = f"{tepm_username}{random.randint(0, 9)}"
            self.username = tepm_username

    def check_email(self):
        if self.email:
            normolize_email = self.email.lower()
            self.email = normolize_email

    def check_password(self):
        if not self.password:
            temp_password = f"password-{uuid.uuid4().__str__().split('-')[-1]}"
            self.password = temp_password

    def hashing_password(self):
        if not self.password.startswith("pbkdf2_sha256"):
            self.set_password(self.password)

    def token(self):
        refresh = RefreshToken.for_user(self)
        return {
            "access": str(refresh.access_token),
            "refresh_token": str(refresh),
        }

    def clean(self):
        self.check_username()
        self.check_email()
        self.check_password()
        self.hashing_password()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.clean
        super(User, self).save(*args, **kwargs)


PHONE_EXPIRE = 2
EMAIL_EXPIRE = 5


class UserConfirmation(BaseModel):
    TYPE_CHOICES = (
        (VIA_PHONE_NUMBER, VIA_PHONE_NUMBER),
        (VIA_EMAIL, VIA_EMAIL),
    )
    code = models.CharField(max_length=4)
    verify_type = models.CharField(max_length=31, choices=TYPE_CHOICES)
    user = models.ForeignKey("users.User", models.CASCADE, related_name="verify_codes")
    expiration_time = models.DateTimeField(null=True)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user.__str__())

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.verify_type == VIA_EMAIL:
                self.expiration_time = datetime.now() + timedelta(minutes=EMAIL_EXPIRE)
            else:
                self.expiration_time = datetime.now() + timedelta(minutes=PHONE_EXPIRE)
        super(UserConfirmation, self).save(*args, **kwargs)
