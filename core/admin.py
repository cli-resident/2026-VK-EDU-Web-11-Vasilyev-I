from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    extra = 0


class AccountAdmin(UserAdmin):
    inlines = [ProfileInline]


admin.site.unregister(User)
admin.site.register(User, AccountAdmin)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'rating', 'avatar']
    search_fields = ['user__username', 'user__email']
    list_filter = ['user__is_active']
    list_select_related = ['user']
    raw_id_fields = ['user']
