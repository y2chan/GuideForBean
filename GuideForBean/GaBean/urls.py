# GaBean/urls.py

from django.urls import path
from . import views

app_name = 'GaBean'

urlpatterns = [
    path('', views.home, name='home'),
    path('campusmap/', views.campusmap, name='campusmap'),
    path('humun_food/', views.humun_food, name='humun_food'),
    path('info_sugang/', views.info_sugang, name='info_sugang'),
    path('info_bus/', views.get_bus_info, name='info_bus'),
    path('info_subway/', views.get_subway_info, name='info_subway'),
    path('info_graduate/', views.info_graduate, name='info_graduate'),
    path('info_shuttle/', views.info_shuttle, name='info_shuttle'),
    path('info_gabean/', views.info_gabean, name='info_gabean'),
    path('sound_kong/', views.sound_kong, name='sound_kong'),
    path('sound_kong/write/', views.sound_kong_write, name='sound_kong_write'),
    path('sound_kong/detail/<int:post_id>/', views.sound_kong_detail, name='sound_kong_detail'),
    path('campusmap_detail/', views.campusmap_detail, name='campusmap_detail'),
    path('humun_random/', views.humun_random, name='humun_random'),
    path('news', views.news_search, name='news'),
    path('test/', views.test, name='test'),
    path('get_all_restaurant', views.get_all_restaurant, name='get_all_restaurant'),
]
