# from .views import *
from django.urls import path
from .views import (
    PostListAPIView,
    PostCreateView,
    PostRetrieveUpdateDestroy,
    PostCommentListView,
    PostCommentCreateView,
    CommentListCreateAPIView,
)


urlpatterns = [
    path("list/", PostListAPIView.as_view()),
    path("create/", PostCreateView.as_view()),
    path("<uuid:pk>/", PostRetrieveUpdateDestroy.as_view()),
    path("<uuid:pk>/comments/", PostCommentListView.as_view()),
    path("<uuid:pk>/comments/create/", PostCommentCreateView.as_view()),
    path("comments/", CommentListCreateAPIView.as_view()),
]
