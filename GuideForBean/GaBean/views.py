from django.shortcuts import render
from .models import Restaurant, Restaurant_time, Bus_arrival_info
from .api_utils import get_and_save_restaurants  # 위에서 만든 함수 임포트
import requests
import json

def save_bus_arrival_info(data):
    for arrival in data:
        Bus_arrival_info.objects.create(
            bus_stop_location=arrival['버스정류장위치'],
            bus_number=arrival['버스번호'],
            arrival_time=arrival['버스도착예정시간'],
        )

def get_bus_arrival_info():
    api_key = "mogcuiLBAxr03JYAaBObRQuyTUU0tyR%2FYDbztxd11VVfCtcbbNIyr%2BJpU0Ir5DY1whzpR9blc%2Fsb7qf37lA0Cw%3D%3D"
    url = f"http://ws.bus.go.kr/api/rest/arrive/getArrInfoByRouteAll?ServiceKey={api_key}&busRouteId=100100118"
    response = requests.get(url)
    data = json.loads(response.content)

    if data.get('resultMessage') == '정상 처리되었습니다.':
        arrivals = data['result']['busArrivalInfo']
        save_bus_arrival_info(arrivals)


def bus_arrival_info(request):
    get_bus_arrival_info()  # API 데이터 업데이트
    arrivals = Bus_arrival_info.objects.all()
    return render(request, 'info_bus.html', {'arrivals': arrivals})

def home(request):
    return render(request, 'home.html', {'home': home})

def campusmap(request):
    return render(request, 'campusmap.html')

def humun_food(request):
    return render(request, 'humun_food.html')

def info_sugang(request):
    # 강의 정보 데이터 처리 로직 작성
    return render(request, 'info_sugang.html')

def graduation(request):
    # 졸업 정보 데이터 처리 로직 작성
    return render(request, 'graduation.html', {'graduation_info': graduation_info})

def lunch_recommendation(request):
    # 랜덤한 식당 추천 로직 작성
    return render(request, 'lunch_recommendation.html', {'recommended_restaurant': recommended_restaurant})