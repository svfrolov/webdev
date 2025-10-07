from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    # Страницы приложения
    path('real-estates-page/', views.real_estate_list, name='real-estate-list-page'),
    path('real-estates-page/<int:property_id>/', views.real_estate_detail, name='real-estate-detail-page'),
    path('orders-page/<int:order_id>/', views.order_detail, name='order-detail-page'),
    
    # URL для добавления объекта недвижимости в заявку
    path('real-estates/<int:property_id>/add-to-order/', views.add_to_order, name='add-property-to-order'),
    
    # URL для удаления объекта недвижимости из заявки
    path('orders/<int:order_id>/remove-property/<int:item_id>/', views.remove_from_order, name='remove-property-from-order'),
]