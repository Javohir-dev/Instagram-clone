from .serializers import SignUpSerializer
from .views import CreateUserView, VerifyAPIView
from django.urls import path


urlpatterns = [
    path("signup/", CreateUserView.as_view()),
    path("verify/", VerifyAPIView.as_view()),
]
