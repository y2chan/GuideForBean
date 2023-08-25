from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'GaBean'

urlpatterns = [
    path('', views.home, name='home'),
    path('map/', views.map, name='map'),
    path('restaurant/', views.restaurant, name='restaurant'),
    path('courses/', views.courses, name='courses'),
    path('graduation/', views.graduation, name='graduation'),
    path('lunch_recommendation/', views.lunch_recommendation, name='lunch_recommendation'),
]