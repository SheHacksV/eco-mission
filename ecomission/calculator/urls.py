from django.urls import path, re_path

from . import views

urlpatterns = [
  path('', views.index, name='index'),
  path('cars/', views.get_car_details, name='get_car_details'),
  re_path(r'^cars/results/$', views.get_results, name='get_results'),
]
