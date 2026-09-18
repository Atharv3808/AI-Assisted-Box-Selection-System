from django.contrib import admin
from packaging.models import Product, Box, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'length', 'width', 'height', 'weight', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'internal_length', 'internal_width', 'internal_height', 'max_weight', 'cost', 'created_at')
    search_fields = ('name',)
    list_filter = ('cost', 'created_at')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity')
    list_filter = ('product',)
