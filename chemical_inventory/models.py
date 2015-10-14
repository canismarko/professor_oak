import datetime
import csv
import re

from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.dispatch import receiver
from django.db.models import signals

# Create your models here.
class Chemical(models.Model):
    """The general idea of a chemical (eg Lithium hydroxide). It is *not*
    a bottle of lithium hydroxide, just the general concept of lithium
    hydroxide. An instance of `Chemical` describes safety information
    among other things.

    """
    name = models.CharField(max_length=200, db_index=True)
    cas_number = models.CharField(max_length=100, db_index=True, blank=True)
    formula = models.CharField(max_length=50, db_index=True, blank=True)
    stripped_formula = models.CharField(max_length=50, db_index=True, blank=True)
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
    safety_data_sheet = models.FileField(upload_to='safety_data_sheets',
                                         null=True, blank=True)

    class Meta:
        ordering = ['name']

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
        if Container.objects.filter(chemical__id=self.pk, is_empty=False).count() != 0:
            return True
        return False
    
    def stock_is_null(self):
        """Returns whether a chemical has no containers"""
        if Container.objects.filter(chemical__id=self.pk).count() == 0:
            return True
        return False
    
    def structure_url(self):
        from chemspipy import ChemSpider
        try:
            cs_key = settings.CHEMSPIDER_KEY
        except AttributeError:
            url = 'http://discovermagazine.com/~/media/Images/Zen%20Photo/N/nanoputian/3487.gif'
        else:
            cs = ChemSpider(cs_key)
            IUPAC = self.name
            search_results = cs.simple_search(IUPAC)
            try:
                url = search_results[0].image_url
            except IndexError:
                url = ""
        return url

    def get_absolute_url(self):
        return reverse('chemical_detail', kwargs={'pk': self.pk})

    def has_expired(self):
        if Container.objects.filter(chemical__id=self.pk, expiration_date__lte=datetime.date.today()).count() != 0:
            return True
        return False

@receiver(signals.pre_save, sender=Chemical)
def strip_formula(sender, instance, raw, using, update_fields, *args, **kwargs):
    """Strips the formula supplied to remove underscores and carrots, saves it as the stripped_formula field. Used for formula searching."""
    instance.stripped_formula = instance.formula.replace("_","").replace("^","")

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
    comment = models.TextField(blank=True)

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
        url = reverse('chemical_detail', kwargs={'pk': self.chemical_id})
        return url

    def save(self, *args, **kwargs):
        """Automatically set the user if necessary."""
        ret = super().save(*args, **kwargs)
        return ret

    def is_expired(self):
        if self.expiration_date <= datetime.date.today():
            return True
        return False

    def get_absolute_url(self):
        return reverse('chemical_detail', kwargs={'pk': self.chemical_id})


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
    formula_regex = re.compile('(\d)')
    # for line in [list(csvreader)[0]]:
    for line in csvreader:
        # Translate attributes from csv file
        cas_number = line[1]
        name = line[2]
        # Make numbers subscripted in the formula
        formula = line[3]
        formula = formula_regex.sub(r'_\1', formula)
        # Default to maximum hazard
        try:
            health = int(line[4])
        except ValueError:
            health = 4
        try:
            flammability = int(line[5])
        except ValueError:
            flammability = 4
        try:
            instability = int(line[6])
        except ValueError:
            instability = 4
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
        glove_names = glove_string.split(';')
        if glove_names == [""]:
            # Default glove
            chemical.gloves.add(default_glove)
        else:
            for glove_name in glove_names:
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
    # Prepare a string indicated this container was automatically imported
    today = datetime.date.today()
    commentstring = 'Imported from old inventory on {datestring}'.format(
        datestring=today.strftime('%Y-%m-%d'))
    for line in csvreader:
        container = Container(comment=commentstring)
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
