from django.urls import include, path

from rest_framework.routers import DefaultRouter

from api.v0.notification_preferences.views.preferences import NotificationPreferencesView
from api.v0.users.views.logout import UserLogoutView
from api.v0.users.views.me import UserMeView
from api.v0.users.views.user import UserViewSet

router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')

urlpatterns = [
    path('me/', UserMeView.as_view(), name='user_me'),
    path('logout/', UserLogoutView.as_view(), name='user_logout'),
    path(
        'notification-preferences/',
        NotificationPreferencesView.as_view(),
        name='user_notification_preferences',
    ),
    path('', include(router.urls)),
]
