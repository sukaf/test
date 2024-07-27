from django import forms
from .models import Schedule


class ScheduleAdminForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = '__all__'


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    form = ScheduleAdminForm
    list_display = ('course', 'date', 'time', 'description')
    search_fields = ('course__title', 'date', 'time')
    list_filter = ('course', 'date')
    ordering = ('date', 'time')
