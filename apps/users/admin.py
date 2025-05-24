from django.contrib import admin
from apps.users.models import User, UserType

admin.site.register(UserType)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["username", 'first_name','last_name', 'email', 'phone']
    list_filter = ["username", 'first_name', 'last_name','email', 'phone']
    search_fields = ["username", 'first_name', 'last_name','email', 'phone']