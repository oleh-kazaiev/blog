from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from payments.plans import get_subscription_plans


class SubscriptionPlanListView(APIView):
    """API view for listing available subscription plans."""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        """Get list of available subscription plans."""
        plans = []
        for plan in get_subscription_plans().values():
            plans.append({
                'key': plan['key'],
                'label': plan['label'],
                'price_cents': plan['price_cents'],
                'currency': plan['currency'],
                'duration_seconds': int(plan['duration'].total_seconds()),
            })
        return Response(plans)
