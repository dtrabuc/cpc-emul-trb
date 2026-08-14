from django.urls import path
from .views import StateView

urlpatterns = [
    path('state/', StateView.as_view(), name='state'),
]