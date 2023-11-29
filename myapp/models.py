from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Beekeepers(User):
    beekeeper_id = models.IntegerField(unique=True)

    def __str__(self):
        return self.username


class HivesPlaces(models.Model):
    beekeeper = models.ForeignKey(Beekeepers, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    comment = models.TextField()


class Hives(models.Model):
    place = models.ForeignKey(HivesPlaces, on_delete=models.CASCADE)
    number = models.IntegerField()
    type = models.CharField(max_length=255)
    size = models.IntegerField()
    comment = models.TextField()


class Mother(models.Model):
    hive = models.ForeignKey(Hives, on_delete=models.SET_NULL, null=True)
    year = models.IntegerField()
    performance = models.CharField(max_length=255)
    male_line = models.CharField(max_length=255)
    female_line = models.CharField(max_length=255)
    comment = models.TextField()


class Visit(models.Model):
    hive = models.ForeignKey(Hives, on_delete=models.CASCADE)
    date = models.DateField()
    type = models.CharField(max_length=255)
    treatment = models.CharField(max_length=255)
    mite_drop = models.IntegerField()
    condition = models.IntegerField()
    honey_amount = models.FloatField()
    zootechnical_act = models.CharField(max_length=255)

