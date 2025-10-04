from django.urls import path
from . import views_simple
from . import views_minio

# Удаляем пространство имен для простоты
# app_name = 'services'

urlpatterns = [
    path('', views_simple.GetOrders, name='real-estate-list-page'),
    # Изменяем путь с 'property/<int:id>/' на 'order/<int:id>/' для соответствия методичке
    path('order/<int:id>/', views_simple.GetOrder, name='order_url'),
    path('hello/', views_simple.hello, name='hello'),
    path('sendText', views_simple.sendText, name='sendText'),
    
    # Маршруты для работы с MinIO
    path('minio/', views_minio.hello, name='minio_hello'),
    path('upload/', views_minio.upload_file, name='upload_file'),
]