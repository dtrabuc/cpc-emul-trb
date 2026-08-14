from django.urls import path
from .views import StateView, KeyPressView, ResetView

urlpatterns = [
    path('state/', StateView.as_view(), name='state'),
    path('key/', KeyPressView.as_view(), name='key'),
    path('reset/', ResetView.as_view(), name='reset'),
]