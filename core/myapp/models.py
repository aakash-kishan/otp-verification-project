from django.db import models

class Customer(models.Model):
    
    userid = models.IntegerField()
    name = models.CharField(max_length=25)
    dob = models.DateField()
    age = models.IntegerField()
    ph = models.CharField(max_length=10, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    about = models.CharField(max_length=255)

    def __str__(self):
        return self.name
