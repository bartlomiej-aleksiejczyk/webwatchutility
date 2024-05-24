from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from django.contrib.auth import views as auth_views

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + ((None, {"fields": ("role",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + ((None, {"fields": ("role",)}),)


admin.site.register(CustomUser, CustomUserAdmin)
