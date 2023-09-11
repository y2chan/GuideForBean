from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'GaBean'

urlpatterns = [
    path('', views.home, name='home'),
    path('campusmap/', views.campusmap, name='campusmap'),
    path('humun_food/', views.humun_food, name='humun_food'),
    path('info_sugang/', views.info_sugang, name='info_sugang'),
    path('info_bus/', views.bus_arrival_info, name='info_bus'),
    path('graduation/', views.graduation, name='graduation'),
    path('lunch_recommendation/', views.lunch_recommendation, name='lunch_recommendation'),
]