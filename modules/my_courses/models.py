from django.db import models
from django.contrib.auth.models import User
from modules.course.models import Article


class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    date_enrolled = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    class Meta:
        unique_together = ('user', 'article')


class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.article.title}'
