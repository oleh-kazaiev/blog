from django.urls import path

from api.auth.views.login import LoginView
from api.auth.views.signup import SignupView

urlpatterns = [
    path('login/', LoginView.as_view(), name='api-login'),
    path('signup/', SignupView.as_view(), name='api-signup'),
]
