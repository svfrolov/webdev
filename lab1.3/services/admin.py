from django.contrib import admin
from .models import RealEstate, Order, OrderRealEstate


@admin.register(RealEstate)
class RealEstateAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'property_type', 'price', 'area', 'rooms', 'is_active')
    list_filter = ('property_type', 'is_active')
    search_fields = ('name', 'address', 'description')


class OrderRealEstateInline(admin.TabularInline):
    model = OrderRealEstate
    extra = 0
    fields = ('real_estate', 'quantity', 'order_number', 'is_main', 'discount_percent', 'final_price')
    readonly_fields = ('final_price',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client_name', 'status', 'created_at', 'formed_at', 'completed_at', 'creator')
    list_filter = ('status', 'payment_method')
    search_fields = ('client_name', 'client_phone', 'client_email')
    readonly_fields = ('created_at', 'formed_at', 'completed_at', 'creator', 'moderator', 'total_price', 'estimated_delivery_date')
    inlines = [OrderRealEstateInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('status', 'created_at', 'formed_at', 'completed_at')
        }),
        ('Информация о клиенте', {
            'fields': ('client_name', 'client_phone', 'client_email', 'payment_method')
        }),
        ('Информация о заявке', {
            'fields': ('creator', 'moderator', 'total_price', 'estimated_delivery_date')
        }),
    )


@admin.register(OrderRealEstate)
class OrderRealEstateAdmin(admin.ModelAdmin):
    list_display = ('order', 'real_estate', 'quantity', 'order_number', 'is_main', 'discount_percent', 'final_price')
    list_filter = ('is_main',)
    search_fields = ('order__id', 'real_estate__name')