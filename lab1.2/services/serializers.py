from rest_framework import serializers
from django.contrib.auth.models import User
from .models import RealEstate, Order, OrderRealEstate


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели пользователя
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class RealEstateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели объекта недвижимости
    """
    class Meta:
        model = RealEstate
        fields = '__all__'


class OrderRealEstateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для связи заявки и объекта недвижимости
    """
    real_estate = RealEstateSerializer(read_only=True)
    real_estate_id = serializers.PrimaryKeyRelatedField(
        queryset=RealEstate.objects.all(),
        write_only=True,
        source='real_estate'
    )
    
    class Meta:
        model = OrderRealEstate
        fields = ['id', 'real_estate', 'real_estate_id', 'quantity', 'order_number', 'is_main', 
                 'discount_percent', 'final_price']


class OrderSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели заявки
    """
    creator = UserSerializer(read_only=True)
    moderator = UserSerializer(read_only=True)
    order_properties = OrderRealEstateSerializer(source='orderrealestate_set', many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'status', 'created_at', 'creator', 'formed_at', 'completed_at', 'moderator',
                 'client_name', 'client_phone', 'client_email', 'payment_method', 
                 'total_price', 'estimated_delivery_date', 'order_properties']
        read_only_fields = ['status', 'created_at', 'creator', 'formed_at', 'completed_at', 'moderator',
                           'total_price', 'estimated_delivery_date']