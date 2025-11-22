from django.urls import path

from api.v0.emails.views.detail import EmailDetailView
from api.v0.emails.views.list import EmailListView

urlpatterns = [
    path('', EmailListView.as_view(), name='email_list'),
    path('<int:pk>/', EmailDetailView.as_view(), name='email_detail'),
]
