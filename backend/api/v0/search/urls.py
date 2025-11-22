from django.urls import path

from api.v0.search.views.post_search import PostSearchView

urlpatterns = [
    path('', PostSearchView.as_view(), name='search_posts'),
]
