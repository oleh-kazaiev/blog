from django.urls import include, path

from rest_framework.routers import DefaultRouter

from api.v0.posts.views.admin_category import AdminCategoryViewSet
from api.v0.posts.views.by_category import PostsByCategoryView
from api.v0.posts.views.category import CategoryViewSet
from api.v0.posts.views.comment import PostCommentCreateView
from api.v0.posts.views.manage_post import PostManageViewSet
from api.v0.posts.views.post import PostViewSet
from api.v0.posts.views.purchase import PostPurchaseView
from api.v0.posts.views.reaction_toggle import PostReactionToggleView

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'posts', PostViewSet, basename='post')

manage_router = DefaultRouter()
manage_router.register(r'posts', PostManageViewSet, basename='manage-post')
manage_router.register(r'categories', AdminCategoryViewSet, basename='admin-category')

urlpatterns = [
    path('', include(router.urls)),
    path('manage/', include(manage_router.urls)),
    path('posts/<slug:slug>/react/', PostReactionToggleView.as_view(), name='post-react'),
    path('posts/<slug:slug>/purchase/', PostPurchaseView.as_view(), name='post-purchase'),
    path('posts/<slug:slug>/add-comment/', PostCommentCreateView.as_view(), name='post-add-comment'),
    path('posts/by_category/', PostsByCategoryView.as_view(), name='post-by-category'),
]
