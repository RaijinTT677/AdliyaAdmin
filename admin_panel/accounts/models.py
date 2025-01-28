from django.db import models
from PIL import Image
import imagehash
import os


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
    image_hash = models.TextField(verbose_name="Хэш изображения", blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Переопределённый метод save для автоматического вычисления хэша изображения перед сохранением.
        """
        if self.image and self.image.name:
            # Проверяем существование файла изображения
            if os.path.exists(self.image.path):
                self.image_hash = self.calculate_image_hash(self.image.path)
        super().save(*args, **kwargs)

    @staticmethod
    def calculate_image_hash(image_path, hash_size=64):
        """
        Вычисление хэша изображения с использованием phash.
        """
        try:
            with Image.open(image_path) as img:
                img = img.convert("RGB")
                img_hash = imagehash.phash(img, hash_size=hash_size)
                return str(img_hash)
        except Exception as e:
            print(f"Ошибка вычисления хэша изображения: {e}")
            return None
