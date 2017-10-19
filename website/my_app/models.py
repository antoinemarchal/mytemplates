#-*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class Pointing(models.Model):
    lon = models.FloatField()
    lat = models.FloatField()
    size = models.IntegerField()
    
    def __str__(self):
        return "LON = {0}, LAT = {1}, SIZE = {2}".format(self.lon, self.lat, self.size)


