from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from datetime import datetime, timedelta
import decimal


class RealEstate(models.Model):
    """
    Модель объекта недвижимости (услуги)
    """
    name = models.CharField(max_length=255, verbose_name="Наименование")
    description = models.TextField(verbose_name="Описание")
    is_active = models.BooleanField(default=True, verbose_name="Статус (действует/удален)")
    image_url = models.URLField(blank=True, null=True, verbose_name="URL изображения")
    image_key = models.CharField(max_length=255, blank=True, null=True, verbose_name="Ключ изображения в Minio")
    
    # Поля по предметной области "продажа недвижимости"
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Цена")
    area = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Площадь (кв.м)")
    address = models.CharField(max_length=255, verbose_name="Адрес")
    rooms = models.PositiveIntegerField(default=1, verbose_name="Количество комнат")
    floor = models.PositiveIntegerField(null=True, blank=True, verbose_name="Этаж")
    total_floors = models.PositiveIntegerField(null=True, blank=True, verbose_name="Всего этажей")
    property_type = models.CharField(max_length=50, choices=[
        ('apartment', 'Квартира'),
        ('house', 'Дом'),
        ('commercial', 'Коммерческая недвижимость'),
        ('land', 'Земельный участок')
    ], verbose_name="Тип недвижимости")
    
    class Meta:
        verbose_name = "Объект недвижимости"
        verbose_name_plural = "Объекты недвижимости"
        
    def __str__(self):
        return f"{self.name} ({self.address})"


class Order(models.Model):
    """
    Модель заявки на покупку недвижимости
    """
    STATUS_CHOICES = (
        ('draft', 'Черновик'),
        ('deleted', 'Удален'),
        ('formed', 'Сформирован'),
        ('completed', 'Завершен'),
        ('rejected', 'Отклонен'),
    )
    
    # Обязательные поля NotNull
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    creator = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_orders', verbose_name="Создатель")
    
    # Nullable поля
    formed_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата формирования")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата завершения")
    moderator = models.ForeignKey(User, on_delete=models.PROTECT, related_name='moderated_orders', 
                                  null=True, blank=True, verbose_name="Модератор")
    
    # Дополнительные поля по предметной области
    client_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="ФИО клиента")
    client_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Телефон клиента")
    client_email = models.EmailField(blank=True, null=True, verbose_name="Email клиента")
    payment_method = models.CharField(max_length=50, blank=True, null=True, choices=[
        ('cash', 'Наличные'),
        ('mortgage', 'Ипотека'),
        ('installment', 'Рассрочка')
    ], verbose_name="Способ оплаты")
    
    # Поле для расчета при завершении заявки
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Итоговая стоимость")
    estimated_delivery_date = models.DateField(null=True, blank=True, verbose_name="Предполагаемая дата доставки документов")
    
    properties = models.ManyToManyField(RealEstate, through='OrderRealEstate', verbose_name="Объекты недвижимости")
    
    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        
    def __str__(self):
        return f"Заявка #{self.id} ({self.get_status_display()})"
    
    def calculate_total_price(self):
        """
        Расчет итоговой стоимости заявки с учетом скидок
        Формула: сумма (цена объекта * количество * (1 - скидка/100))
        """
        total = decimal.Decimal('0.00')
        
        for order_property in self.orderrealestate_set.all():
            # Рассчитываем финальную цену для каждого объекта недвижимости в заявке
            discount_multiplier = decimal.Decimal('1.00') - (order_property.discount_percent / decimal.Decimal('100.00'))
            item_price = order_property.real_estate.price * order_property.quantity * discount_multiplier
            
            # Обновляем финальную цену в записи м-м
            order_property.final_price = item_price
            order_property.save()
            
            # Добавляем к общей сумме
            total += item_price
        
        # Применяем дополнительную скидку в зависимости от способа оплаты
        if self.payment_method == 'cash':
            # 5% скидка при оплате наличными
            total = total * decimal.Decimal('0.95')
        elif self.payment_method == 'mortgage':
            # 2% скидка при ипотеке
            total = total * decimal.Decimal('0.98')
            
        return total
    
    def calculate_delivery_date(self):
        """
        Расчет предполагаемой даты доставки документов
        Формула: текущая дата + 30 дней - (количество объектов недвижимости * 2 дня)
        Но не менее 14 дней
        """
        property_count = self.orderrealestate_set.count()
        
        # Базовый срок - 30 дней
        days = 30
        
        # Вычитаем 2 дня за каждый объект недвижимости
        days -= property_count * 2
        
        # Но не менее 14 дней
        if days < 14:
            days = 14
            
        # Рассчитываем дату
        if self.completed_at:
            delivery_date = self.completed_at.date() + timedelta(days=days)
        else:
            delivery_date = datetime.now().date() + timedelta(days=days)
            
        return delivery_date
    
    def complete_order(self, moderator):
        """
        Метод для завершения заявки модератором
        Включает расчет итоговой стоимости и даты доставки
        """
        if self.status != 'formed':
            raise ValueError("Только сформированные заявки могут быть завершены")
        
        self.status = 'completed'
        self.completed_at = datetime.now()
        self.moderator = moderator
        
        # Расчет итоговой стоимости
        self.total_price = self.calculate_total_price()
        
        # Расчет предполагаемой даты доставки
        self.estimated_delivery_date = self.calculate_delivery_date()
        
        self.save()
        
    def reject_order(self, moderator):
        """
        Метод для отклонения заявки модератором
        """
        if self.status != 'formed':
            raise ValueError("Только сформированные заявки могут быть отклонены")
        
        self.status = 'rejected'
        self.completed_at = datetime.now()
        self.moderator = moderator
        self.save()
    
    def form_order(self):
        """
        Метод для формирования заявки создателем
        """
        if self.status != 'draft':
            raise ValueError("Только черновики могут быть сформированы")
        
        # Проверка обязательных полей
        required_fields = ['client_name', 'client_phone', 'client_email', 'payment_method']
        missing_fields = []
        
        for field in required_fields:
            if not getattr(self, field):
                missing_fields.append(field)
        
        if missing_fields:
            raise ValueError(f"Не заполнены обязательные поля: {', '.join(missing_fields)}")
        
        # Проверка наличия объектов недвижимости в заявке
        if self.orderrealestate_set.count() == 0:
            raise ValueError("Заявка должна содержать хотя бы один объект недвижимости")
        
        self.status = 'formed'
        self.formed_at = datetime.now()
        self.save()
    
    @classmethod
    def get_draft_order(cls, user):
        """
        Получить черновик заявки для пользователя или создать новый
        """
        draft_order = cls.objects.filter(creator=user, status='draft').first()
        return draft_order
    
    @classmethod
    def create_draft_order(cls, user):
        """
        Создать новый черновик заявки для пользователя
        """
        # Проверяем, нет ли уже черновика у пользователя
        existing_draft = cls.get_draft_order(user)
        if existing_draft:
            return existing_draft
        
        # Создаем новый черновик
        draft_order = cls.objects.create(
            status='draft',
            creator=user
        )
        return draft_order


class OrderRealEstate(models.Model):
    """
    Связь многие-ко-многим между заявками и объектами недвижимости
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name="Заявка")
    real_estate = models.ForeignKey(RealEstate, on_delete=models.PROTECT, verbose_name="Объект недвижимости")
    
    # Дополнительные поля
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    order_number = models.PositiveIntegerField(default=1, verbose_name="Порядковый номер")
    is_main = models.BooleanField(default=False, verbose_name="Основной объект")
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Скидка (%)")
    final_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Финальная цена")
    
    class Meta:
        verbose_name = "Объект недвижимости в заявке"
        verbose_name_plural = "Объекты недвижимости в заявках"
        # Составной уникальный ключ
        unique_together = ('order', 'real_estate')
        
    def __str__(self):
        return f"{self.real_estate.name} в заявке #{self.order.id}"
    
    def save(self, *args, **kwargs):
        """
        Переопределяем метод save для автоматического расчета финальной цены
        """
        # Рассчитываем финальную цену при сохранении
        if self.real_estate and self.quantity and self.discount_percent is not None:
            discount_multiplier = decimal.Decimal('1.00') - (self.discount_percent / decimal.Decimal('100.00'))
            self.final_price = self.real_estate.price * self.quantity * discount_multiplier
            
        super().save(*args, **kwargs)