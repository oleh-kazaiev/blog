from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from .category import Category


class Post(models.Model):
    """Post model for blog articles."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    excerpt = models.CharField(max_length=400, blank=True)
    content = models.TextField()
    featured_image = models.ImageField(upload_to='posts/', blank=True, null=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='posts', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, related_name='posts', on_delete=models.SET_NULL, null=True, blank=True)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_paid = models.BooleanField(default=False, db_index=True)
    price_cents = models.PositiveIntegerField(default=0)

    class Meta:
        """Meta configuration."""

        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['is_published', '-published_at', '-created_at'], name='post_pub_date_idx'),
            models.Index(fields=['category', 'is_published', '-published_at'], name='post_cat_pub_idx'),
            models.Index(fields=['author', 'is_published'], name='post_author_idx'),
        ]

    def __str__(self):
        """Return string representation."""
        return self.title

    def save(self, *args, **kwargs):
        """Save post with auto-generated slug and published_at."""
        if not self.slug:
            self.slug = slugify(self.title)
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()

        # Auto-set is_paid based on price_cents
        if self.price_cents > 0:
            self.is_paid = True
        elif not self.is_paid:
            # Only reset price if explicitly marked as not paid
            self.price_cents = 0

        super().save(*args, **kwargs)

    @property
    def likes_count(self):
        """Get the number of likes for this post."""
        return self.reactions.filter(reaction_type='like').count()

    @property
    def dislikes_count(self):
        """Get the number of dislikes for this post."""
        return self.reactions.filter(reaction_type='dislike').count()

    def get_user_reaction(self, user):
        """Get the reaction type for a specific user."""
        if not user or not user.is_authenticated:
            return None
        reaction = self.reactions.filter(user=user).first()
        return reaction.reaction_type if reaction else None

    def user_has_access(self, user) -> bool:
        """Check if user has access to this post via subscription or purchase."""
        if not self.is_paid:
            return True
        if not user or not getattr(user, 'is_authenticated', False):
            return False
        from payments.models import Subscription  # local import to avoid circular dependency

        now = timezone.now()
        has_active_subscription = Subscription.objects.filter(
            user=user,
            status='active',
        ).filter(
            models.Q(valid_until__isnull=True) | models.Q(valid_until__gte=now)
        ).exists()
        if has_active_subscription:
            return True
        return self.purchases.filter(user=user, status='succeeded').exists()
