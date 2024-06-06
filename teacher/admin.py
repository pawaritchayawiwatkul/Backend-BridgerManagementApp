from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Teacher, UnavailableTimeOneTime, UnavailableTimeRegular

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'school')
    search_fields = ('user__first_name', 'school__name')
    filter_horizontal = ('course',)

@admin.register(UnavailableTimeOneTime)
class UnavailableTimeOneTimeAdmin(admin.ModelAdmin):
    list_display = ('datetime', 'duration', 'teacher')
    search_fields = ('teacher__user__first_name',)
    list_filter = ('datetime',)

@admin.register(UnavailableTimeRegular)
class UnavailableTimeRegularAdmin(admin.ModelAdmin):
    list_display = ('day', 'time', 'duration', 'teacher')
    search_fields = ('teacher__user__first_name',)
    list_filter = ('day',)