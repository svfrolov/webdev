"""
URL configuration for the project.
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('services/', include('services.urls')),
    path('', lambda request: redirect('services:real-estate-list-page'), name='home'),
]