from django.urls import path
from rango import views

app_name = 'rango'

urlpatterns = [
    path ('rango/', views.index, name='index',),
    path('rango/about/', views.about, name='about'),
]