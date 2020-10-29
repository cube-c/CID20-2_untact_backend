from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from exhibition.models import UserWithTitle, Position, Exhibit, UserActivity

class UserWithTitleAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (('Additional Info', {'fields': ('title',),}),)
    list_display = ('username', 'email', 'first_name', 'last_name', 'title')

class PositionAdmin(admin.ModelAdmin):
    list_display = ('position_id', 'posx', 'posy', 'posz', 'roty')

class ExhibitAdmin(admin.ModelAdmin):
    list_display = ('name', 'summary', 'position')

class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'last_activity_ip', 'last_activity_date')

# Register your models here.
admin.site.register(UserWithTitle, UserWithTitleAdmin)
admin.site.register(UserActivity, UserActivityAdmin)
admin.site.register(Position, PositionAdmin)
admin.site.register(Exhibit, ExhibitAdmin)