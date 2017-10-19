#-*- coding: utf-8 -*-
from django import forms
from .models import Pointing

class PointingForm(forms.ModelForm):
    class Meta:
        model = Pointing
        fields = '__all__'
