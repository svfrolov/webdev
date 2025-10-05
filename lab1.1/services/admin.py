from django.contrib import admin
from .models import RealEstate, Order, OrderRealEstate

class OrderRealEstateInline(admin.TabularInline):
    model = OrderRealEstate
    extra = 1

@admin.register(RealEstate)
class RealEstateAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'price', 'area', 'rooms', 'property_type', 'is_active')
    list_filter = ('is_active', 'property_type')
    search_fields = ('name', 'address', 'description')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'creator', 'created_at', 'formed_at', 'completed_at', 'moderator', 'total_price')
    list_filter = ('status', 'created_at', 'formed_at', 'completed_at')
    search_fields = ('client_name', 'client_email', 'client_phone')
    readonly_fields = ('created_at', 'formed_at', 'completed_at')
    inlines = [OrderRealEstateInline]

@admin.register(OrderRealEstate)
class OrderRealEstateAdmin(admin.ModelAdmin):
    list_display = ('order', 'real_estate', 'quantity', 'order_number', 'is_main', 'discount_percent', 'final_price')
    list_filter = ('is_main',)
    search_fields = ('order__id', 'real_estate__name')