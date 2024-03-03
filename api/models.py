from django.db import models
from django.contrib.auth.models import User


class Product(models.Model):

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ['name', ]

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    start_datetime = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    min_student = models.PositiveIntegerField(default=0)
    max_student = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} | Цена {self.price}"


class Lesson(models.Model):

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    video_link = models.URLField()

    def __str__(self):
        return self.product.name


class Group(models.Model):

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
        ordering = ['name', ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User, related_name='group_members')

    def __str__(self):
        return f"{self.name} | Количество участников {self.members.count()}"