import os
import sys
from django.core.wsgi import get_wsgi_application

sys.path.append("C:\\Users\\y2chan\\Desktop\\GuideForBean\\GuideForBean")  # 프로젝트 루트 디렉토리 추가
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "GuideForBean.settings")
application = get_wsgi_application()

import requests
from GaBean.models import Restaurant  # 모델 임포트

def get_and_save_restaurants():
    api_key = "e3f403961290597b9a92ea2b725a350f"
    latitude = "37.64389652257"
    longitude = "127.11087695220976"
    radius = 180  # 180미터 반경

    url = f"https://dapi.kakao.com/v2/local/search/category.json?category_group_code=FD6&x={longitude}&y={latitude}&radius={radius}"

    headers = {
        "Authorization": f"KakaoAK {api_key}"
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    for place in data.get("documents", []):
        name = place.get("place_name")
        category = place.get("category_name")
        open_hours = place.get("open_time", "정보 없음")

        # 모델에 데이터 추가
        restaurant = Restaurant(name=name, category=category, open_hours=open_hours)
        restaurant.save()