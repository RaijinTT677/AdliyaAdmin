from django.db import models
import cv2
import numpy as np

class Content(models.Model):
    FORMAT_CHOICES = [
        ('mp3', 'MP3'),
        ('mp4', 'MP4'),
        ('pdf', 'PDF'),
        ('other', 'Другое'),
    ]

    name = models.CharField(max_length=255, verbose_name="Название")
    file = models.FileField(upload_to='uploads/', verbose_name="Файл")
    image = models.ImageField(upload_to='images/', verbose_name="Изображение", null=True, blank=True)
    format = models.CharField(max_length=20, choices=FORMAT_CHOICES, verbose_name="Формат")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    views = models.IntegerField(default=0, verbose_name="Просмотры")
    image_hash = models.CharField(max_length=64, verbose_name="Хэш изображения", blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.image:
            self.image_hash = self.calculate_image_hash(self.image)
        super().save(*args, **kwargs)

    @staticmethod
    def calculate_image_hash(image_field):
        # Вычисление хэша изображения
        image = cv2.imdecode(np.frombuffer(image_field.read(), np.uint8), cv2.IMREAD_GRAYSCALE)
        resized = cv2.resize(image, (8, 8), interpolation=cv2.INTER_AREA)
        mean = resized.mean()
        hash_value = ''.join('1' if pixel > mean else '0' for pixel in resized.flatten())
        return hash_value
