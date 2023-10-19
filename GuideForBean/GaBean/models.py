from django.db import models

class Restaurant(models.Model):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    content = models.TextField(default='')

    class Meta:
        app_label = 'GaBean'

    def __str__(self):
        return self.name

class Restaurant_time(models.Model):
    name = models.ForeignKey(Restaurant, on_delete=models.CASCADE, default='')
    day_week = models.CharField(max_length=100, default="")
    open_hours = models.TimeField
    close_hours = models.TimeField

    class Meta:
        app_label = 'GaBean'

    def __str__(self):
        return self.name


class Bus_arrival_info(models.Model):
    bus_stop_location = models.CharField(max_length=100)  # 버스 정류장 위치
    bus_number = models.CharField(max_length=20)  # 버스 번호
    arrival_time = models.DateTimeField()  # 버스 도착 예정 시간

    class Meta:
        app_label = 'GaBean'

    def __str__(self):
        return f"{self.bus_stop_location} - {self.bus_number} - {self.arrival_time}"

class HumunFood(models.Model):
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=100)
    phone = models.CharField(max_length=50, default='번호 없음')
    content = models.TextField()

    def __str__(self):
        return self.name

class OpeningHours(models.Model):
    WEEK_CHOICES = [
        ('월요일', '월요일'),
        ('화요일', '화요일'),
        ('수요일', '수요일'),
        ('목요일', '목요일'),
        ('금요일', '금요일'),
        ('토요일', '토요일'),
        ('일요일', '일요일'),
        ('매일', '매일'),
        ('휴무', '휴무'),
    ]

    week = models.CharField(max_length=50, choices=WEEK_CHOICES)
    open_time = models.TimeField()
    close_time = models.TimeField()
    restaurant = models.ForeignKey(HumunFood, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.restaurant.name} - {self.week} 영업시간"


class Post(models.Model):
    title = models.CharField(max_length=20)
    content = models.TextField(max_length=300)
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title