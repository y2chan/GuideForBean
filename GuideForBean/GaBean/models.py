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