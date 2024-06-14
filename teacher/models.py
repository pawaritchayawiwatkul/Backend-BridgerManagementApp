from django.db import models
from core.models import User
from school.models import School, Course

# Create your models here.

class TeacherCourses(models.Model):
    teacher = models.ForeignKey("Teacher", on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    favorite = models.BooleanField(default=False)
    
class Teacher(models.Model):
    user = models.OneToOneField(User, models.CASCADE)
    course = models.ManyToManyField(Course, through=TeacherCourses, related_name="teachers")
    school = models.ForeignKey(School, models.CASCADE, related_name="teachers")

    def __str__(self) -> str:
        return self.user.__str__()

class UnavailableTimeOneTime(models.Model):
    date = models.DateField()
    start = models.TimeField()
    stop = models.TimeField()
    teacher = models.ForeignKey(Teacher, models.CASCADE, related_name="unavailable_once")

class UnavailableTimeRegular(models.Model):
    DAY_CHOICES = [
        ('1', 'Monday'),
        ('2', 'Tuesday'),
        ('3', 'Wednesday'),
        ('4', 'Thursday'),
        ('5', 'Friday'),
        ('6', 'Saturday'),
        ('7', 'Sunday'),
    ]
    day = models.CharField(max_length=1, choices=DAY_CHOICES)
    start = models.TimeField()
    stop = models.TimeField()
    teacher = models.ForeignKey(Teacher, models.CASCADE, related_name="unavailable_reg")