from django.urls import path

from api.v0.subscriptions.views.active import SubscriptionActiveView
from api.v0.subscriptions.views.cancel import SubscriptionCancelView
from api.v0.subscriptions.views.confirm import SubscriptionConfirmView
from api.v0.subscriptions.views.create import SubscriptionCreateView
from api.v0.subscriptions.views.detail import SubscriptionDetailView
from api.v0.subscriptions.views.plan_list import SubscriptionPlanListView

urlpatterns = [
    path('plans/', SubscriptionPlanListView.as_view(), name='subscriptions_plans'),
    path('', SubscriptionCreateView.as_view(), name='subscriptions_create'),
    path('current/', SubscriptionDetailView.as_view(), name='subscriptions_detail'),
    path('confirm/', SubscriptionConfirmView.as_view(), name='subscriptions_confirm'),
    path('active/', SubscriptionActiveView.as_view(), name='subscriptions_active'),
    path('cancel/', SubscriptionCancelView.as_view(), name='subscriptions_cancel'),
]
