from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from modules.course.models import Article
from .models import Schedule


def course_detail(request, slug):
    course = get_object_or_404(Article, slug=slug)
    schedules = Schedule.objects.filter(course=course).order_by('date', 'time')
    return render(request, 'set_courses/course_detail.html', {
        'course': course,
        'schedules': schedules,
        'course_slug': course.slug  # Добавьте slug курса
    })


def schedule_data(request, slug):
    course = get_object_or_404(Article, slug=slug)
    schedules = Schedule.objects.filter(course=course)
    events = []
    for schedule in schedules:
        events.append({
            'title': schedule.course.title,
            'start': schedule.date.isoformat(),
            'description': schedule.description,
            'full_description': schedule.full_description,
        })
    return JsonResponse(events, safe=False)
