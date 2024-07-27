# views.py
from django.shortcuts import render
from .models import Teacher


def teachers_list(request):
    teachers = Teacher.objects.all()
    return render(request, 'teachers/teachers_list.html', {'teachers': teachers})
