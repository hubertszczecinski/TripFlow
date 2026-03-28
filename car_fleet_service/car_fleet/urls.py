from django.urls import path
from .views import get_car_fleet

urlpatterns = [
    path('car_fleet/', get_car_fleet),
]