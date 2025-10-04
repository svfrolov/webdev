from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'services'

# Создаем router для автоматической генерации URL-адресов для ViewSet
router = DefaultRouter()
router.register(r'real-estates', views.RealEstateViewSet, basename='realestate')
router.register(r'orders', views.OrderViewSet, basename='order')

urlpatterns = [
    # Корневой URL API
    path('', views.api_root, name='api-root'),
    # Включаем URL-адреса, сгенерированные router
    path('', include(router.urls)),
    
    # URL для логического удаления заявки через SQL
    path('orders/<int:order_id>/delete-sql/', views.delete_order_sql, name='delete-order-sql'),
    
    # URL для добавления объекта недвижимости в заявку
    path('real-estates/<int:property_id>/add-to-order/', views.add_property_to_order, name='add-property-to-order'),
    
    # URL для удаления объекта недвижимости из заявки
    path('orders/<int:order_id>/remove-property/<int:property_id>/', views.remove_property_from_order, name='remove-property-from-order'),
    
    # URL для формирования заявки
    path('orders/<int:order_id>/form/', views.form_order, name='order-form'),
    
    # URL для страниц приложения
    path('real-estates-page/', views.real_estate_list, name='real-estate-list-page'),
    path('real-estates-page/<int:property_id>/', views.real_estate_detail, name='real-estate-detail-page'),
    path('orders-page/<int:order_id>/', views.order_detail, name='order-detail-page'),
]