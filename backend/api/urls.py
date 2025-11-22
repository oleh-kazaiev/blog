from django.urls import include, path

urlpatterns = [
    path('v0/', include('api.v0.urls')),
    path('', include('api.auth.urls')),
]
