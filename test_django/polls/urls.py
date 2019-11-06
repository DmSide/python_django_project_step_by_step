from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('background_view', views.background_view, name='background_view'),
]