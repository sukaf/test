from django.contrib import admin
from .models import Schedule


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('course', 'date', 'time', 'description')
    search_fields = ('course__title', 'date', 'time')
    list_filter = ('course', 'date')
    ordering = ('date', 'time')
