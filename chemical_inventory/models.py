from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Chemical(models.Model):
    cas_number = models.CharField(max_length=10, db_index=True, blank=True)
    name = models.CharField(max_length=200)
    formula = models.CharField(max_length=50, blank=True)
    NFPA_RATINGS = [
        (0, 'None (0)'),
        (1, 'Low (1)'),
        (2, 'Caution (2)'),
        (3, 'Warning (3)'),
        (4, 'Danger (4)'),
    ]
    NFPA_HAZARDS = [
        ('W', '̶Water reactive (̶W'),
        ('OX', 'Oxidizer (OX)'),
        ('SA', 'Simple asphyxiant (SA)'),
    ]
    health = models.IntegerField(choices=NFPA_RATINGS)
    flammability = models.IntegerField(choices=NFPA_RATINGS)
    instability = models.IntegerField(choices=NFPA_RATINGS)
    special_hazards = models.CharField(max_length=2, choices=NFPA_HAZARDS, blank=True)
    glove = models.ForeignKey('Glove')

    def __str__(self):
        return "{} ({})".format(self.name, self.formula)


class Glove(models.Model):
    name = models.CharField(max_length=50)
    supplier = models.ManyToManyField('Supplier', blank=True)

    def __str__(self):
        return self.name


class Container(models.Model):
    chemical = models.ForeignKey('Chemical')
    location = models.ForeignKey('Location')
    batch = models.CharField(max_length=30, blank=True)
    date_added = models.DateTimeField(auto_now=True)
    date_opened = models.DateField(null=True)
    expiration_date = models.DateField()
    state = models.CharField(max_length=10)
    container_type = models.CharField(max_length=50)
    owner = models.ForeignKey(User)
    quantity = models.FloatField(null=True, blank=True)
    unit_of_measure = models.CharField(max_length=20, null=True)
    empty_status = models.BooleanField()
    emptied_by = models.ForeignKey(User, null=True, blank=True, related_name='emptied_containers')
    barcode = models.CharField(max_length=30, blank=True)
    supplier = models.ForeignKey('Supplier', null=True, blank=True)

    def __str__(self):
        string = "{chemical} {container_type} in {location}"
        return string.format(chemical=self.chemical,
                             container_type=self.container_type,
                             location=self.location)


class Location(models.Model):
    name = models.CharField(max_length=50, blank=True)
    room_number = models.CharField(max_length=20)
    building = models.CharField(max_length=30)
    msds_location = models.CharField(max_length=60, blank=True)

    def __str__(self):
        return "{name} ({room} {bldg})".format(name=self.name,
                                             room=self.room_number,
                                             bldg=self.building)


class Supplier(models.Model):
    name = models.CharField(max_length=50)


class SafetyDataSheet(models.Model):
    sds_file = models.FileField()
    chemical = models.ForeignKey('Chemical')
    supplier = models.ForeignKey('Supplier')
