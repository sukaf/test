# set_courses/urls.py

from django.urls import path
from .views import course_detail, schedule_data

urlpatterns = [
    path('course/<slug:slug>/', course_detail, name='course_detail'),
    path('schedule-data/<slug:slug>/', schedule_data, name='schedule_data'),  # Новый маршрут для данных расписания
]
