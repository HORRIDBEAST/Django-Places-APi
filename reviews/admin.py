from django.contrib import admin
from .models import User, Place, Review


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'phone_number', 'created_at']
    search_fields = ['name', 'phone_number']
    list_filter = ['created_at']


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'address', 'created_at']
    search_fields = ['name', 'address']
    list_filter = ['created_at']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'place', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__name', 'place__name', 'text']