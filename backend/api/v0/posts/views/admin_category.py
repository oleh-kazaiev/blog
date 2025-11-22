from rest_framework import viewsets

from api.permissions import IsAdminUserFlag
from api.v0.posts.serializers.category import CategorySerializer
from blog.models import Category


class AdminCategoryViewSet(viewsets.ModelViewSet):
    """Create/list/update categories for admins."""

    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUserFlag]
