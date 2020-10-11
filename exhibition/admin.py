from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from exhibition.models import UserWithTitle
from exhibition.models import Position
from exhibition.models import Exhibit

class UserWithTitleAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (('Additional Info', {'fields': ('title',),}),)
    list_display = ('username', 'email', 'first_name', 'last_name', 'title')

class PositionAdmin(admin.ModelAdmin):
    list_display = ('position_id', 'posx', 'posy', 'posz', 'roty')

class ExhibitAdmin(admin.ModelAdmin):
    list_display = ('name', 'summary', 'position')

# Register your models here.
admin.site.register(UserWithTitle, UserWithTitleAdmin)
admin.site.register(Position, PositionAdmin)
admin.site.register(Exhibit, ExhibitAdmin)