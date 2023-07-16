from django.contrib.auth.models import AbstractUser
from django.db import models
from shared.models import BaseModel


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
    photo = models.ImageField(upload_to="user_photos/", null=True, blank=True)

    def __str__(self):
        return self.username
