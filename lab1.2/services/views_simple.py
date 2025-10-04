from django.shortcuts import render
from django.http import HttpResponse
from datetime import date

def hello(request):
    """
    Представление для главной страницы с примером использования шаблонизатора
    """
    return render(request, 'services/index.html', {'data': {
        'current_date': date.today(),
        'list': ['python', 'django', 'html']
    }})

def GetOrders(request):
    """
    Представление для отображения списка заказов с жестко закодированными данными
    """
    return render(request, 'services/orders.html', {'data': {
        'current_date': date.today(),
        'orders': [
            {'title': 'ЖК Зеленые аллеи', 'id': 1},
            {'title': 'ЖК Западный порт', 'id': 2},
            {'title': 'ЖК Ильинские луга', 'id': 3},
        ]
    }})

def GetOrder(request, id):
    """
    Представление для отображения детальной информации о заказе
    """
    # Словарь с информацией о заказах
    orders_info = {
        1: {'title': 'ЖК Зеленые аллеи', 'address': 'Москва, ул. Зеленая, 10', 'price': '10000000'},
        2: {'title': 'ЖК Западный порт', 'address': 'Москва, ул. Западная, 20', 'price': '15000000'},
        3: {'title': 'ЖК Ильинские луга', 'address': 'Москва, ул. Ильинская, 30', 'price': '12000000'},
    }
    
    # Получаем информацию о заказе по ID
    order_info = orders_info.get(id, {'title': f'Неизвестный объект #{id}', 'address': 'Адрес не указан', 'price': 'Цена не указана'})
    
    return render(request, 'services/order_detail.html', {'data': {
        'current_date': date.today(),
        'id': id,
        'order': order_info
    }})

def sendText(request):
    """
    Обработчик для формы отправки текста
    """
    if request.method == 'POST':
        input_text = request.POST.get('text', '')
        # Возвращаем текст обратно в шаблон
        return render(request, 'services/index.html', {'data': {
            'current_date': date.today(),
            'list': ['python', 'django', 'html'],
            'input_text': input_text
        }})
    else:
        # Если это не POST запрос, перенаправляем на главную
        return hello(request)