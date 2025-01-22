import imagehash
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import ContentForm  # Добавляем форму для работы с контентом
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Content
from .serializers import ContentSerializer
from rest_framework.parsers import MultiPartParser, FormParser
import uuid
from rest_framework.decorators import api_view
from rest_framework.response import Response
import cv2
import numpy as np
from .models import Content
from PIL import Image


# Авторизация пользователя
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('content_list')  # После входа перенаправляем на список контента
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')

    return render(request, 'accounts/login.html')


# Страница списка контента
@login_required
def content_list(request):
    contents = Content.objects.all()  # Получаем весь контент из базы
    return render(request, 'accounts/content_list.html', {'contents': contents})


# Добавление контента
@login_required
def add_content(request):
    if request.method == 'POST':
        print("🔍 Форма отправлена!")  # Проверяем, что запрос дошёл
        form = ContentForm(request.POST, request.FILES)
        if form.is_valid():
            print("✅ Форма валидна!")  # Проверяем, что форма корректная
            form.save()
            messages.success(request, "Контент успешно добавлен!")
            return redirect('content_list')
        else:
            print("❌ Ошибка в форме:", form.errors)  # Выводим ошибки формы
            messages.error(request, "Ошибка! Проверьте данные.")
    else:
        form = ContentForm()

    return render(request, 'accounts/add_content.html', {'form': form})


# Редактирование контента
@login_required
def edit_content(request, content_id):
    content = get_object_or_404(Content, id=content_id)

    if request.method == 'POST':
        form = ContentForm(request.POST, request.FILES, instance=content)
        if form.is_valid():
            form.save()
            messages.success(request, "Контент успешно обновлён!")
            return redirect('content_list')
    else:
        form = ContentForm(instance=content)

    return render(request, 'accounts/edit_content.html', {'form': form, 'content': content})


# Удаление контента
@login_required
def delete_content(request, content_id):
    content = get_object_or_404(Content, id=content_id)
    content.delete()
    messages.success(request, "Контент удалён!")
    return redirect('content_list')


@api_view(['GET'])
def content_list_api(request):
    contents = Content.objects.all()
    serializer = ContentSerializer(contents, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def increment_views_api(request, content_id):
    content = get_object_or_404(Content, id=content_id)
    content.views += 1  # Увеличиваем счётчик
    content.save()
    return Response({"message": "Просмотр засчитан", "views": content.views})


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def compare_image_api(request):
    print(f"🔍 Получен запрос: {request.method}")
    print(f"🔍 Данные запроса: {request.data}")

    # Проверка наличия файла в запросе
    if 'file' not in request.data:
        return Response({"error": "Нет файла в запросе"}, status=400)

    # Получаем загруженный файл и вычисляем его хэш
    uploaded_file = request.data['file']
    try:
        uploaded_image = Image.open(uploaded_file)
        uploaded_image_hash = str(imagehash.phash(uploaded_image))
        print(f"🔍 Хэш загруженного изображения: {uploaded_image_hash}")
    except Exception as e:
        return Response({"error": f"Не удалось обработать изображение: {str(e)}"}, status=400)

    # Фильтруем активные контенты с названием и хэшем
    active_contents = Content.objects.filter(is_active=True).exclude(name__isnull=True).exclude(name__exact='')
    print(f"🔍 Найдено активных контентов: {active_contents.count()}")

    closest_match = None
    smallest_difference = float('inf')

    # Сравниваем хэши изображений
    for content in active_contents:
        if content.image_hash:  # Проверяем, что у контента есть хэш
            existing_hash = imagehash.hex_to_hash(content.image_hash)
            difference = uploaded_image_hash - existing_hash  # Сравниваем хэши
            print(f"🔍 Сравнение с {content.name}: разница {difference}")

            if difference < smallest_difference:  # Если это лучшее совпадение
                smallest_difference = difference
                closest_match = content

    # Если совпадение найдено, возвращаем информацию
    if closest_match:
        return Response({
            "message": "Совпадение найдено!",
            "content_name": closest_match.name,
            "content_file": closest_match.file.url,
            "difference": smallest_difference
        }, status=200)

    # Если совпадения не найдено
    return Response({"message": "Совпадений не найдено."}, status=404)