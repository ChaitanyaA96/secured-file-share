from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

class UserAdmin(BaseUserAdmin):
    model = User
    ordering = ['email']
    list_display = ['email', 'role', 'is_active', 'is_staff', 'email_verified']
    list_display_links = ['email']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Role & Status', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
        ('MFA Settings', {'fields': ('mfa_enabled', 'mfa_secret')}),
        ('Email Verification', {'fields': ('email_verified', 'email_verification_token', 'email_verification_expiry')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role'),
        }),
    )

    search_fields = ['email']
    list_filter = ['is_active', 'is_staff', 'role', 'email_verified']

admin.site.register(User, UserAdmin) 