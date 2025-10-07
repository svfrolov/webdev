"""
Файл с коллекциями данных для использования вместо базы данных
"""

# Коллекция объектов недвижимости (массив)
real_estates = [
    {
        'id': 1,
        'name': 'Современная квартира в центре',
        'description': 'Просторная светлая квартира с современным ремонтом в центре города. '
                       'Высокие потолки, большие окна, встроенная кухня. '
                       'Рядом парк, магазины, школы и детские сады. '
                       'Отличная транспортная доступность.',
        'price': 8500000,
        'area': 65.5,
        'address': 'г. Москва, ул. Тверская, д. 15, кв. 42',
        'rooms': 2,
        'floor': 5,
        'total_floors': 12,
        'property_type': 'apartment',
        'property_type_display': 'Квартира',
        'image_key': 'apartment1.jpg',
        'image_url': None,  # Будет заполнено в контроллере
        'is_active': True
    },
    {
        'id': 2,
        'name': 'Уютный загородный дом',
        'description': 'Двухэтажный загородный дом из экологически чистых материалов. '
                       'Участок 15 соток с ландшафтным дизайном, беседкой и барбекю. '
                       'В доме 4 спальни, 2 санузла, просторная гостиная с камином. '
                       'Центральные коммуникации, газовое отопление.',
        'price': 15000000,
        'area': 180,
        'address': 'Московская область, Одинцовский район, пос. Лесной, ул. Сосновая, д. 7',
        'rooms': 6,
        'floor': 2,
        'total_floors': 2,
        'property_type': 'house',
        'property_type_display': 'Дом',
        'image_key': 'house1.jpg',
        'image_url': None,
        'is_active': True
    },
    {
        'id': 3,
        'name': 'Коммерческое помещение в бизнес-центре',
        'description': 'Офисное помещение в современном бизнес-центре класса B+. '
                       'Качественная отделка, панорамные окна, система кондиционирования. '
                       'Удобная планировка: open space + 2 кабинета. '
                       'Охрана, видеонаблюдение, парковка для сотрудников и клиентов.',
        'price': 12000000,
        'area': 120,
        'address': 'г. Москва, Пресненская наб., д. 10, офис 505',
        'rooms': 3,
        'floor': 5,
        'total_floors': 25,
        'property_type': 'commercial',
        'property_type_display': 'Коммерческая недвижимость',
        'image_key': 'commercial1.jpg',
        'image_url': None,
        'is_active': True
    },
    {
        'id': 4,
        'name': 'Земельный участок под строительство',
        'description': 'Ровный земельный участок правильной формы в коттеджном поселке. '
                       'Электричество по границе участка, газ в перспективе. '
                       'Хорошая транспортная доступность, круглогодичный подъезд. '
                       'Красивые виды, лес в шаговой доступности.',
        'price': 3500000,
        'area': 1200,
        'address': 'Московская область, Истринский район, д. Лужки, уч. 42',
        'rooms': 0,
        'floor': None,
        'total_floors': None,
        'property_type': 'land',
        'property_type_display': 'Земельный участок',
        'image_key': 'land1.jpg',
        'image_url': None,
        'is_active': True
    },
    {
        'id': 5,
        'name': 'Студия с видом на реку',
        'description': 'Компактная студия с современным ремонтом и панорамным видом на реку. '
                       'Функциональная планировка, встроенная кухня, гардеробная. '
                       'Дом новый, с подземным паркингом и охраной. '
                       'Развитая инфраструктура района.',
        'price': 5200000,
        'area': 28,
        'address': 'г. Москва, Пресненская наб., д. 8, кв. 315',
        'rooms': 1,
        'floor': 15,
        'total_floors': 30,
        'property_type': 'apartment',
        'property_type_display': 'Квартира',
        'image_key': 'apartment2.jpg',
        'image_url': None,
        'is_active': True
    },
    {
        'id': 6,
        'name': 'Таунхаус в коттеджном поселке',
        'description': 'Современный таунхаус в охраняемом коттеджном поселке. '
                       'Три уровня, качественная отделка, встроенная техника. '
                       'Участок 2 сотки, парковка на 2 автомобиля. '
                       'Рядом лес, озеро, детская площадка.',
        'price': 9800000,
        'area': 150,
        'address': 'Московская область, Красногорский район, пос. Отрадное, ул. Лесная, д. 12',
        'rooms': 4,
        'floor': 3,
        'total_floors': 3,
        'property_type': 'house',
        'property_type_display': 'Дом',
        'image_key': 'house2.jpg',
        'image_url': None,
        'is_active': True
    },
]

# Словарь заявки (корзина)
order = {
    'id': 1,
    'status': 'draft',
    'status_display': 'Черновик',
    'created_at': '2025-10-05T10:00:00Z',
    'formed_at': None,
    'completed_at': None,
    'creator': {'id': 1, 'username': 'admin'},
    'moderator': None,
    'client_name': 'Иванов Иван Иванович',
    'client_phone': '+7 (999) 123-45-67',
    'client_email': 'ivanov@example.com',
    'payment_method': 'mortgage',
    'payment_method_display': 'Ипотека',
    'total_price': 0,
    'estimated_delivery_date': None,
    'items': []  # Список объектов недвижимости в заявке
}

# Функция для добавления объекта недвижимости в заявку
def add_property_to_order(property_id):
    """
    Добавляет объект недвижимости в заявку
    """
    # Находим объект недвижимости по ID
    property_to_add = None
    for prop in real_estates:
        if prop['id'] == property_id:
            property_to_add = prop
            break
    
    if not property_to_add:
        return False
    
    # Проверяем, есть ли уже этот объект в заявке
    for item in order['items']:
        if item['real_estate']['id'] == property_id:
            # Если объект уже есть, увеличиваем количество
            item['quantity'] += 1
            item['final_price'] = item['real_estate']['price'] * item['quantity'] * (1 - item['discount_percent'] / 100)
            return True
    
    # Если объекта еще нет в заявке, добавляем его
    order_number = len(order['items']) + 1
    
    new_item = {
        'id': order_number,
        'order_number': order_number,
        'quantity': 1,
        'is_main': order_number == 1,  # Первый объект становится основным
        'discount_percent': 0,
        'final_price': property_to_add['price'],
        'real_estate': property_to_add
    }
    
    order['items'].append(new_item)
    return True

# Функция для удаления объекта недвижимости из заявки
def remove_property_from_order(item_id):
    """
    Удаляет объект недвижимости из заявки
    """
    for i, item in enumerate(order['items']):
        if item['id'] == item_id:
            order['items'].pop(i)
            
            # Обновляем порядковые номера оставшихся объектов
            for j, remaining_item in enumerate(order['items'], 1):
                remaining_item['order_number'] = j
                remaining_item['is_main'] = (j == 1)  # Первый объект становится основным
            
            return True
    
    return False

# Функция для расчета общей стоимости заявки
def calculate_total_price():
    """
    Рассчитывает общую стоимость заявки
    """
    total = 0
    
    for item in order['items']:
        total += item['final_price']
    
    # Применяем дополнительную скидку в зависимости от способа оплаты
    if order['payment_method'] == 'cash':
        # 5% скидка при оплате наличными
        total = total * 0.95
    elif order['payment_method'] == 'mortgage':
        # 2% скидка при ипотеке
        total = total * 0.98
    
    order['total_price'] = total
    return total