from django.contrib import admin
from .models import Sweet, Order

# Register your models here.

@admin.register(Sweet)
class SweetAdmin(admin.ModelAdmin):
    list_display = ['name', 'price']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'sweet', 'quantity', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'sweet__name']