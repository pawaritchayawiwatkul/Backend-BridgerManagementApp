# Register your models here.
from django.contrib import admin
from .models import CourseRegistration, Student, Lesson

# Register your models here.
# admin.site.register(ProfilePicture)
admin.site.register(CourseRegistration)
admin.site.register(Student)
admin.site.register(Lesson)