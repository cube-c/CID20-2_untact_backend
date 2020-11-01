from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from exhibition.models import UserWithTitle, Position, Exhibit

class UserWithTitleAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (('Additional Info', {'fields': ('title',),}),)
    list_display = ('username', 'email', 'first_name', 'last_name', 'title', 'last_activity_date', 'status')

class PositionAdmin(admin.ModelAdmin):
    list_display = ('position_id', 'posx', 'posy', 'posz', 'roty')

class ExhibitAdmin(admin.ModelAdmin):
    list_display = ('name', 'summary', 'position', 'hash')

# Register your models here.
admin.site.register(UserWithTitle, UserWithTitleAdmin)
admin.site.register(Position, PositionAdmin)
admin.site.register(Exhibit, ExhibitAdmin)