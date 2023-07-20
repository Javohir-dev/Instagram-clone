from .serializers import SignUpSerializer
from .views import CreateUserView, VerifyAPIView, GetNewVerification
from django.urls import path


urlpatterns = [
    path("signup/", CreateUserView.as_view()),
    path("verify/", VerifyAPIView.as_view()),
    path("new-verify/", GetNewVerification.as_view()),
]
