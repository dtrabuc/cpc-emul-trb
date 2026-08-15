from django.urls import path
from .views import StateView, KeyPressView, ResetView, LoadROMView

urlpatterns = [
    path('state/', StateView.as_view(), name='state'),
    path('key/', KeyPressView.as_view(), name='key'),
    path('reset/', ResetView.as_view(), name='reset'),
    path('load_roms/', LoadROMView.as_view(), name='load_roms'),
]