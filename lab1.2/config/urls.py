"""
URL configuration for lab3 project (adapted for lab1 requirements).
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Используем упрощенные URL-маршруты вместо API
    path('', include('services.urls_simple')),
    # Оставляем оригинальные API URL для совместимости
    path('api/', include('services.urls')),
    path('api-auth/', include('rest_framework.urls')),
]

# Добавляем обработку статических и медиа файлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)