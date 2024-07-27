from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from modules.course.utils import image_compress  # Подключаем функцию image_compress


class Teacher(models.Model):
    name = models.CharField(max_length=255, verbose_name='Имя преподавателя')
    description = models.TextField(verbose_name='Описание', blank=True)
    photo = models.ImageField(upload_to='teachers/photos/', verbose_name='Фото', blank=True, null=True)

    class Meta:
        verbose_name = 'Преподаватель'
        verbose_name_plural = 'Преподаватели'

    def __str__(self):
        return self.name


@receiver(post_save, sender=Teacher)
def teacher_post_save(sender, instance, created, **kwargs):
    if not created and instance.photo:
        image_compress(instance.photo.path, width=150, height=100)
