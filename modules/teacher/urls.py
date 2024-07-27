# urls.py
from django.urls import path
from . import views

urlpatterns = [
    # другие URL-обработчики
    path('teachers/', views.teachers_list, name='teachers_list'),
]
