from django.contrib import admin
from .models import Book, Cart, Address, Order, CustomUser

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'genre', 'price')
    search_fields = ('title', 'author')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'quantity', 'price', 'total', 'ordered')
    list_filter = ('ordered',)
    search_fields = ('user__username', 'book__title')

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'city', 'state', 'pincode')
    search_fields = ('user__username', 'address')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'total', 'status', 'date')
    list_filter = ('status',)
    search_fields = ('user__username', 'address__address')

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_regular_user', 'is_staff', 'is_superuser')
    list_filter = ('is_regular_user', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')

    def is_regular_user(self, obj):
        return obj.is_regular_user
    is_regular_user.boolean = True
    is_regular_user.short_description = 'Regular User'
