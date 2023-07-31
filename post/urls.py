# from .views import *
from django.urls import path
from .views import PostListAPIView, PostCreateView, PostRetrieveUpdateDestroy


urlpatterns = [
    path("posts/", PostListAPIView.as_view()),
    path("posts/create/", PostCreateView.as_view()),
    path("posts/<uuid:pk>/", PostRetrieveUpdateDestroy.as_view()),
]
