from django import forms
from .models import HumunFood

class HumunFoodForm(forms.ModelForm):
    class Meta:
        model = HumunFood
        fields = '__all__'
