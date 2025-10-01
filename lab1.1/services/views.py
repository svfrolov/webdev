from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from django.db import connection
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q, Sum, F, ExpressionWrapper, DecimalField
from django.contrib import messages
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse as api_reverse
from rest_framework import viewsets, permissions, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.decorators import action
from .models import RealEstate, Order, OrderRealEstate
from .serializers import RealEstateSerializer, OrderSerializer, OrderRealEstateSerializer
import decimal


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request, format=None):
    """
    Корневая точка API, отображающая доступные эндпоинты.
    """
    return Response({
        'welcome': 'Добро пожаловать в API продажи недвижимости',
        'real_estates': api_reverse('services:realestate-list', request=request, format=format),
        'orders': api_reverse('services:order-list', request=request, format=format),
        'status': 'API работает корректно',
        'version': 'v1.0',
    })


class RealEstateViewSet(viewsets.ModelViewSet):
    """
    API endpoint для работы с объектами недвижимости.
    """
    queryset = RealEstate.objects.filter(is_active=True)
    serializer_class = RealEstateSerializer
    
    def get_permissions(self):
        """
        Разрешения:
        - Просмотр доступен всем
        - Создание, изменение и удаление доступно только администраторам
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]


class OrderViewSet(viewsets.ModelViewSet):
    """
    API endpoint для работы с заявками.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Пользователи видят только свои заявки.
        Администраторы видят все заявки.
        """
        user = self.request.user
        if user.is_staff:
            return Order.objects.exclude(status='deleted')
        return Order.objects.filter(creator=user).exclude(status='deleted')
    
    def perform_create(self, serializer):
        """
        При создании заявки автоматически устанавливаем текущего пользователя как создателя
        """
        serializer.save(creator=self.request.user)
    
    @action(detail=True, methods=['post'])
    def form_order(self, request, pk=None):
        """
        Формирование заявки создателем
        """
        order = self.get_object()
        
        if order.creator != request.user:
            return Response({"error": "Вы не можете формировать чужие заявки"}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            order.form_order()
            return Response({"status": "Заявка успешно сформирована"})
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def complete_order(self, request, pk=None):
        """
        Завершение заявки модератором
        """
        if not request.user.is_staff:
            return Response({"error": "Только модераторы могут завершать заявки"}, status=status.HTTP_403_FORBIDDEN)
        
        order = self.get_object()
        
        try:
            order.complete_order(moderator=request.user)
            return Response({"status": "Заявка успешно завершена", "total_price": order.total_price, "delivery_date": order.estimated_delivery_date})
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def reject_order(self, request, pk=None):
        """
        Отклонение заявки модератором
        """
        if not request.user.is_staff:
            return Response({"error": "Только модераторы могут отклонять заявки"}, status=status.HTTP_403_FORBIDDEN)
        
        order = self.get_object()
        
        try:
            order.reject_order(moderator=request.user)
            return Response({"status": "Заявка отклонена"})
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@login_required
@require_http_methods(["POST"])
def delete_order_sql(request, order_id):
    """
    Логическое удаление заявки через SQL запрос UPDATE (без ORM)
    """
    # Проверяем, что заявка принадлежит текущему пользователю
    order = get_object_or_404(Order, id=order_id)
    
    if order.creator != request.user and not request.user.is_staff:
        return HttpResponseForbidden("Вы не можете удалить чужую заявку")
    
    # Проверяем, что заявка находится в статусе черновик
    if order.status != 'draft':
        messages.error(request, "Только черновики могут быть удалены")
        return redirect('services:order-detail-page', order_id=order_id)
    
    # Выполняем SQL запрос UPDATE для логического удаления заявки
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE services_order SET status = %s WHERE id = %s",
            ['deleted', order_id]
        )
    
    messages.success(request, "Заявка успешно удалена")
    return redirect('services:real-estate-list-page')


@login_required
@require_http_methods(["POST"])
def add_property_to_order(request, property_id):
    """
    Добавление объекта недвижимости в заявку-черновик
    """
    # Получаем объект недвижимости
    real_estate = get_object_or_404(RealEstate, id=property_id, is_active=True)
    
    # Получаем или создаем черновик заявки для текущего пользователя
    draft_order = Order.get_draft_order(request.user)
    
    if not draft_order:
        draft_order = Order.create_draft_order(request.user)
    
    # Проверяем, не добавлен ли уже этот объект в заявку
    order_property = OrderRealEstate.objects.filter(order=draft_order, real_estate=real_estate).first()
    
    if order_property:
        # Если объект уже добавлен, увеличиваем количество
        order_property.quantity += 1
        order_property.save()
        messages.success(request, f"Количество объекта '{real_estate.name}' увеличено в корзине")
    else:
        # Иначе создаем новую связь
        # Определяем порядковый номер для нового объекта
        order_number = OrderRealEstate.objects.filter(order=draft_order).count() + 1
        
        OrderRealEstate.objects.create(
            order=draft_order,
            real_estate=real_estate,
            quantity=1,
            order_number=order_number,
            is_main=(order_number == 1)  # Первый добавленный объект становится основным
        )
        messages.success(request, f"Объект '{real_estate.name}' добавлен в корзину")
    
    # Перенаправляем на страницу, с которой пришел запрос
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return HttpResponseRedirect(referer)
    else:
        return redirect('services:order-detail-page', order_id=draft_order.id)


@login_required
@require_http_methods(["POST"])
def remove_property_from_order(request, order_id, property_id):
    """
    Удаление объекта недвижимости из заявки-черновика
    """
    # Получаем заявку и проверяем права доступа
    order = get_object_or_404(Order, id=order_id)
    
    if order.creator != request.user and not request.user.is_staff:
        return HttpResponseForbidden("Вы не можете изменять чужие заявки")
    
    # Проверяем, что заявка находится в статусе черновик
    if order.status != 'draft':
        messages.error(request, "Только черновики могут быть изменены")
        return redirect('services:order-detail-page', order_id=order_id)
    
    # Получаем связь между заявкой и объектом недвижимости
    order_property = get_object_or_404(OrderRealEstate, order_id=order_id, id=property_id)
    
    # Удаляем связь
    property_name = order_property.real_estate.name
    order_property.delete()
    
    messages.success(request, f"Объект '{property_name}' удален из корзины")
    
    # Обновляем порядковые номера оставшихся объектов
    for i, op in enumerate(OrderRealEstate.objects.filter(order=order), 1):
        op.order_number = i
        op.is_main = (i == 1)  # Первый объект становится основным
        op.save()
    
    return redirect('services:order-detail-page', order_id=order_id)


@login_required
@require_http_methods(["POST"])
def form_order(request, order_id):
    """
    Формирование заявки (изменение статуса на "сформирован")
    """
    order = get_object_or_404(Order, id=order_id)
    
    if order.creator != request.user:
        return HttpResponseForbidden("Вы не можете формировать чужие заявки")
    
    try:
        order.form_order()
        messages.success(request, "Заявка успешно сформирована")
    except ValueError as e:
        messages.error(request, str(e))
    
    return redirect('services:order-detail-page', order_id=order_id)


# Представление для отображения страницы со списком объектов недвижимости
def real_estate_list(request):
    """
    Отображение страницы со списком объектов недвижимости
    """
    # Получаем все активные объекты недвижимости
    real_estates = RealEstate.objects.filter(is_active=True)
    
    # Обработка поиска
    search_query = request.GET.get('search', '')
    if search_query:
        real_estates = real_estates.filter(
            Q(name__icontains=search_query) | 
            Q(address__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Обработка сортировки
    sort_param = request.GET.get('sort', '')
    if sort_param == 'price_asc':
        real_estates = real_estates.order_by('price')
    elif sort_param == 'price_desc':
        real_estates = real_estates.order_by('-price')
    elif sort_param == 'area_desc':
        real_estates = real_estates.order_by('-area')
    else:
        real_estates = real_estates.order_by('id')
    
    # Пагинация (показываем по 3 объекта на странице)
    paginator = Paginator(real_estates, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Если пользователь авторизован, получаем его черновик заявки
    draft_order = None
    if request.user.is_authenticated:
        draft_order = Order.get_draft_order(request.user)
    
    context = {
        'real_estates': page_obj,
        'draft_order': draft_order,
        'is_paginated': paginator.num_pages > 1,
        'page_obj': page_obj
    }
    
    return render(request, 'services/real_estate_list.html', context)


# Представление для отображения страницы с деталями объекта недвижимости
def real_estate_detail(request, property_id):
    """
    Отображение страницы с деталями объекта недвижимости
    """
    # Получаем объект недвижимости
    real_estate = get_object_or_404(RealEstate, id=property_id, is_active=True)
    
    # Если пользователь авторизован, получаем его черновик заявки
    draft_order = None
    if request.user.is_authenticated:
        draft_order = Order.get_draft_order(request.user)
    
    context = {
        'real_estate': real_estate,
        'draft_order': draft_order
    }
    
    return render(request, 'services/real_estate_detail.html', context)


# Представление для отображения страницы с деталями заявки
@login_required
def order_detail(request, order_id):
    """
    Отображение страницы с деталями заявки
    """
    # Получаем заявку
    order = get_object_or_404(Order, id=order_id)
    
    # Проверяем права доступа
    if order.creator != request.user and not request.user.is_staff:
        return HttpResponseForbidden("У вас нет доступа к этой заявке")
    
    # Проверяем, не удалена ли заявка
    if order.status == 'deleted':
        messages.error(request, "Эта заявка была удалена")
        return redirect('services:real-estate-list-page')
    
    # Обрабатываем POST-запрос для обновления информации о клиенте
    if request.method == 'POST':
        order.client_name = request.POST.get('client_name')
        order.client_phone = request.POST.get('client_phone')
        order.client_email = request.POST.get('client_email')
        order.payment_method = request.POST.get('payment_method')
        order.save()
        messages.success(request, "Информация о клиенте обновлена")
        return redirect('services:order-detail-page', order_id=order.id)
    
    # Получаем объекты недвижимости в заявке
    order_properties = order.orderrealestate_set.all().select_related('real_estate')
    
    # Рассчитываем общую стоимость
    total_price = sum(item.final_price for item in order_properties)
    
    context = {
        'order': order,
        'order_properties': order_properties,
        'total_price': total_price,
        'draft_order': order if order.status == 'draft' else None
    }
    
    return render(request, 'services/order_detail.html', context)