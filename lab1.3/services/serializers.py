from rest_framework import serializers
from .models import RealEstate, Order, OrderRealEstate


class RealEstateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для объектов недвижимости
    """
    class Meta:
        model = RealEstate
        fields = '__all__'


class OrderRealEstateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для связи заявок и объектов недвижимости
    """
    real_estate = RealEstateSerializer(read_only=True)
    
    class Meta:
        model = OrderRealEstate
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    """
    Сериализатор для заявок
    """
    creator_username = serializers.ReadOnlyField(source='creator.username')
    moderator_username = serializers.ReadOnlyField(source='moderator.username', default=None)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True, default=None)
    order_properties = OrderRealEstateSerializer(source='orderrealestate_set', many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ('creator', 'created_at', 'formed_at', 'completed_at', 'moderator', 'total_price', 'estimated_delivery_date')