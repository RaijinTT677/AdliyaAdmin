from django.contrib.auth import views as auth_views
from django.http import HttpResponseRedirect
from django.urls import path
from .views import content_list_api, increment_views_api

from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('content_list/', views.content_list, name='content_list'),
    path('add_content/', views.add_content, name='add_content'),
    path('edit_content/<int:content_id>/', views.edit_content, name='edit_content'),
    path('delete_content/<int:content_id>/', views.delete_content, name='delete_content'),
    path('api/content/', views.content_list_api, name='content_list_api'),
    path('content/', content_list_api, name='content_list_api'),
    path('content/<int:content_id>/increment_views/', increment_views_api, name='increment_views_api'),
]
