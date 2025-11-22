from django.urls import path

from api.v0.notification_preferences.views.preferences import NotificationPreferencesView

urlpatterns = [
    path('', NotificationPreferencesView.as_view(), name='notification_preferences'),
]
