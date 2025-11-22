from django.db import models
from django.utils import timezone

from rest_framework.permissions import BasePermission

from payments.models import Subscription


class IsAdminUserFlag(BasePermission):
    """Allows access only to authenticated users with is_admin flag (or staff)."""

    def has_permission(self, request, view):
        """Check if user has admin flag or is staff."""
        user = getattr(request, 'user', None)
        return bool(user and user.is_authenticated and (getattr(user, 'is_admin', False) or user.is_staff))


class IsAdminOrActiveSubscriber(BasePermission):
    """Allows access to admins/staff or users with an active subscription."""

    def has_permission(self, request, view):
        """Return True when user is admin/staff or has an active subscription."""
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return False
        if getattr(user, 'is_admin', False) or user.is_staff:
            return True

        now = timezone.now()
        return Subscription.objects.filter(
            user=user,
            status='active',
        ).filter(
            models.Q(valid_until__isnull=True) | models.Q(valid_until__gte=now)
        ).exists()
