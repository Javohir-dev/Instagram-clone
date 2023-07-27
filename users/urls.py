from .serializers import SignUpSerializer
from .views import (
    CreateUserView,
    VerifyAPIView,
    GetNewVerification,
    ChangeUserInformationView,
    ChangeUserPhotoView,
    LogInView,
    LogInRefreshView,
    LogOutView,
    ForgotPasswordView,
    ResetPasswordView,
)
from django.urls import path


urlpatterns = [
    path("login/", LogInView.as_view()),
    path("login/refresh/", LogInRefreshView.as_view()),
    path("logout/", LogOutView.as_view()),
    path("signup/", CreateUserView.as_view()),
    path("verify/", VerifyAPIView.as_view()),
    path("new-verify/", GetNewVerification.as_view()),
    path("change-info/", ChangeUserInformationView.as_view()),
    path("change-user-photo/", ChangeUserPhotoView.as_view()),
    path("forgot-password/", ForgotPasswordView.as_view()),
    path("reset-password/", ResetPasswordView.as_view()),
]
