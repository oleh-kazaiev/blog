from django.urls import include, path

urlpatterns = [
    path('', include('api.v0.posts.urls')),
    path('users/', include('api.v0.users.urls')),
    path('emails/', include('api.v0.emails.urls')),
    path('notification-preferences/', include('api.v0.notification_preferences.urls')),
    path('payments/', include('api.v0.payments.urls')),
    path('subscriptions/', include('api.v0.subscriptions.urls')),
    path('search/', include('api.v0.search.urls')),
]
