from .views import content_list_api, increment_views_api
from django.urls import path
from .views import compare_image_api, get_images_api

print("🔧 api_urls.py загружен!")
urlpatterns = [
    path('content/', content_list_api, name='content_list_api'),
    path('content/<int:content_id>/increment_views/', increment_views_api, name='increment_views_api'),
    path('content/compare/', compare_image_api, name='compare_image_api'),
    path('content/images/', get_images_api, name='get_images_api'),  # Новый маршрут
]
