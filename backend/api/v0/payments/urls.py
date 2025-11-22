from django.urls import path

from api.v0.payments.views.confirm import PaymentConfirmView
from api.v0.payments.views.create import PaymentCreateView
from api.v0.payments.views.detail import PaymentDetailView

urlpatterns = [
    path('', PaymentCreateView.as_view(), name='payments_create'),
    path('<int:pk>/', PaymentDetailView.as_view(), name='payments_detail'),
    path('<int:pk>/confirm/', PaymentConfirmView.as_view(), name='payments_confirm'),
]
