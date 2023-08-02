from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    AllowAny,
)

from django.shortcuts import render

from .models import Post, PostComment, PostLike, CommentLike
from shared.custom_pagination import CustomPagination
from .serializers import (
    PostSerializer,
    PostLikeSerializer,
    CommentSerializer,
    CommentLikeSerializer,
)


class PostListAPIView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [
        AllowAny,
    ]
    pagination_class = CustomPagination

    def get_queryset(self):
        return Post.objects.all()


class PostCreateView(generics.CreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
    ]

    def put(self, request, *args, **kwargs):
        post = self.get_object()
        serializer = self.serializer_class(post, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "success": True,
                "code": status.HTTP_200_OK,
                "message": "The post has been successfully updated.",
                "data": serializer.data,
            }
        )

    def delete(self, request, *args, **kwargs):
        post = self.get_object()
        post.delete()

        return Response(
            {
                "success": True,
                "code": status.HTTP_204_NO_CONTENT,
                "message": "The post has been successfully deleted.",
            }
        )


class PostCommentListView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [
        AllowAny,
    ]

    def get_queryset(self):
        post_id = self.kwargs["pk"]
        queryset = PostComment.objects.filter(post__id=post_id)
        return queryset


class PostCommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def perform_create(self, serializer):
        post_id = self.kwargs["pk"]
        serializer.save(author=self.request.user, post_id=post_id)


class CommentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
    ]
    queryset = PostComment.objects.all()
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentRetrieveView(generics.RetrieveAPIView):
    serializer_class = CommentSerializer
    permission_classes = [
        AllowAny,
    ]
    queryset = PostComment.objects.all()


class CommentLikeListView(generics.ListAPIView):
    serializer_class = CommentLikeSerializer
    permission_classes = [
        AllowAny,
    ]

    def get_queryset(self):
        comment_id = self.kwargs["pk"]
        return CommentLike.objects.filter(comment_id=comment_id)


class PostLikeListView(generics.ListAPIView):
    serializer_class = PostLikeSerializer
    permission_classes = [
        AllowAny,
    ]

    def get_queryset(self):
        post_id = self.kwargs["pk"]
        return PostLike.objects.filter(post_id=post_id)


# Post Like List with pagination
class LikeListView(generics.ListAPIView):
    serializer_class = PostLikeSerializer
    permission_classes = [
        AllowAny,
    ]
    queryset = PostLike.objects.all()
    pagination_class = CustomPagination


class PostLikeAPIView(APIView):
    def post(self, request, pk):
        try:
            post_like = PostLike.objects.get(author=self.request.user, post_id=pk)
            post_like.delete()
            serializer = PostLikeSerializer(post_like)
            data = {
                "success": True,
                "message": "The like has been successfully deleted.",
                "data": serializer.data,
            }

            return Response(data, status=status.HTTP_204_NO_CONTENT)
        except PostLike.DoesNotExist:
            post_like = PostLike.objects.create(
                author=self.request.user,
                post_id=pk,
            )
            serializer = PostLikeSerializer(post_like)
            data = {
                "success": True,
                "message": "The like has been successfully added.",
                "data": serializer.data,
            }

            return Response(data, status=status.HTTP_204_NO_CONTENT)


# class PostLikeAPIView(APIView):
#     def post(self, request, pk):
#         try:
#             post_like = PostLike.objects.create(
#                 author=self.request.user,
#                 post_id=pk,
#             )
#             serializer = PostLikeSerializer(post_like)
#             data = {
#                 "success": True,
#                 "message": "The like has been successfully added.",
#                 "data": serializer.data,
#             }
#             return Response(data, status=status.HTTP_201_CREATED)
#         except Exception as error:
#             data = {
#                 "success": False,
#                 "message": f"{str(error)}",
#                 "data": None,
#             }
#             return Response(data, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, pk):
#         try:
#             post_like = PostLike.objects.get(
#                 author=self.request.user,
#                 post_id=pk,
#             )
#             post_like.delete()
#             data = {
#                 "success": True,
#                 "message": "The like has been successfully deleted.",
#                 "data": None,
#             }
#             return Response(data, status=status.HTTP_204_NO_CONTENT)
#         except Exception as error:
#             data = {
#                 "success": False,
#                 "message": f"{str(error)}",
#                 "data": None,
#             }
#             return Response(data, status=status.HTTP_400_BAD_REQUEST)


class CommentLikeAPIView(APIView):
    def post(self, request, pk):
        try:
            comment_like = CommentLike.objects.get(
                author=self.request.user, comment_id=pk
            )
            comment_like.delete()
            serializer = CommentLikeSerializer(comment_like)
            data = {
                "success": True,
                "message": "The like has been successfully deleted.",
                "data": serializer.data,
            }

            return Response(data, status=status.HTTP_204_NO_CONTENT)
        except CommentLike.DoesNotExist:
            comment_like = CommentLike.objects.create(
                author=self.request.user,
                comment_id=pk,
            )
            serializer = CommentLikeSerializer(comment_like)
            data = {
                "success": True,
                "message": "The like has been successfully added.",
                "data": serializer.data,
            }

            return Response(data, status=status.HTTP_204_NO_CONTENT)
