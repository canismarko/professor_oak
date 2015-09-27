import datetime
import csv
import re

from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

# Create your models here.
class Chemical(models.Model):
    """The general idea of a chemical (eg Lithium hydroxide). It is *not*
    a bottle of lithium hydroxide, just the general concept of lithium
    hydroxide. An instance of `Chemical` describes safety information
    among other things.

    """
    name = models.CharField(max_length=200)
    cas_number = models.CharField(max_length=10, db_index=True, blank=True)
    formula = models.CharField(max_length=50, blank=True)
    NFPA_RATINGS = [
        (0, 'None (0)'),
        (1, 'Low (1)'),
        (2, 'Caution (2)'),
        (3, 'Warning (3)'),
        (4, 'Danger (4)'),
    ]
    NFPA_HAZARDS = [
        ('W', 'Water reactive (W)'),
        ('OX', 'Oxidizer (OX)'),
        ('SA', 'Simple asphyxiant (SA)'),
    ]
    health = models.IntegerField(choices=NFPA_RATINGS)
    flammability = models.IntegerField(choices=NFPA_RATINGS)
    instability = models.IntegerField(choices=NFPA_RATINGS)
    special_hazards = models.CharField(max_length=2, choices=NFPA_HAZARDS, blank=True)
    gloves = models.ManyToManyField('Glove')

    def __str__(self):
        return "{name} ({formula})".format(name=self.name, formula=self.formula)

    def detail_url(self):
        """Return the url for the detailed view of this chemical and all the
        containers of it. Looked up in urls.py."""
        url = reverse('chemical_detail', kwargs={'pk': self.pk})
        return url

    def edit_url(self):
        """Return the url for the detailed view of this chemical and all the
        containers of it. Looked up in urls.py."""
        url = reverse('chemical_edit', kwargs={'pk': self.pk})
        return url

    def is_in_stock(self):
        """Return True if a chemical has a container with material in it,
        otherwise return False."""
        # Stubbed for development
        return True

    def structure_url(self):
        from chemspipy import ChemSpider
        try:
            cs_key = settings.CHEMSPIDER_KEY
        except AttributeError:
            url = 'http://discovermagazine.com/~/media/Images/Zen%20Photo/N/nanoputian/3487.gif'
        else:
            cs = ChemSpider(cs_key)
            CAS = self.cas_number
            search_results = cs.simple_search(CAS)
            url = search_results[0].image_url
        return url


class Glove(models.Model):
    """Different chemicals have different glove compatibility. The `name`
    field should provide some indication of the material from which it is
    made."""
    name = models.CharField(max_length=50)
    supplier = models.ManyToManyField('Supplier', blank=True)

    def __str__(self):
        return self.name


class Container(models.Model):
    """This is a specific container of a chemical. This could be a
    specific bottle of lithium hydroxide in your lab. Attributes
    associated with a container include things like its location,
    amount and owner.

    """
    chemical = models.ForeignKey('Chemical')
    location = models.ForeignKey('Location')
    batch = models.CharField(max_length=30, blank=True)
    date_added = models.DateTimeField(auto_now=True)
    date_opened = models.DateField(null=True, default=datetime.date.today)
    expiration_date = models.DateField()
    state = models.CharField(max_length=10)
    container_type = models.CharField(max_length=50)
    owner = models.ForeignKey(User, blank=True, null=True)
    quantity = models.FloatField(null=True, blank=True)
    unit_of_measure = models.CharField(max_length=20, null=True, blank=True)
    is_empty = models.BooleanField(default=False)
    emptied_by = models.ForeignKey(User, null=True, blank=True, related_name='emptied_containers')
    barcode = models.CharField(max_length=30, blank=True)
    supplier = models.ForeignKey('Supplier', null=True, blank=True)

    def __str__(self):
        string = "{chemical} {container_type} in {location}"
        return string.format(chemical=self.chemical,
                             container_type=self.container_type,
                             location=self.location)

    def edit_url(self):
        """Return the url for the detailed view of this chemical and all the
        containers of it. Looked up in urls.py."""
        url = reverse('container_edit', kwargs={'pk': self.pk})
        return url

    def detail_url(self):
        """Return the url for the detailed view of this chemical and all the
        containers of it. Looked up in urls.py."""
        url = reverse('chemical_detail', kwargs={'pk': self.pk})
        return url

    def save(self, *args, **kwargs):
        """Automatically set the user if necessary."""
        ret = super().save(*args, **kwargs)
        return ret


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

    def __str__(self):
        return self.name


class SafetyDataSheet(models.Model):
    sds_file = models.FileField()
    chemical = models.ForeignKey('Chemical')
    supplier = models.ForeignKey('Supplier')


def import_chemicals_csv(csvfile):
    """Parses a csv file exported from our old Access database and
    converts it to model instances."""
    f = open(csvfile)
    csvreader = csv.reader(f)
    default_glove = Glove.objects.get(name='Nitrile')
    # for line in [list(csvreader)[0]]:
    for line in csvreader:
        # Translate attributes from csv file
        cas_number = line[1]
        name = line[2]
        formula = line[3]
        health = line[4]
        flammability = line[5]
        instability = line[6]
        special_hazards = line[7]
        # Create chemical object
        chemical = Chemical(
            cas_number=cas_number,
            name=name,
            formula=formula,
            health=health,
            flammability=flammability,
            instability=instability,
        )
        chemical.save()
        # Add gloves
        glove_string = line[9]
        for glove_name in glove_string.split(';'):
            glove_name = glove_name.strip()
            if Glove.objects.filter(name=glove_name).exists():
                glove = Glove.objects.get(name=glove_name)
            else:
                # Create glove first
                glove = Glove(name=glove_name)
                glove.save()
            chemical.gloves.add(glove)

def import_containers_csv(csvfile):
    f = open(csvfile)
    csvreader = csv.reader(f, quoting=csv.QUOTE_NONE)
    default_glove = Glove.objects.get(name='Nitrile')
    for line in csvreader:
        container = Container()
        # Look up existing chemical
        cas_number = line[1].strip('"')
        try:
            chemical = Chemical.objects.get(cas_number=cas_number)
        except Chemical.DoesNotExist as e:
            # Cannot find associated chemical
            print('Cannot find chemical for {}'.format(line))
            break
        # Continue creating container
        container.chemical = chemical
        # Find location
        location_name = line[2].strip('"')
        try:
            location = Location.objects.get(name=location_name)
        except Location.DoesNotExist:
            location = Location(name=location_name, room_number='NA', building='NA')
            location.save()
        finally:
            container.location = location
        # Find or add supplier
        supplier_name = line[4].strip('"')
        try:
            supplier = Supplier.objects.get(name=supplier_name)
        except Supplier.DoesNotExist:
            supplier = Supplier(name=supplier_name)
            supplier.save()
        container.supplier = supplier
        # Set added and expiration date
        added_string = line[5].strip('"')[0:10]
        try:
            added_date = datetime.datetime.strptime(added_string, '%Y-%m-%d')
        except ValueError:
            added_date = datetime.datetime.now()
        container.expiration_date = added_date + datetime.timedelta(days=365)
        # Find and set owner
        owner_string = line[9].strip('"')
        if not owner_string == '':
            try:
                owner = User.objects.get(first_name=owner_string)
            except User.DoesNotExist:
                # User does not exist, so print a message
                print('Cannot find user {} for container {}'.format(owner_string, line[0]))
            else:
                container.owner = owner
        # Split up the quantity string
        quantity_string = line[10].strip('"').strip()
        match = re.match('([0-9.]+)\s?([a-zA-Z]+)', quantity_string)
        if match:
            container.quantity, container.unit_of_measure = match.groups()
        # Other simple values
        container.batch = line[3].strip('"')
        container.state = line[7].strip('"')
        container.container_type = line[8].strip('"')
        container.save()
