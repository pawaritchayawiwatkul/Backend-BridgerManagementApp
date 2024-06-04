from django.db import models
from school.models import Course, School
from core.models import User
from teacher.models import Teacher
from uuid import uuid4
import secrets

# Create your models here.

class CourseRegistration(models.Model):
    registered_date = models.DateField(auto_now_add=True)
    finised_date = models.DateField(null=True)
    course = models.ForeignKey(to=Course, on_delete=models.PROTECT, related_name="registration")
    student = models.ForeignKey(to="Student", on_delete=models.CASCADE, related_name="registration")
    finished = models.BooleanField(default=False)
    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    favorite = models.BooleanField(default=False)
    teacher = models.ForeignKey(Teacher, on_delete=models.PROTECT)
    used_lessons = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)

class StudentTeacherRelation(models.Model):
    student = models.ForeignKey("Student", on_delete=models.CASCADE, related_name="teacher_relation")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="student_relation")
    favorite_teacher = models.BooleanField(default=False)
    favorite_student = models.BooleanField(default=False)

class Student(models.Model):
    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    course = models.ManyToManyField(to=Course, through=CourseRegistration, related_name="student")
    school = models.ManyToManyField(to=School, related_name="student")
    teacher = models.ManyToManyField(to=Teacher, through=StudentTeacherRelation, related_name="student")
    user = models.OneToOneField(User, models.CASCADE)

class Lesson(models.Model):
    notes = models.CharField(max_length=300, blank=True)
    booked_datetime = models.DateTimeField()
    attended = models.BooleanField(default=False)
    registration = models.ForeignKey(to=CourseRegistration, on_delete=models.CASCADE)
