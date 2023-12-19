from django.shortcuts import render, redirect
from .models import Restaurant, Restaurant_time, Bus_arrival_info, HumunFood, OpeningHours, Post
from django.conf import settings
from .forms import HumunFoodForm
import requests
import json
import datetime
import random
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

retry_strategy = Retry(
    total=3,
    backoff_factor=0.1,
    status_forcelist=[500, 502, 503, 504],
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session = requests.Session()
session.mount('http://', adapter)
session.mount('https://', adapter)

def info_library(request):
    return render(request, 'info_library.html')

def news_search(request):
    # 네이버 검색 API를 호출할 URL을 설정합니다.
    url = "https://openapi.naver.com/v1/search/news.json"

    # URL 파라미터에서 검색어를 가져옵니다. 기본값은 빈 문자열입니다.
    query = request.GET.get('query', '')

    if query:
        # API를 호출할 때 사용할 파라미터를 설정합니다.
        params = {'query': query, 'display': 20}

        # API를 호출할 때 사용할 헤더를 설정합니다. 클라이언트 ID와 시크릿은 실제 값으로 변경해야 합니다.
        headers = {
            'X-Naver-Client-Id': '48KtNy0_eHdwWFg3vDUg',
            'X-Naver-Client-Secret': 'LFiuNrJGef'
        }

        # API를 호출하고 응답을 가져옵니다.
        response = requests.get(url, headers=headers, params=params)

        # 응답을 JSON 형식으로 파싱합니다.
        result = json.loads(response.text)

        for item in result['items']:
            item['title'] = item['title'].replace('<b>', '<strong>').replace('</b>', '</strong>')
            item['description'] = item['description'].replace('<b>', '<strong>').replace('</b>', '</strong>')
            item['pubDate'] = datetime.strptime(item['pubDate'], '%a, %d %b %Y %H:%M:%S +0900').strftime('%Y년 %m월 %d일 %H시 %M분')

        # 결과와 검색어를 템플릿에 전달합니다.
        return render(request, 'news.html', {'news': result['items'], 'query': query})

    else:  # 검색어가 없는 경우 빈 결과를 전달합니다.
        return render(request, 'news.html', {'news': [], 'query': query})
from itertools import groupby
import requests
from django.conf import settings
import xml.etree.ElementTree as ET
from django.shortcuts import render

def get_bus_info(request):
    try:
        api_key = settings.BUS_API_KEY
        api_urls = [
            # 삼육대후문.논골.한화아파트
            f"http://ws.bus.go.kr/api/rest/arrive/getArrInfoByRoute?serviceKey={api_key}&stId=222001597&busRouteId=100100039&ord=16", # 202
            f"http://ws.bus.go.kr/api/rest/arrive/getArrInfoByRoute?serviceKey={api_key}&stId=222001597&busRouteId=100100165&ord=22", # 1155
            # 삼육대앞
            f"http://ws.bus.go.kr/api/rest/arrive/getArrInfoByRoute?serviceKey={api_key}&stId=110000055&busRouteId=100100039&ord=18", # 202
            f"http://ws.bus.go.kr/api/rest/arrive/getArrInfoByRoute?serviceKey={api_key}&stId=110000055&busRouteId=100100165&ord=24", # 1155
            # 화랑대역1번출구
            f"http://ws.bus.go.kr/api/rest/arrive/getArrInfoByRoute?serviceKey={api_key}&stId=110000018&busRouteId=100100039&ord=106", # 202
            f"http://ws.bus.go.kr/api/rest/arrive/getArrInfoByRoute?serviceKey={api_key}&stId=110000018&busRouteId=100100165&ord=44", # 1155
            # 태릉입구역7번출구.서울생활사박물관
            f"http://ws.bus.go.kr/api/rest/arrive/getArrInfoByRoute?serviceKey={api_key}&stId=110000017&busRouteId=100100165&ord=42", # 1155
            # 석계역(석계역4번출구)
            f"http://ws.bus.go.kr/api/rest/arrive/getArrInfoByRoute?serviceKey={api_key}&stId=107000057&busRouteId=100100165&ord=40", # 1155
            # 석계역1번출구.A
            f"http://ws.bus.go.kr/api/rest/arrive/getArrInfoByRoute?serviceKey={api_key}&stId=110000183&busRouteId=100100165&ord=38" # 1155
        ]

        grouped_data = {"direction_1": [], "direction_2": []}

        for api_url in api_urls:
            response = requests.get(api_url)
            # XML 데이터 파싱
            root = ET.fromstring(response.text)

            # 원하는 데이터 추출
            data = {
                "stNm": root.find(".//stNm").text,
                "rtNm": root.find(".//rtNm").text,
                "arrmsg1": root.find(".//arrmsg1").text,
                "arrmsg2": root.find(".//arrmsg2").text,
            }

            if data["stNm"] in ["삼육대후문.논골.한화아파트", "삼육대앞"]:
                grouped_data["direction_1"].append(data)
            else:
                grouped_data["direction_2"].append(data)

        def group_by_stNm(data):
            # stNm 기준으로 데이터를 먼저 정렬합니다.
            sorted_data = sorted(data, key=lambda x: x['stNm'])
            return {k: list(g) for k, g in groupby(sorted_data, key=lambda x: x['stNm'])}

        grouped_data["direction_1"] = group_by_stNm(grouped_data["direction_1"])
        grouped_data["direction_2"] = group_by_stNm(grouped_data["direction_2"])

        return render(request, 'info_bus.html', {'grouped_data': grouped_data})

    except requests.exceptions.RequestException as e:
        # 네트워크 오류 또는 연결 오류
        return render(request, 'bus_error_net.html', {'error_message': 'API 서버에 연결할 수 없습니다.'})

    except ValueError as e:
        # JSON 파싱 오류
        return render(request, 'bus_error_json.html', {'error_message': 'API 응답을 파싱할 수 없습니다.'})

def get_current_base_datetime():
    now = timezone.now()
    current_hour = now.hour
    base_time = None

    if current_hour < 2.5:
        base_time = '2300'
        base_date = (now - timedelta(days=1)).strftime('%Y%m%d')
    elif current_hour < 5.5:
        base_time = '0200'
        base_date = now.strftime('%Y%m%d')
    elif current_hour < 8.5:
        base_time = '0500'
        base_date = now.strftime('%Y%m%d')
    elif current_hour < 11.5:
        base_time = '0800'
        base_date = now.strftime('%Y%m%d')
    elif current_hour < 14.5:
        base_time = '1100'
        base_date = now.strftime('%Y%m%d')
    elif current_hour < 17.5:
        base_time = '1400'
        base_date = now.strftime('%Y%m%d')
    elif current_hour < 20.5:
        base_time = '1700'
        base_date = now.strftime('%Y%m%d')
    elif current_hour < 23.5:
        base_time = '2000'
        base_date = now.strftime('%Y%m%d')
    else:
        base_time = '2300'
        base_date = now.strftime('%Y%m%d')

    return base_date, base_time

def get_weather(city):
    api_key = settings.BUS_API_KEY
    base_date, base_time = get_current_base_datetime()
    url = f'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst?serviceKey={api_key}&numOfRows=10&pageNo=1&base_date={base_date}&base_time={base_time}&nx=62&ny=128&dataType=JSON'
    response = requests.get(url, timeout=10)

    try:
        data = response.json()

        if 'response' not in data or 'body' not in data['response'] or 'items' not in data['response']['body']:
            raise ValueError("Invalid API response format")

        # 데이터 추출 및 처리
        temperature = None
        weather_status = None
        wind_speed = None
        precipitation_type = None

        for item in data['response']['body']['items']['item']:
            category = item['category']
            fcst_value = item['fcstValue']

            if category == 'TMP':
                temperature = fcst_value
            elif category == 'SKY':
                fcst_value = int(fcst_value)
                if 0 <= fcst_value <= 5:
                    weather_status = '구름 없음'
                elif 6 <= fcst_value <= 8:
                    weather_status = '구름 많음'
                elif 9 <= fcst_value <= 10:
                    weather_status = '흐림'
            elif category == 'WSD':
                fcst_value = float(fcst_value)
                if 0 <= fcst_value < 4:
                    wind_speed = '선선함'
                elif 4 <= fcst_value < 9:
                    wind_speed = '약풍'
                elif 9 <= fcst_value < 14:
                    wind_speed = '강풍'
                elif 14 <= fcst_value:
                    wind_speed = '심한 강풍'
            elif category == 'PTY':
                fcst_value = int(fcst_value)
                if fcst_value == 0:
                    precipitation_type = '맑음'
                elif fcst_value == 1:
                    precipitation_type = '비'
                elif fcst_value == 2:
                    precipitation_type = '비/눈'
                elif fcst_value == 3:
                    precipitation_type = '눈'
                elif fcst_value == 4:
                    precipitation_type = '소나기'

        # 현재 날짜 및 시간 설정
        today_date = datetime.now().strftime('%Y-%m-%d')
        current_time = datetime.now().strftime('%H:%M')

        # 결과 데이터를 딕셔너리로 저장
        weather_info = {
            'today_date': today_date,
            'current_time': current_time,
            'temperature': temperature if temperature is not None else 'N/A',
            'weather_status': weather_status if weather_status is not None else 'N/A',
            'wind_speed': wind_speed if wind_speed is not None else 'N/A',
            'precipitation_type': precipitation_type if precipitation_type is not None else 'N/A',
        }

    except ValueError as e:
        weather_info = {
            'today_date': 'N/A',
            'current_time': 'N/A',
            'temperature': 'N/A',
            'weather_status': 'N/A',
            'wind_speed': 'N/A',
            'precipitation_type': 'N/A',
        }

    return weather_info

def home(request):
    city = "서울특별시 노원구 화랑로 815"  # 실제 도시로 변경해주세요
    try:
        weather_info = get_weather(city)
    except requests.Timeout:
        # 타임아웃이 발생한 경우, 대체 동작 수행
        weather_info = {
            'today_date': 'N/A',
            'current_time': 'N/A',
            'temperature': 'N/A',
            'weather_status': 'N/A',
            'wind_speed': 'N/A',
            'precipitation_type': '서버 응답 시간 초과',
        }
    return render(request, 'home.html', {'weather_info': weather_info, 'city': city})


def campusmap(request):
    return render(request, 'campusmap.html')

import logging

# 로거 생성
logger = logging.getLogger(__name__)

def humun_food(request):
    # 요일을 숫자로 매핑하는 딕셔너리
    weekday_mapping = {
        '월요일': 0,
        '화요일': 1,
        '수요일': 2,
        '목요일': 3,
        '금요일': 4,
        '토요일': 5,
        '일요일': 6,
        '매일': '매일',
        '휴무': '휴무',
    }

    # 가게 목록을 가져옵니다.
    restaurants = HumunFood.objects.all()

    # 현재 날짜와 시간을 가져옵니다.
    current_datetime = timezone.now()
    current_time = current_datetime.time()
    current_weekday = current_datetime.weekday()

    for restaurant in restaurants:
        opening_hours = OpeningHours.objects.filter(restaurant=restaurant)
        current_opening_hour = None
        if current_weekday is not None:
            for opening_hour in opening_hours:
                week_number = weekday_mapping[opening_hour.week]

                if week_number == current_weekday or week_number == '매일':
                    current_opening_hour = opening_hour
                    break

        time_difference = None  # Initialize time_difference here

        try:
            if current_opening_hour:
                current_datetime = datetime.now().replace(hour=current_time.hour, minute=current_time.minute)
                open_datetime = datetime.now().replace(hour=current_opening_hour.open_time.hour, minute=current_opening_hour.open_time.minute)
                close_datetime = datetime.now().replace(hour=current_opening_hour.close_time.hour, minute=current_opening_hour.close_time.minute)

                if open_datetime <= current_datetime < close_datetime:
                    restaurant.open_status = "영업 중"
                    time_difference = close_datetime - current_datetime
                elif open_datetime == close_datetime:
                    # 현재 요일에 해당하는 영업 정보가 없을 경우 "휴무"로 처리
                    restaurant.open_status = "휴무"
                    restaurant.remaining_time = None
                elif current_datetime >= close_datetime:
                    restaurant.open_status = "마감"
                    next_day_open_datetime = open_datetime + timedelta(days=1)
                    if current_datetime.time() < open_datetime.time():
                        next_day_open_datetime = open_datetime
                        time_difference = next_day_open_datetime - current_datetime
                else:
                    restaurant.open_status = "영업 중"
                    time_difference = close_datetime - current_datetime

                if time_difference:
                    hours, remainder = divmod(time_difference.total_seconds(), 3600)
                    minutes = remainder // 60

                    restaurant.remaining_time = (int(hours), int(minutes))
                else:
                    restaurant.remaining_time = None
            else:
                # 현재 요일에 해당하는 영업 정보가 없을 경우 "휴무"로 처리
                restaurant.open_status = "휴무"
                restaurant.remaining_time = None
        except Exception as e:
            logger.exception("An error occurred while getting the current time: %s", e)

    # 가게 타입 정보를 가져옵니다.
    restaurant_types = HumunFood.objects.values_list('type', flat=True).distinct()

    context = {
        'restaurants': restaurants,
        'restaurant_types': restaurant_types,
        'current_time': current_time,
    }
    return render(request, 'humun_food.html', context)

def get_all_restaurant(request):
    # 모든 'type' 데이터 가져오기
    types = list(HumunFood.objects.exclude(type='카페').values_list('type', flat=True).distinct())
    items = list(HumunFood.objects.exclude(type='카페').values_list('name', flat=True).distinct())
    return JsonResponse({'types': types, 'items': items})

def humun_random(request):
    return render(request, 'humun_random.html')

def info_sugang(request):
    # 강의 정보 데이터 처리 로직 작성
    return render(request, 'info_sugang.html')

def info_graduate(request):
    # 졸업 정보 데이터 처리 로직 작성
    return render(request, 'info_graduate.html')

def get_weekday_timetable():
    # 월요일부터 목요일까지 시간표를 반환합니다.
    timetable = {
        "화랑대 -> 학교": ["08:10", "08:15", "08:20", "08:25", "08:30", "08:35", "08:40", "08:45", "08:50", "08:55", "09:00", "09:05", "09:10", "09:15", "09:20", "09:25", "09:30", "09:35", "09:40", "09:45", "09:50", "09:55", "10:00", "10:20", "10:40", "11:00", "11:20", "11:40", "12:00"],
        "태릉입구, 석계 -> 학교": ["12:00", "12:25", "12:50", "13:15", "13:40", "14:05", "14:30", "15:00", "15:20", "15:40", "16:00", "16:20", "16:40", "17:00", "17:20", "17:40", "18:00", "18:15"],
        "별내 -> 학교": ["08:40", "09:40", "10:40", "11:40", "12:40", "13:40", "14:40", "15:40", "16:40", "17:40"],
        "학교 -> 태릉입구, 석계": ["12:00", "12:25", "12:50", "13:15", "13:40", "14:05", "14:30", "15:00", "15:20", "15:40", "16:00", "16:20", "16:40", "17:00", "17:20", "17:40", "18:00", "18:15"],
        "학교 -> 별내": ["10:25", "11:25", "12:25", "13:25", "14:25", "15:25", "16:25", "17:25"],
        # 나머지 노선 시간표도 추가
    }
    return timetable

def get_friday_timetable():
    # 금요일 시간표를 반환합니다.
    timetable = {
        "화랑대 -> 학교": ["08:10", "08:15", "08:20", "08:25", "08:30", "08:35", "08:40", "08:45", "08:50", "08:55", "09:00", "09:05", "09:10", "09:15", "09:20", "09:25", "09:30", "09:35", "09:40", "09:50", "09:55", "10:00", "10:20", "10:40", "11:00", "11:20", "11:40", "12:00"],
        "태릉입구, 석계 -> 학교": ["12:00", "12:25", "12:50", "13:15", "13:40", "14:05", "14:30", "15:00", "15:20", "15:30"],
        "별내 -> 학교": ["08:40", "09:40", "10:40", "11:40", "12:40", "13:40", "14:40", "15:40"],
        "학교 -> 태릉입구, 석계": ["12:00", "12:25", "12:50", "13:15", "13:40", "14:05", "14:30", "15:00", "15:20", "15:40"],
        "학교 -> 별내": ["10:25", "11:25", "12:25", "13:25", "14:25", "15:25"],
        # 나머지 노선 시간표도 추가
    }
    return timetable

def get_weekend_timetable():
    # 주말 시간표를 반환합니다.
    timetable = {
        "전체 노선": ["운행 종료"],
    }
    return timetable

def info_shuttle(request):
    # 현재 시간을 가져옵니다.
    now = datetime.now()

    # 현재 요일을 가져옵니다. (월요일: 0, 일요일: 6)
    current_weekday = now.weekday()

    left_info = {}
    right_info = {}

    # 남은 시간을 계산합니다.
    remaining_times = {}
    if 0 <= current_weekday < 4:  # 월요일부터 목요일까지
        timetable = get_weekday_timetable()
    elif current_weekday == 4:  # 금요일
        timetable = get_friday_timetable()
    else:  # 토요일과 일요일
        weekend_timetable = get_weekend_timetable()
        left_info, right_info = weekend_timetable, weekend_timetable  # 주말은 left_info와 right_info에 둘 다 할당
        timetable = weekend_timetable  # 이 부분이 빠져있어서 발생한 오류입니다.

    for shuttle, times in timetable.items():
        next_departure_time = None
        for time_str in times:
            if time_str == "운행 종료":
                remaining_times[shuttle] = "운행 종료"
                if len(left_info) < 3:
                    left_info[shuttle] = "운행 종료"
                else:
                    right_info[shuttle] = "운행 종료"
                break
            departure_time = datetime.strptime(time_str, "%H:%M")
            departure_time = departure_time.replace(year=now.year, month=now.month, day=now.day)  # 현재 날짜 정보 추가
            if departure_time > now:
                next_departure_time = departure_time
                break

        if next_departure_time is not None:
            time_difference = next_departure_time - now
            remaining_minutes = int(time_difference.total_seconds() / 60)  # 초를 분으로 변환
            remaining_times[shuttle] = f"{remaining_minutes} 분 남았습니다."  # 분을 붙여서 저장
            if len(left_info) < 3:
                left_info[shuttle] = f"{remaining_minutes} 분 남았습니다."
            else:
                right_info[shuttle] = f"{remaining_minutes} 분 남았습니다."
        else:
            remaining_times[shuttle] = "운행 종료"  # next_departure_time이 None인 경우 처리
            if len(left_info) < 3:
                left_info[shuttle] = "운행 종료"
            else:
                right_info[shuttle] = "운행 종료"

    return render(request, 'info_shuttle.html', {'left_info': left_info, 'right_info': right_info})



def campusmap_detail(request):
    return render(request, 'campusmap_detail.html')

def get_subway_info(request):
    try:
        api_key = settings.SUBWAY_API_KEY
        api_urls = [
            f"http://swopenapi.seoul.go.kr/api/subway/{api_key}/xml/realtimeStationArrival/0/5/화랑대(서울여대입구)",
            f"http://swopenapi.seoul.go.kr/api/subway/{api_key}/xml/realtimeStationArrival/0/5/태릉입구",
            f"http://swopenapi.seoul.go.kr/api/subway/{api_key}/xml/realtimeStationArrival/0/5/석계",
            f"http://swopenapi.seoul.go.kr/api/subway/{api_key}/xml/realtimeStationArrival/0/5/별내"
        ]

        grouped_data = {"direction_1": [], "direction_2": [], "direction_3": [], "direction_4": []}

        for api_url in api_urls:
            response = requests.get(api_url)
            root = ET.fromstring(response.text)

            statnNm_element = root.find(".//statnNm")
            if statnNm_element is not None:
                data = {
                    "statnNm": statnNm_element.text,
                    "trainLineNm": root.find(".//trainLineNm").text,
                    "arvlMsg2": root.find(".//arvlMsg2").text,
                    "recptnDt": root.find(".//recptnDt").text,
                }

                if data["statnNm"] in ["화랑대(서울여대입구)"]:
                    grouped_data["direction_1"].append(data)
                elif data["statnNm"] in ["태릉입구"]:
                    grouped_data["direction_2"].append(data)
                elif data["statnNm"] in ["석계"]:
                    grouped_data["direction_3"].append(data)
                else:
                    grouped_data["direction_4"].append(data)

        return render(request, 'info_subway.html', {'grouped_data': grouped_data})

    except requests.exceptions.RequestException as e:
        return render(request, 'bus_error_net.html', {'error_message': 'API 서버에 연결할 수 없습니다.'})

    except ET.ParseError as e:
        return render(request, 'bus_error_xml.html', {'error_message': 'XML 데이터를 파싱할 수 없습니다.'})

def test(request):
    return render(request, 'test.html')

def info_gabean(request):
    return render(request, 'info_gabean.html')


def sound_kong(request):
    posts = Post.objects.all()
    return render(request, 'sound_kong.html', {'posts': posts})

def sound_kong_write(request):
    if request.method == 'POST':
        title = request.POST['title']
        content = request.POST['content']
        Post.objects.create(title=title, content=content)
        return redirect('GaBean:sound_kong')
    return render(request, 'sound_kong_write.html')

def sound_kong_detail(request, post_id):
    post = Post.objects.get(id=post_id)
    return render(request, 'sound_kong_detail.html', {'post': post})



## 모바일 용 view
from django.views.generic import TemplateView

class mobile_home(TemplateView):
    template_name = 'mobile/m_home.html'  # 모바일 전용 템플릿

    def get_current_base_datetime(self):
        now = timezone.now()
        current_hour = now.hour
        base_time = None

        if current_hour < 2.5:
            base_time = '2300'
            base_date = (now - timedelta(days=1)).strftime('%Y%m%d')
        elif current_hour < 5.5:
            base_time = '0200'
            base_date = now.strftime('%Y%m%d')
        elif current_hour < 8.5:
            base_time = '0500'
            base_date = now.strftime('%Y%m%d')
        elif current_hour < 11.5:
            base_time = '0800'
            base_date = now.strftime('%Y%m%d')
        elif current_hour < 14.5:
            base_time = '1100'
            base_date = now.strftime('%Y%m%d')
        elif current_hour < 17.5:
            base_time = '1400'
            base_date = now.strftime('%Y%m%d')
        elif current_hour < 20.5:
            base_time = '1700'
            base_date = now.strftime('%Y%m%d')
        elif current_hour < 23.5:
            base_time = '2000'
            base_date = now.strftime('%Y%m%d')
        else:
            base_time = '2300'
            base_date = now.strftime('%Y%m%d')

        return base_date, base_time

    def get_weather(self, city):
        api_key = settings.BUS_API_KEY
        base_date, base_time = self.get_current_base_datetime()
        url = f'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst?serviceKey={api_key}&numOfRows=10&pageNo=1&base_date={base_date}&base_time={base_time}&nx=62&ny=128&dataType=JSON'
        response = requests.get(url, timeout=10)

        try:
            data = response.json()

            if 'response' not in data or 'body' not in data['response'] or 'items' not in data['response']['body']:
                raise ValueError("Invalid API response format")

            # 데이터 추출 및 처리
            temperature = None
            weather_status = None
            wind_speed = None
            precipitation_type = None

            for item in data['response']['body']['items']['item']:
                category = item['category']
                fcst_value = item['fcstValue']

                if category == 'TMP':
                    temperature = fcst_value
                elif category == 'SKY':
                    fcst_value = int(fcst_value)
                    if 0 <= fcst_value <= 5:
                        weather_status = '구름 없음'
                    elif 6 <= fcst_value <= 8:
                        weather_status = '구름 많음'
                    elif 9 <= fcst_value <= 10:
                        weather_status = '흐림'
                elif category == 'WSD':
                    fcst_value = float(fcst_value)
                    if 0 <= fcst_value < 4:
                        wind_speed = '선선함'
                    elif 4 <= fcst_value < 9:
                        wind_speed = '약풍'
                    elif 9 <= fcst_value < 14:
                        wind_speed = '강풍'
                    elif 14 <= fcst_value:
                        wind_speed = '심한 강풍'
                elif category == 'PTY':
                    fcst_value = int(fcst_value)
                    if fcst_value == 0:
                        precipitation_type = '맑음'
                    elif fcst_value == 1:
                        precipitation_type = '비'
                    elif fcst_value == 2:
                        precipitation_type = '비/눈'
                    elif fcst_value == 3:
                        precipitation_type = '눈'
                    elif fcst_value == 4:
                        precipitation_type = '소나기'

            # 현재 날짜 및 시간 설정
            today_date = datetime.now().strftime('%Y-%m-%d')
            current_time = datetime.now().strftime('%H:%M')

            # 결과 데이터를 딕셔너리로 저장
            weather_info = {
                'today_date': today_date,
                'current_time': current_time,
                'temperature': temperature if temperature is not None else 'N/A',
                'weather_status': weather_status if weather_status is not None else 'N/A',
                'wind_speed': wind_speed if wind_speed is not None else 'N/A',
                'precipitation_type': precipitation_type if precipitation_type is not None else 'N/A',
            }

        except ValueError as e:
            weather_info = {
                'today_date': 'N/A',
                'current_time': 'N/A',
                'temperature': 'N/A',
                'weather_status': 'N/A',
                'wind_speed': 'N/A',
                'precipitation_type': 'N/A',
            }

        return weather_info

    def get(self, request, *args, **kwargs):
        city = "서울특별시 노원구 화랑로 815"  # 실제 도시로 변경해주세요
        try:
            weather_info = self.get_weather(city)
        except requests.Timeout:
            # 타임아웃이 발생한 경우, 대체 동작 수행
            weather_info = {
                'today_date': 'N/A',
                'current_time': 'N/A',
                'temperature': 'N/A',
                'weather_status': 'N/A',
                'wind_speed': 'N/A',
                'precipitation_type': '서버 응답 시간 초과',
            }
        return render(request, self.template_name, {'weather_info': weather_info, 'city': city})

class mobile_info_bus(TemplateView):
    template_name = 'mobile/m_info_bus.html'  # 모바일 전용 템플릿
    def get(self, request, *args, **kwargs):
        try:
            api_key = settings.BUS_API_KEY
            api_urls = [
                # 삼육대후문.논골.한화아파트
                f"http://ws.bus.go.kr/api/rest/arrive/getArrInfoByRoute?serviceKey={api_key}&stId=222001597&busRouteId=100100039&ord=16", # 202
                f"http://ws.bus.go.kr/api/rest/arrive/getArrInfoByRoute?serviceKey={api_key}&stId=222001597&busRouteId=100100165&ord=22", # 1155
                # 삼육대앞
                f"http://ws.bus.go.kr/api/rest/arrive/getArrInfoByRoute?serviceKey={api_key}&stId=110000055&busRouteId=100100039&ord=18", # 202
                f"http://ws.bus.go.kr/api/rest/arrive/getArrInfoByRoute?serviceKey={api_key}&stId=110000055&busRouteId=100100165&ord=24", # 1155
                # 화랑대역1번출구
                f"http://ws.bus.go.kr/api/rest/arrive/getArrInfoByRoute?serviceKey={api_key}&stId=110000018&busRouteId=100100039&ord=106", # 202
                f"http://ws.bus.go.kr/api/rest/arrive/getArrInfoByRoute?serviceKey={api_key}&stId=110000018&busRouteId=100100165&ord=44", # 1155
                # 태릉입구역7번출구.서울생활사박물관
                f"http://ws.bus.go.kr/api/rest/arrive/getArrInfoByRoute?serviceKey={api_key}&stId=110000017&busRouteId=100100165&ord=42", # 1155
                # 석계역(석계역4번출구)
                f"http://ws.bus.go.kr/api/rest/arrive/getArrInfoByRoute?serviceKey={api_key}&stId=107000057&busRouteId=100100165&ord=40", # 1155
                # 석계역1번출구.A
                f"http://ws.bus.go.kr/api/rest/arrive/getArrInfoByRoute?serviceKey={api_key}&stId=110000183&busRouteId=100100165&ord=38" # 1155
            ]

            grouped_data = {"direction_1": [], "direction_2": []}

            for api_url in api_urls:
                response = requests.get(api_url)
                # XML 데이터 파싱
                root = ET.fromstring(response.text)

                # 원하는 데이터 추출
                data = {
                    "stNm": root.find(".//stNm").text,
                    "rtNm": root.find(".//rtNm").text,
                    "arrmsg1": root.find(".//arrmsg1").text,
                    "arrmsg2": root.find(".//arrmsg2").text,
                }

                if data["stNm"] in ["삼육대후문.논골.한화아파트", "삼육대앞"]:
                    grouped_data["direction_1"].append(data)
                else:
                    grouped_data["direction_2"].append(data)

            # 중복된 stNm 값을 그룹화하기 위한 딕셔너리 생성
            for data in grouped_data["direction_1"] + grouped_data["direction_2"]:
                stNm = data.get('stNm')
                if stNm is not None:
                    if stNm not in grouped_data:
                        grouped_data[stNm] = []
                    grouped_data[stNm].append(data)

            def group_by_stNm(data):
                # stNm 기준으로 데이터를 먼저 정렬합니다.
                sorted_data = sorted(data, key=lambda x: x['stNm'])
                return {k: list(g) for k, g in groupby(sorted_data, key=lambda x: x['stNm'])}

            grouped_data["direction_1"] = group_by_stNm(grouped_data["direction_1"])
            grouped_data["direction_2"] = group_by_stNm(grouped_data["direction_2"])

            # 그룹화된 데이터를 템플릿으로 전달
            return render(request, self.template_name, {'grouped_data': grouped_data})

        except requests.exceptions.RequestException as e:
            # 네트워크 오류 또는 연결 오류
            return render(request, 'bus_error_net.html', {'error_message': 'API 서버에 연결할 수 없습니다.'})

        except ValueError as e:
            # JSON 파싱 오류
            return render(request, 'bus_error_json.html', {'error_message': 'API 응답을 파싱할 수 없습니다.'})

class mobile_humun_food(TemplateView):
    template_name = 'mobile/m_humun_food.html'  # 모바일 전용 템플릿
    def get(self, request):
        # 요일을 숫자로 매핑하는 딕셔너리
        weekday_mapping = {
            '월요일': 0,
            '화요일': 1,
            '수요일': 2,
            '목요일': 3,
            '금요일': 4,
            '토요일': 5,
            '일요일': 6,
            '매일': '매일',
            '휴무': '휴무',
        }

        # 가게 목록을 가져옵니다.
        restaurants = HumunFood.objects.all()

        # 현재 날짜와 시간을 가져옵니다.
        current_datetime = timezone.now()
        current_time = current_datetime.time()
        current_weekday = current_datetime.weekday()

        for restaurant in restaurants:
            opening_hours = OpeningHours.objects.filter(restaurant=restaurant)
            current_opening_hour = None
            if current_weekday is not None:
                for opening_hour in opening_hours:
                    week_number = weekday_mapping[opening_hour.week]

                    if week_number == current_weekday or week_number == '매일':
                        current_opening_hour = opening_hour
                        break

            time_difference = None  # Initialize time_difference here

            try:
                if current_opening_hour:
                    current_datetime = datetime.now().replace(hour=current_time.hour, minute=current_time.minute)
                    open_datetime = datetime.now().replace(hour=current_opening_hour.open_time.hour, minute=current_opening_hour.open_time.minute)
                    close_datetime = datetime.now().replace(hour=current_opening_hour.close_time.hour, minute=current_opening_hour.close_time.minute)

                    if open_datetime <= current_datetime <= close_datetime:
                        restaurant.open_status = "영업 중"
                        time_difference = close_datetime - current_datetime
                    elif open_datetime == close_datetime:
                        # 현재 요일에 해당하는 영업 정보가 없을 경우 "휴무"로 처리
                        restaurant.open_status = "휴무"
                        restaurant.remaining_time = None
                    elif close_datetime == current_datetime:
                        restaurant.open_status = "마감"
                        # Calculate the next day's opening time
                        next_day_open_datetime = open_datetime + timedelta(days=1)
                        time_difference = next_day_open_datetime - current_datetime
                    else:
                        # 그렇지 않으면 "마감"
                        restaurant.open_status = "마감"
                        # Calculate the next day's opening time
                        next_day_open_datetime = open_datetime + timedelta(days=1)
                        time_difference = next_day_open_datetime - current_datetime

                    if time_difference:
                        hours, remainder = divmod(time_difference.total_seconds(), 3600)
                        minutes = remainder // 60

                        restaurant.remaining_time = (int(hours), int(minutes))
                    else:
                        restaurant.remaining_time = None
                else:
                    # 현재 요일에 해당하는 영업 정보가 없을 경우 "휴무"로 처리
                    restaurant.open_status = "휴무"
                    restaurant.remaining_time = None
            except Exception as e:
                logger.exception("An error occurred while getting the current time: %s", e)

        # 가게 타입 정보를 가져옵니다.
        restaurant_types = HumunFood.objects.values_list('type', flat=True).distinct()

        context = {
            'restaurants': restaurants,
            'restaurant_types': restaurant_types,
            'current_time': current_time,
        }
        return render(request, self.template_name, context)

class mobile_info_sugang(TemplateView):
    template_name = 'mobile/m_info_sugang.html'  # 모바일 전용 템플릿

class mobile_info_subway(TemplateView):
    template_name = 'mobile/m_info_subway.html'  # 모바일 전용 템플릿
    def get(self, request, *args, **kwargs):
        try:
            api_key = settings.SUBWAY_API_KEY
            api_urls = [
                f"http://swopenapi.seoul.go.kr/api/subway/{api_key}/xml/realtimeStationArrival/0/5/화랑대(서울여대입구)",
                f"http://swopenapi.seoul.go.kr/api/subway/{api_key}/xml/realtimeStationArrival/0/5/태릉입구",
                f"http://swopenapi.seoul.go.kr/api/subway/{api_key}/xml/realtimeStationArrival/0/5/석계",
                f"http://swopenapi.seoul.go.kr/api/subway/{api_key}/xml/realtimeStationArrival/0/5/별내"
            ]

            grouped_data = {"direction_1": [], "direction_2": [], "direction_3": [], "direction_4": []}

            for api_url in api_urls:
                response = requests.get(api_url)
                root = ET.fromstring(response.text)

                statnNm_element = root.find(".//statnNm")
                if statnNm_element is not None:
                    data = {
                        "statnNm": statnNm_element.text,
                        "trainLineNm": root.find(".//trainLineNm").text,
                        "arvlMsg2": root.find(".//arvlMsg2").text,
                        "recptnDt": root.find(".//recptnDt").text,
                    }

                    if data["statnNm"] in ["화랑대(서울여대입구)"]:
                        grouped_data["direction_1"].append(data)
                    elif data["statnNm"] in ["태릉입구"]:
                        grouped_data["direction_2"].append(data)
                    elif data["statnNm"] in ["석계"]:
                        grouped_data["direction_3"].append(data)
                    else:
                        grouped_data["direction_4"].append(data)

            return render(request, self.template_name, {'grouped_data': grouped_data})

        except requests.exceptions.RequestException as e:
            return render(request, 'bus_error_net.html', {'error_message': 'API 서버에 연결할 수 없습니다.'})

        except ET.ParseError as e:
            return render(request, 'bus_error_xml.html', {'error_message': 'XML 데이터를 파싱할 수 없습니다.'})

class mobile_info_graduate(TemplateView):
    template_name = 'mobile/m_info_graduate.html'  # 모바일 전용 템플릿

class mobile_info_shuttle(TemplateView):
    template_name = 'mobile/m_info_shuttle.html'  # 모바일 전용 템플릿
    def get_weekday_timetable(self):
        # 월요일부터 목요일까지 시간표를 반환합니다.
        timetable = {
            "화랑대 -> 학교": ["08:10", "08:15", "08:20", "08:25", "08:30", "08:35", "08:40", "08:45", "08:50", "08:55", "09:00", "09:05", "09:10", "09:15", "09:20", "09:25", "09:30", "09:35", "09:40", "09:45", "09:50", "09:55", "10:00", "10:20", "10:40", "11:00", "11:20", "11:40", "12:00"],
            "태릉입구, 석계 -> 학교": ["12:00", "12:25", "12:50", "13:15", "13:40", "14:05", "14:30", "15:00", "15:20", "15:40", "16:00", "16:20", "16:40", "17:00", "17:20", "17:40", "18:00", "18:15"],
            "별내 -> 학교": ["08:40", "09:40", "10:40", "11:40", "12:40", "13:40", "14:40", "15:40", "16:40", "17:40"],
            "학교 -> 태릉입구, 석계": ["12:00", "12:25", "12:50", "13:15", "13:40", "14:05", "14:30", "15:00", "15:20", "15:40", "16:00", "16:20", "16:40", "17:00", "17:20", "17:40", "18:00", "18:15"],
            "학교 -> 별내": ["10:25", "11:25", "12:25", "13:25", "14:25", "15:25", "16:25", "17:25"],
            # 나머지 노선 시간표도 추가
        }
        return timetable

    def get_friday_timetable(self):
        # 금요일 시간표를 반환합니다.
        timetable = {
            "화랑대 -> 학교": ["08:10", "08:15", "08:20", "08:25", "08:30", "08:35", "08:40", "08:45", "08:50", "08:55", "09:00", "09:05", "09:10", "09:15", "09:20", "09:25", "09:30", "09:35", "09:40", "09:50", "09:55", "10:00", "10:20", "10:40", "11:00", "11:20", "11:40", "12:00"],
            "태릉입구, 석계 -> 학교": ["12:00", "12:25", "12:50", "13:15", "13:40", "14:05", "14:30", "15:00", "15:20", "15:30"],
            "별내 -> 학교": ["08:40", "09:40", "10:40", "11:40", "12:40", "13:40", "14:40", "15:40"],
            "학교 -> 태릉입구, 석계": ["12:00", "12:25", "12:50", "13:15", "13:40", "14:05", "14:30", "15:00", "15:20", "15:40"],
            "학교 -> 별내": ["10:25", "11:25", "12:25", "13:25", "14:25", "15:25"],
            # 나머지 노선 시간표도 추가
        }
        return timetable

    def get_weekend_timetable():
        # 주말 시간표를 반환합니다.
        timetable = {
            "전체 노선": ["운행 종료"],
        }

        return timetable

    def get(self, request):
        # 현재 시간을 가져옵니다.
        now = datetime.now()

        # 현재 요일을 가져옵니다. (월요일: 0, 일요일: 6)
        current_weekday = now.weekday()

        left_info = {}
        right_info = {}

        # 남은 시간을 계산합니다.
        remaining_times = {}
        if 0 <= current_weekday < 4:  # 월요일부터 목요일까지
            timetable = get_weekday_timetable()
        elif current_weekday == 4:  # 금요일
            timetable = get_friday_timetable()
        else:  # 토요일과 일요일
            weekend_timetable = get_weekend_timetable()
            left_info, right_info = weekend_timetable, weekend_timetable  # 주말은 left_info와 right_info에 둘 다 할당
            timetable = weekend_timetable  # 이 부분이 빠져있어서 발생한 오류입니다.

        for shuttle, times in timetable.items():
            next_departure_time = None
            for time_str in times:
                if time_str == "운행 종료":
                    remaining_times[shuttle] = "운행 종료"
                    if len(left_info) < 3:
                        left_info[shuttle] = "운행 종료"
                    else:
                        right_info[shuttle] = "운행 종료"
                    break
                departure_time = datetime.strptime(time_str, "%H:%M")
                departure_time = departure_time.replace(year=now.year, month=now.month, day=now.day)  # 현재 날짜 정보 추가
                if departure_time > now:
                    next_departure_time = departure_time
                    break

            if next_departure_time is not None:
                time_difference = next_departure_time - now
                remaining_minutes = int(time_difference.total_seconds() / 60)  # 초를 분으로 변환
                remaining_times[shuttle] = f"{remaining_minutes} 분 남았습니다."  # 분을 붙여서 저장
                if len(left_info) < 3:
                    left_info[shuttle] = f"{remaining_minutes} 분 남았습니다."
                else:
                    right_info[shuttle] = f"{remaining_minutes} 분 남았습니다."
            else:
                remaining_times[shuttle] = "운행 종료"  # next_departure_time이 None인 경우 처리
                if len(left_info) < 3:
                    left_info[shuttle] = "운행 종료"
                else:
                    right_info[shuttle] = "운행 종료"

        return render(request, self.template_name, {'left_info': left_info, 'right_info': right_info})

class mobile_info_gabean(TemplateView):
    template_name = 'mobile/m_info_gabean.html'  # 모바일 전용 템플릿

class mobile_sound_kong(TemplateView):
    template_name = 'mobile/m_sound_kong.html'  # 모바일 전용 템플릿
    def get(self, request):
        posts = Post.objects.all()
        return render(request, self.template_name, {'posts': posts})

class mobile_sound_kong_write(TemplateView):
    template_name = 'mobile/m_sound_kong_write.html'  # 모바일 전용 템플릿

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        title = request.POST['title']
        content = request.POST['content']
        Post.objects.create(title=title, content=content)
        return redirect('gabean_mobile:m_sound_kong')

class mobile_sound_kong_detail(TemplateView):
    template_name = 'mobile/m_sound_kong_detail.html'  # 모바일 전용 템플릿
    def get(self, request, post_id):
        post = Post.objects.get(id=post_id)
        return render(request, self.template_name, {'post': post})

class mobile_campusmap(TemplateView):
    template_name = 'mobile/m_campusmap.html'  # 모바일 전용 템플릿

class mobile_campusmap_detail(TemplateView):
    template_name = 'mobile/m_campusmap_detail.html'  # 모바일 전용 템플릿

class mobile_get_all_restaurant(TemplateView):
    def get_all_restaurant(self, request):
        # 모든 'type' 데이터 가져오기
        types = list(HumunFood.objects.exclude(type='카페').values_list('type', flat=True).distinct())
        items = list(HumunFood.objects.exclude(type='카페').values_list('name', flat=True).distinct())
        return JsonResponse({'types': types, 'items': items})
class mobile_humun_random(TemplateView):
    template_name = 'mobile/m_humun_random.html'  # 모바일 전용 템플릿

    def get(self, request):
        return render(request, self.template_name)

def some_view(request):
    user_agent = request.META['HTTP_USER_AGENT']
    if 'Mobile' in user_agent:
        return HttpResponseRedirect('http://m.gabean.kr')
    else:
        return HttpResponseRedirect('http://gabean.kr')

class mobile_news_search(TemplateView):
    template_name = 'mobile/m_news.html'  # 모바일 전용 템플릿
    def get(self, request):

        # 네이버 검색 API를 호출할 URL을 설정합니다.
        url = "https://openapi.naver.com/v1/search/news.json"

        # URL 파라미터에서 검색어를 가져옵니다. 기본값은 빈 문자열입니다.
        query = request.GET.get('query', '')

        if query:
            # API를 호출할 때 사용할 파라미터를 설정합니다.
            params = {'query': query, 'display': 10}

            # API를 호출할 때 사용할 헤더를 설정합니다. 클라이언트 ID와 시크릿은 실제 값으로 변경해야 합니다.
            headers = {
                'X-Naver-Client-Id': '48KtNy0_eHdwWFg3vDUg',
                'X-Naver-Client-Secret': 'LFiuNrJGef'
            }

            # API를 호출하고 응답을 가져옵니다.
            response = requests.get(url, headers=headers, params=params)

            # 응답을 JSON 형식으로 파싱합니다.
            result = json.loads(response.text)

            for item in result['items']:
                item['title'] = item['title'].replace('<b>', '<strong>').replace('</b>', '</strong>')
                item['description'] = item['description'].replace('<b>', '<strong>').replace('</b>', '</strong>')
                item['pubDate'] = datetime.strptime(item['pubDate'], '%a, %d %b %Y %H:%M:%S +0900').strftime('%Y.%m.%d %H:%M')

            # 결과와 검색어를 템플릿에 전달합니다.
            return render(request, self.template_name, {'news': result['items'], 'query': query})

        else:  # 검색어가 없는 경우 빈 결과를 전달합니다.
            return render(request, self.template_name, {'news': [], 'query': query})

class mobile_info_library(TemplateView):
    template_name = 'mobile/m_info_library.html'  # 모바일 전용 템플릿

    def get(self, request):
        return render(request, self.template_name)
