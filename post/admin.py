from django.contrib import admin
from .models import Post, PostLike, PostComment, CommentLike


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("author", "id", "caption", "created_time")
    search_fields = ("id", "author__username", "caption")


@admin.register(PostComment)
class PostCommentAdmin(admin.ModelAdmin):
    list_display = ("author", "id", "post", "created_time")
    search_fields = ("id", "author__username", "comment")


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ("author", "id", "post", "created_time")
    search_fields = ("id", "author__username")


@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ("author", "id", "comment", "created_time")
    search_fields = ("id", "author__username")


# admin.site.register(Post, PostAdmin)
