from django.contrib import admin
from .models import RealEstate, Order, OrderRealEstate

class OrderRealEstateInline(admin.TabularInline):
    model = OrderRealEstate
    extra = 1
    fields = ('real_estate', 'quantity', 'order_number', 'is_main', 'discount_percent', 'final_price')
    readonly_fields = ('final_price',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'created_at', 'creator', 'client_name', 'total_price')
    list_filter = ('status', 'created_at', 'formed_at', 'completed_at')
    search_fields = ('client_name', 'client_email', 'client_phone')
    readonly_fields = ('total_price', 'estimated_delivery_date')
    inlines = [OrderRealEstateInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('status', 'created_at', 'formed_at', 'completed_at', 'creator', 'moderator')
        }),
        ('Информация о клиенте', {
            'fields': ('client_name', 'client_phone', 'client_email', 'payment_method')
        }),
        ('Финансовая информация', {
            'fields': ('total_price', 'estimated_delivery_date')
        }),
    )
    
    def has_delete_permission(self, request, obj=None):
        # Запрещаем физическое удаление заявок
        return False

@admin.register(RealEstate)
class RealEstateAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'property_type', 'price', 'area', 'address', 'is_active')
    list_filter = ('property_type', 'is_active')
    search_fields = ('name', 'address', 'description')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'is_active', 'image_url', 'image_key')
        }),
        ('Характеристики недвижимости', {
            'fields': ('price', 'area', 'address', 'rooms', 'floor', 'total_floors', 'property_type')
        }),
    )

@admin.register(OrderRealEstate)
class OrderRealEstateAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'real_estate', 'quantity', 'order_number', 'is_main', 'discount_percent', 'final_price')
    list_filter = ('is_main',)
    search_fields = ('order__client_name', 'real_estate__name')
    readonly_fields = ('final_price',)