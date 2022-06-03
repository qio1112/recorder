from django.contrib import admin
from .models import User, Label, Record, Picture, RecFile


class LabelAdmin(admin.ModelAdmin):
    list_filter = ('type', 'created_date', 'last_modified_date', 'editable', 'created_by', 'last_modified_by')
    list_display = ('name', 'created_by', 'type', 'editable')


class PicturesInline(admin.TabularInline):
    model = Picture


class RecordAdmin(admin.ModelAdmin):
    inlines = [
        PicturesInline,
    ]
    list_filter = ('created_by', 'created_date')
    list_display = ('title', 'created_by', 'created_date')


admin.site.register(User)
admin.site.register(Label, LabelAdmin)
admin.site.register(Record, RecordAdmin)
admin.site.register(Picture)
admin.site.register(RecFile)