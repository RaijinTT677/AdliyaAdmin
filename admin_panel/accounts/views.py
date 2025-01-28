from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import ContentForm
from .serializers import ContentSerializer
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from .models import Content
import cv2
import numpy as np
import torch
from torchvision import models, transforms
from PIL import Image
from scipy.spatial.distance import cosine

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

# API для получения списка контента
@api_view(['GET'])
def content_list_api(request):
    contents = Content.objects.all()
    serializer = ContentSerializer(contents, many=True)
    return Response(serializer.data)

# API для увеличения количества просмотров
@api_view(['POST'])
def increment_views_api(request, content_id):
    content = get_object_or_404(Content, id=content_id)
    content.views += 1  # Увеличиваем счётчик
    content.save()
    return Response({"message": "Просмотр засчитан", "views": content.views})


# Загрузка предобученной модели
model = models.resnet18(pretrained=True)
model.eval()  # Перевод в режим оценки









# Кэширование модели ResNet50
resnet50_model = torch.nn.Sequential(*list(models.resnet50(pretrained=True).children())[:-1])
resnet50_model.eval()

def extract_colored_regions(image):
    """
    Извлекает области с красной обводкой, игнорируя мелкие контуры.
    """
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([150, 120, 70])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv_image, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv_image, lower_red2, upper_red2)
    combined_mask = cv2.bitwise_or(mask1, mask2)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    regions = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 10000:
            continue
        x, y, w, h = cv2.boundingRect(contour)
        region = image[y:y + h, x:x + w]
        regions.append((region, (x, y, w, h)))

    return regions, combined_mask

def extract_features(image):
    """
    Извлекает эмбеддинги изображения с использованием кэшированной ResNet50.
    """
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    image_tensor = transform(image_pil).unsqueeze(0)

    with torch.no_grad():
        features = resnet50_model(image_tensor).squeeze().numpy()

    return features

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def compare_image_api(request):
    """
    Сравнение изображения из запроса с активными изображениями на сервере.
    Возвращает файл с наибольшим процентом схожести.
    """
    print("🔍 compare_image_api вызван!")  # Проверка вызова
    if 'file' not in request.data:
        print("❌ Нет файла в запросе")
        return Response({"error": "Нет файла в запросе"}, status=400)

    uploaded_file = request.data['file']
    print("📥 Файл получен")

    try:
        uploaded_image = Image.open(uploaded_file).convert("RGB")
        uploaded_image_array = np.array(uploaded_image)
        print("✅ Изображение преобразовано в массив")

        # Извлечение красных областей
        regions, _ = extract_colored_regions(uploaded_image_array)
        print(f"🔍 Найдено {len(regions)} регионов")
        if not regions:
            return Response({"message": "Области интереса не найдены."}, status=200)

        active_contents = Content.objects.filter(is_active=True)
        similarity_results = []

        for content in active_contents:
            if content.image and content.image.path:
                try:
                    content_image = cv2.imread(content.image.path)
                    if content_image is None:
                        print(f"⚠️ Не удалось загрузить изображение: {content.name}")
                        continue

                    for region, _ in regions:
                        content_features = extract_features(content_image)
                        region_features = extract_features(region)
                        similarity = 1 - cosine(region_features, content_features)
                        similarity_percentage = similarity * 100

                        similarity_results.append((content, similarity_percentage))
                        print(f"Сравнение с {content.name}: схожесть {similarity_percentage:.2f}%")

                except Exception as e:
                    print(f"⚠️ Ошибка при обработке контента {content.name}: {e}")

        if similarity_results:
            best_match, best_similarity = max(similarity_results, key=lambda x: x[1])
            return Response({
                "message": "Совпадение найдено!",
                "content_name": best_match.name,
                "content_file": best_match.file.url,
                "similarity": round(best_similarity, 2)
            }, status=200)

        return Response({"message": "Совпадений не найдено."}, status=200)

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return Response({"error": f"Ошибка обработки изображения: {e}"}, status=400)