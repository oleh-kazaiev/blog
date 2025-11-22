from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin for the custom User model with email instead of username."""

    # Non-editable timestamps should be read-only in the admin form
    readonly_fields = ('last_login', 'date_joined')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            _('Personal info'),
            {'fields': ('first_name', 'last_name', 'bio', 'profile_picture', 'website')},
        ),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'is_admin',
                    'groups',
                    'user_permissions',
                )
            },
        ),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'password1', 'password2', 'first_name', 'last_name'),
            },
        ),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_admin')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    list_filter = ('is_admin', 'is_staff', 'is_superuser', 'is_active')
