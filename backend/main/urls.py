from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


# Health check endpoint for container orchestration
def health_check(request):
    """Health check endpoint for container orchestration."""
    return JsonResponse({'status': 'ok'})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('ckeditor5/', include('django_ckeditor_5.urls'), name='ck_editor_5_upload_file'),
    path('health/', health_check, name='health_check'),
]
