from django.shortcuts import render
from .models import Building
from .api_utils import get_and_save_restaurants  # 위에서 만든 함수 임포트

def home(request):
    return render(request, 'Gabean:home.html', {'home': home})

def map(request):
    buildings = Building.objects.all()
    return render(request, 'Gabean:map.html', {'buildings': buildings})

def restaurant(request):
    # API 연동 및 데이터 처리 로직 작성
    restaurants = Restaurant.objects.all()

    # 데이터베이스에 데이터 추가
    get_and_save_restaurants()

    context = {
        'restaurants': restaurants
    }

    return render(request, 'Gabean:restaurant.html')

def courses(request):
    # 강의 정보 데이터 처리 로직 작성
    return render(request, 'Gabean:courses.html', {'courses': courses})

def graduation(request):
    # 졸업 정보 데이터 처리 로직 작성
    return render(request, 'Gabean:graduation.html', {'graduation_info': graduation_info})

def lunch_recommendation(request):
    # 랜덤한 식당 추천 로직 작성
    return render(request, 'Gabean:lunch_recommendation.html', {'recommended_restaurant': recommended_restaurant})