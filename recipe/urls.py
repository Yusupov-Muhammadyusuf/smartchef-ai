from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='index'),
    path('generate/', views.generate_recipe, name='generate_recipe'),
]