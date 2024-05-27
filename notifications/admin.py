from django.contrib import admin
from .models import NotificationPartial


@admin.register(NotificationPartial)
class NotificationPartialAdmin(admin.ModelAdmin):
    pass
