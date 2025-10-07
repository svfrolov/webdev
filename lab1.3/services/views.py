"""
Представления для работы с коллекциями данных без использования БД
"""
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from .data_collections import real_estates, order, add_property_to_order, remove_property_from_order, calculate_total_price
from .minio_storage import MinioStorage

def real_estate_list(request):
    """
    Представление для отображения списка объектов недвижимости
    """
    # Копируем список объектов недвижимости, чтобы не изменять оригинал
    properties = real_estates.copy()
    
    # Обработка поиска
    search_query = request.GET.get('search', '')
    if search_query:
        # Фильтрация по наименованию (строго по методичке)
        properties = [
            prop for prop in properties 
            if search_query.lower() in prop['name'].lower()
        ]
    
    # Генерируем URL изображений из Minio
    minio_storage = MinioStorage()
    for prop in properties:
        if prop['image_key']:
            prop['image_url'] = minio_storage.get_image_url(prop['image_key'])
    
    context = {
        'real_estates': properties,
        'draft_order': order if order['items'] else None,  # Передаем заявку только если в ней есть объекты
        'search_query': search_query,  # Сохраняем поисковый запрос для отображения в форме
    }
    
    return render(request, 'services/real_estate_list.html', context)

def real_estate_detail(request, property_id):
    """
    Представление для отображения детальной информации об объекте недвижимости
    """
    # Находим объект недвижимости по ID
    property_obj = None
    for prop in real_estates:
        if prop['id'] == property_id:
            property_obj = prop
            break
    
    if not property_obj:
        raise Http404("Объект недвижимости не найден")
    
    # Генерируем URL изображения из Minio
    minio_storage = MinioStorage()
    if property_obj['image_key']:
        property_obj['image_url'] = minio_storage.get_image_url(property_obj['image_key'])
    
    context = {
        'real_estate': property_obj,
        'draft_order': order if order['items'] else None,  # Передаем заявку только если в ней есть объекты
    }
    
    return render(request, 'services/real_estate_detail.html', context)

def order_detail(request, order_id):
    """
    Представление для отображения информации о заявке
    """
    # Проверяем, соответствует ли ID заявки
    if order['id'] != order_id:
        raise Http404("Заявка не найдена")
    
    # Генерируем URL изображений из Minio для объектов в заявке
    minio_storage = MinioStorage()
    for item in order['items']:
        if item['real_estate']['image_key']:
            item['real_estate']['image_url'] = minio_storage.get_image_url(item['real_estate']['image_key'])
    
    # Рассчитываем общую стоимость
    total_price = calculate_total_price()
    
    context = {
        'order': order,
        'order_properties': order['items'],
        'total_price': total_price
    }
    
    return render(request, 'services/order_detail.html', context)

def add_to_order(request, property_id):
    """
    Представление для добавления объекта недвижимости в заявку
    """
    if request.method == 'POST':
        add_property_to_order(property_id)
        
        # Определяем, откуда пришел запрос
        referer = request.META.get('HTTP_REFERER', '')
        if f'/real-estates-page/{property_id}/' in referer:
            # Если с детальной страницы объекта, возвращаемся на нее
            return redirect('services:real-estate-detail-page', property_id=property_id)
        else:
            # Иначе возвращаемся на список объектов
            return redirect('services:real-estate-list-page')
    
    # Если не POST, перенаправляем на список объектов
    return redirect('services:real-estate-list-page')

def remove_from_order(request, order_id, item_id):
    """
    Представление для удаления объекта недвижимости из заявки
    """
    if request.method == 'POST':
        remove_property_from_order(item_id)
    
    return redirect('services:order-detail-page', order_id=order_id)