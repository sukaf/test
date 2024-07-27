from django.db import models
from modules.course.models import Article
from django_ckeditor_5.fields import CKEditor5Field


class Schedule(models.Model):
    course = models.ForeignKey(Article, related_name='schedules', on_delete=models.CASCADE, default=1)  # Пример значения по умолчанию
    date = models.DateField()
    time = models.TimeField()
    description = models.TextField(blank=True, null=True)
    full_description = CKEditor5Field(verbose_name='Полное описание', config_name='extends', default="")

    class Meta:
        ordering = ['date', 'time']

    def __str__(self):
        return f"{self.course.title} - {self.date} {self.time}"
