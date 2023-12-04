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
    active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['beekeeper', 'name'],
                name='unique_beekeeper_place_name'
            )
        ]


class Hives(models.Model):
    place = models.ForeignKey(HivesPlaces, on_delete=models.CASCADE)
    number = models.IntegerField()
    type = models.CharField(max_length=255)
    size = models.IntegerField()
    comment = models.TextField()
    active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['place', 'number'],
                name='unique_place_hive_number'
            )
        ]


class Mothers(models.Model):
    hive = models.ForeignKey(Hives, on_delete=models.SET_NULL, null=True)
    ancestor = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    mark = models.CharField(max_length=255, unique=True)
    year = models.IntegerField()
    male_line = models.CharField(max_length=255)
    female_line = models.CharField(max_length=255)
    comment = models.TextField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.mark


class Tasks(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Visits(models.Model):
    hive = models.ForeignKey(Hives, on_delete=models.SET_NULL, null=True)
    date = models.DateField()
    inspection_type = models.CharField(max_length=255)
    condition = models.IntegerField()
    hive_body_size = models.CharField(max_length=255)
    honey_supers_size = models.CharField(max_length=255)
    honey_yield = models.FloatField()
    medication_application = models.CharField(max_length=255)
    disease = models.CharField(max_length=255)
    mite_drop = models.IntegerField()
    performed_tasks = models.ManyToManyField(Tasks, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.date}"




