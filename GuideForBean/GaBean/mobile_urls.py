from django.urls import path
from . import views

app_name = 'gabean_mobile'

urlpatterns = [
    path('', views.mobile_home.as_view(), name='m_home'),
    path('campusmap/', views.mobile_campusmap.as_view(), name='m_campusmap'),
    path('humun_food/', views.mobile_humun_food.as_view(), name='m_humun_food'),
    path('info_sugang/', views.mobile_info_sugang.as_view(), name='m_info_sugang'),
    path('info_bus/', views.mobile_info_bus.as_view(), name='m_info_bus'),
    path('info_subway/', views.mobile_info_subway.as_view(), name='m_info_subway'),
    path('info_graduate/', views.mobile_info_graduate.as_view(), name='m_info_graduate'),
    path('info_shuttle/', views.mobile_info_shuttle.as_view(), name='m_info_shuttle'),
    path('info_gabean/', views.mobile_info_gabean.as_view(), name='m_info_gabean'),
    path('sound_kong/', views.mobile_sound_kong.as_view(), name='m_sound_kong'),
    path('sound_kong/write/', views.mobile_sound_kong_write.as_view(), name='m_sound_kong_write'),
    path('sound_kong/detail/<int:post_id>/', views.mobile_sound_kong_detail.as_view(), name='m_sound_kong_detail'),
    path('campusmap_detail/', views.mobile_campusmap_detail.as_view(), name='m_campusmap_detail'),
    path('humun_random/', views.mobile_humun_random.as_view(), name='m_humun_random'),
    path('m_news', views.mobile_news_search.as_view(), name='m_news'),
    path('m_get_all_restaurant', views.mobile_get_all_restaurant.as_view(), name='m_get_all_restaurant'),
]
