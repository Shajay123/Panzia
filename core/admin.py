# core/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from accounts.models import User
from startups.models import StartupProfile
from people.models import Employee


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'startup', 'is_staff', 'is_active')
    list_filter = ('role', 'startup', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    fieldsets = UserAdmin.fieldsets + (
        ('Startup Info', {
            'fields': ('role', 'startup', 'profile_image', 'bio')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Startup Info', {
            'fields': ('role', 'startup')
        }),
    )


# Unregister default UserAdmin and register custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# Custom Admin Site Header
admin.site.site_header = 'Panzia Admin'
admin.site.site_title = 'Panzia Admin Portal'
admin.site.index_title = 'Welcome to Panzia Admin Dashboard'