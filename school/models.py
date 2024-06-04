from django.db import models
import secrets
import uuid
# Create your models here.

class School(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=300)
    # registered_date = models.DateField(auto_now_add=True)
    # phone_number = models.IntegerField()
    # email = models.EmailField()

    def __str__(self) -> str:
        return self.name
    
class Course(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=300)
    code = models.CharField(max_length=20, unique=True, blank=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    no_exp = models.BooleanField()
    exp_range = models.IntegerField()
    duration = models.IntegerField(default=60)
    number_of_lessons = models.IntegerField(default=10)
    school = models.ForeignKey(School, on_delete=models.CASCADE)

    @staticmethod
    def generate_unique_code():
        return secrets.token_hex(8)  # Generates a random hex code of length 8

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_unique_code()
        super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return self.name + " - " + self.description
    