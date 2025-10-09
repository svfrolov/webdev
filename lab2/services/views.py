from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.db import connection
from .models import RealEstate, Order, OrderRealEstate
from .minio_storage import MinioStorage

def real_estate_list(request):
    """
    Представление для отображения списка объектов недвижимости
    """
    # Получаем только активные объекты недвижимости
    properties = RealEstate.objects.filter(is_active=True)
    
    # Обработка поиска
    search_query = request.GET.get('search', '')
    if search_query:
        # Фильтрация по наименованию
        properties = properties.filter(name__icontains=search_query)
    
    # Генерируем URL изображений из Minio
    minio_storage = MinioStorage()
    for prop in properties:
        if prop.image_key:
            prop.image_url = minio_storage.get_image_url(prop.image_key)
    
    # Получаем черновик заявки для текущего пользователя
    draft_order = None
    if request.user.is_authenticated:
        draft_order = Order.get_draft_order(request.user)
    
    context = {
        'real_estates': properties,
        'draft_order': draft_order,
        'search_query': search_query,
    }
    
    return render(request, 'services/real_estate_list.html', context)

def real_estate_detail(request, property_id):
    """
    Представление для отображения детальной информации об объекте недвижимости
    """
    # Находим объект недвижимости по ID
    property_obj = get_object_or_404(RealEstate, pk=property_id, is_active=True)
    
    # Генерируем URL изображения из Minio
    minio_storage = MinioStorage()
    if property_obj.image_key:
        property_obj.image_url = minio_storage.get_image_url(property_obj.image_key)
    
    # Получаем черновик заявки для текущего пользователя
    draft_order = None
    if request.user.is_authenticated:
        draft_order = Order.get_draft_order(request.user)
    
    context = {
        'real_estate': property_obj,
        'draft_order': draft_order,
    }
    
    return render(request, 'services/real_estate_detail.html', context)

@login_required
def order_detail(request, order_id):
    """
    Представление для отображения информации о заявке
    """
    # Находим заявку по ID и проверяем, что она принадлежит текущему пользователю и не удалена
    order = get_object_or_404(Order, pk=order_id, creator=request.user)
    
    # Если заявка удалена, возвращаем 404
    if order.status == 'deleted':
        raise Http404("Заявка не найдена или была удалена")
    
    # Получаем объекты недвижимости в заявке
    order_properties = order.orderrealestate_set.all().select_related('real_estate')
    
    # Генерируем URL изображений из Minio
    minio_storage = MinioStorage()
    for item in order_properties:
        if item.real_estate.image_key:
            item.real_estate.image_url = minio_storage.get_image_url(item.real_estate.image_key)
    
    # Рассчитываем общую стоимость
    total_price = order.calculate_total_price()
    
    context = {
        'order': order,
        'order_properties': order_properties,
        'total_price': total_price
    }
    
    return render(request, 'services/order_detail.html', context)

@login_required
def add_to_order(request, property_id):
    """
    Представление для добавления объекта недвижимости в заявку
    """
    if request.method == 'POST':
        # Находим объект недвижимости
        property_obj = get_object_or_404(RealEstate, pk=property_id, is_active=True)
        
        # Получаем или создаем черновик заявки для текущего пользователя
        draft_order = Order.get_draft_order(request.user)
        if not draft_order:
            draft_order = Order.create_draft_order(request.user)
        
        # Проверяем, есть ли уже этот объект в заявке
        order_property, created = OrderRealEstate.objects.get_or_create(
            order=draft_order,
            real_estate=property_obj,
            defaults={
                'quantity': 1,
                'order_number': draft_order.orderrealestate_set.count() + 1,
                'is_main': draft_order.orderrealestate_set.count() == 0,
                'discount_percent': 0,
                'final_price': property_obj.price
            }
        )
        
        # Если объект уже был в заявке, увеличиваем количество
        if not created:
            order_property.quantity += 1
            order_property.final_price = property_obj.price * order_property.quantity * (1 - order_property.discount_percent / 100)
            order_property.save()
        
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

@login_required
def remove_from_order(request, order_id, item_id):
    """
    Представление для удаления объекта недвижимости из заявки
    """
    if request.method == 'POST':
        # Находим заявку
        order = get_object_or_404(Order, pk=order_id, creator=request.user, status='draft')
        
        # Находим объект в заявке
        order_property = get_object_or_404(OrderRealEstate, pk=item_id, order=order)
        
        # Удаляем объект из заявки
        order_property.delete()
        
        # Обновляем порядковые номера оставшихся объектов
        for i, item in enumerate(order.orderrealestate_set.all().order_by('order_number'), 1):
            item.order_number = i
            item.is_main = (i == 1)
            item.save()
    
    return redirect('services:order-detail-page', order_id=order_id)

@login_required
def delete_order(request, order_id):
    """
    Представление для логического удаления заявки (изменение статуса на "удален")
    Используем SQL запрос напрямую, без ORM
    """
    if request.method == 'POST':
        # Находим заявку
        order = get_object_or_404(Order, pk=order_id, creator=request.user)
        
        # Используем SQL запрос для логического удаления заявки
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE services_order SET status = %s WHERE id = %s AND creator_id = %s",
                ['deleted', order_id, request.user.id]
            )
        
        return redirect('services:real-estate-list-page')
    
    return redirect('services:order-detail-page', order_id=order_id)