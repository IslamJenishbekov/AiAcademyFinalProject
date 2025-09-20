from django.contrib import admin
from .models import Client

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'age', 'inn', 'created_at')
    search_fields = ('full_name', 'inn')
    list_filter = ('created_at', 'age')
