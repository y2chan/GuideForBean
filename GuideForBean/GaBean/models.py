from django.db import models

class Building(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    text = models.CharField(max_length=400)

    class Meta:
        app_label = 'GaBean'

    def __str__(self):
        return self.name

class Restaurant(models.Model):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    open_hours = models.CharField(max_length=100, default="정보 없음")

    class Meta:
        app_label = 'GaBean'

    def __str__(self):
        return self.name
