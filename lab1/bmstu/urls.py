"""
URL configuration for bmstu project.
"""
from django.contrib import admin
from django.urls import path
from bmstu_lab import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('hello/', views.hello),
    path('', views.GetOrders),
    path('order/<int:id>/', views.GetOrder, name='order_url'),
    path('sendText', views.sendText, name='sendText'),
]