from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home),
    url(r'^about/$', views.about, name='about'),
    url(r'^query/$', views.query, name='query'),
    url(r'^code/$', views.code, name='code'),
    url(r'^references/$', views.references, name='references'),
]
