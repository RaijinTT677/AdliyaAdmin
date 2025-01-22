# Generated by Django 5.1.4 on 2025-01-06 07:49

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('file', models.FileField(upload_to='uploads/', verbose_name='Файл')),
                ('format', models.CharField(choices=[('audio', 'Аудио'), ('video', 'Видео'), ('document', 'Документ'), ('other', 'Другое')], max_length=20, verbose_name='Формат')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активен')),
                ('views', models.IntegerField(default=0, verbose_name='Просмотры')),
            ],
        ),
    ]
