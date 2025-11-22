from django import forms
from django.contrib import admin

from django_ckeditor_5.widgets import CKEditor5Widget

from .models import Category, Comment, Post, PostPurchase, PostReaction


class PostAdminForm(forms.ModelForm):
    """Admin form for Post with CKEditor widget."""

    content = forms.CharField(widget=CKEditor5Widget(config_name='extends'))

    class Meta:
        """Meta configuration."""

        model = Post
        fields = [
            'title',
            'slug',
            'excerpt',
            'content',
            'featured_image',
            'author',
            'category',
            'is_published',
            'published_at',
            'is_paid',
            'price_cents',
        ]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface for Category model."""

    list_display = ('name', 'slug')
    search_fields = ('name',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Admin interface for Post model."""

    form = PostAdminForm
    list_display = ('title', 'author', 'category', 'is_published', 'is_paid', 'published_at')
    list_filter = ('is_published', 'is_paid', 'category')
    search_fields = ('title', 'excerpt', 'content')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin interface for Comment model."""

    list_display = ('post', 'author', 'is_approved', 'created_at')
    list_filter = ('is_approved',)
    search_fields = ('author__email', 'author__first_name', 'author__last_name', 'body')


@admin.register(PostReaction)
class PostReactionAdmin(admin.ModelAdmin):
    """Admin interface for PostReaction model."""

    list_display = ('post', 'user', 'reaction_type', 'created_at')
    list_filter = ('reaction_type',)


@admin.register(PostPurchase)
class PostPurchaseAdmin(admin.ModelAdmin):
    """Admin interface for PostPurchase model."""

    list_display = ('post', 'user', 'status', 'payment', 'access_granted_at', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('post__title', 'user__email')
