from django.contrib import admin
from exhibition.models import UserWithTitle
from exhibition.models import Position
from exhibition.models import Exhibit

class UserWithTitleAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'title')

class PositionAdmin(admin.ModelAdmin):
    list_display = ('position_id', 'posx', 'posy', 'posz', 'roty')

class ExhibitAdmin(admin.ModelAdmin):
    list_display = ('name', 'summary', 'position')

# Register your models here.
admin.site.register(UserWithTitle, UserWithTitleAdmin)
admin.site.register(Position, PositionAdmin)
admin.site.register(Exhibit, ExhibitAdmin)