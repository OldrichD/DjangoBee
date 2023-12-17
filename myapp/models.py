from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import UserManager


class BeekeepersManager(UserManager):
    pass


class Beekeepers(User):
    beekeeper_id = models.IntegerField(unique=True)

    objects = BeekeepersManager()

    def __str__(self):
        return self.username


class HivesPlaces(models.Model):
    beekeeper = models.ForeignKey(Beekeepers, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    comment = models.TextField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['beekeeper', 'name'],
                condition=models.Q(active=True),
                name='unique_active_beekeeper_place_name'
            )
        ]


class Hives(models.Model):
    place = models.ForeignKey(HivesPlaces, on_delete=models.CASCADE, related_name='hives')
    number = models.IntegerField()
    type = models.CharField(max_length=255)
    comment = models.TextField()
    active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['place', 'number'],
                condition=models.Q(active=True),
                name='unique_place_hive_number'
            )
        ]

    def __str__(self):
        return str(self.number)

    def last_honey_yield(self):
        return self.visits.filter(honey_yield__isnull=False, active=True).order_by('-date').first()

    def last_medication_application(self):
        return (
            self.visits
            .filter(medication_application__isnull=False, active=True)
            .exclude(medication_application='')
            .order_by('-date')
            .first()
        )

    def last_mite_drop(self):
        return self.visits.filter(mite_drop__isnull=False, active=True).order_by('-date').first()

    def last_disease(self):
        return self.visits\
            .filter(disease__isnull=False, active=True) \
            .exclude(disease='') \
            .order_by('-date') \
            .first()

    def last_comment(self):
        return self.visits.filter(comment__isnull=False, active=True).exclude(comment='').order_by('-date').first()


class Mothers(models.Model):
    hive = models.ForeignKey(Hives, on_delete=models.SET_NULL, null=True, related_name='mothers')
    ancestor = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    mark = models.CharField(max_length=255, unique=True)
    year = models.IntegerField()
    male_line = models.CharField(max_length=255)
    female_line = models.CharField(max_length=255)
    comment = models.TextField()
    active = models.BooleanField(default=True)

    def display_name(self):
        if self.female_line:
            return f'{self.mark} (linie: {self.female_line})'
        return self.mark

    def __str__(self):
        return self.mark


class Tasks(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Visits(models.Model):
    hive = models.ForeignKey(Hives, on_delete=models.SET_NULL, null=True, related_name='visits')
    date = models.DateField()
    inspection_type = models.CharField(max_length=255)
    condition = models.IntegerField(null=True, blank=True)
    hive_body_size = models.IntegerField(null=False, blank=True)
    honey_supers_size = models.IntegerField(null=False, blank=True)
    honey_yield = models.FloatField(null=True, blank=True)
    medication_application = models.CharField(max_length=255, null=True, blank=True)
    disease = models.CharField(max_length=255, null=True, blank=True)
    mite_drop = models.IntegerField(null=True, blank=True)
    performed_tasks = models.ManyToManyField(Tasks, blank=True)
    active = models.BooleanField(default=True)
    comment = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.date}"



