import datetime
import csv
import re
import os
import subprocess
import warnings
import logging

from django.core.urlresolvers import reverse
from django.core.files import File
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.dispatch import receiver
from django.db.models import signals
from django.utils.text import slugify
from chemspipy import ChemSpider

from professor_oak.models import ScoreMixin

log = logging.getLogger(__name__)

class Hazard(models.Model):
    """A hazard type as defined by the global harmonized system.

    Attributes
    ----------
    - pictogram : Image file that represents this image. If not
	  provided, we will look in `static_files/ghs_pictograms/` for one
	  that matches the `name` attribute
	"""
    PHYSICAL = 'p'
    HEALTH = 'h'
    PHYSICAL_AND_HEALTH = 'ph'
    ENVIRONMENTAL = 'e'
    TYPE_OPTIONS = [
	(PHYSICAL, 'Physical'),
	(HEALTH, 'Health'),
	(PHYSICAL_AND_HEALTH, 'Physical and Health'),
	(ENVIRONMENTAL, 'Environmental'),
    ]
    hazard_type = models.CharField(max_length=4, choices=TYPE_OPTIONS)
    name = models.CharField(max_length=30)
    description = models.TextField(blank=True)
    # String to where the static file for this pictogram is stored
    # (relative to the {% static%}/ location)
    pictogram = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

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
    # Global harmonized system
    ghs_hazards = models.ManyToManyField('Hazard', blank=True)
    # NFPA system
    NFPA_NOT_AVAILABLE = -1
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
        return "{name} ({formula})".format(name=self.name,
                                           formula=self.stripped_formula)

    def detail_url(self):
        """Return the url for the detailed view of this chemical and all the
	containers of it. Looked up in urls.py.
        """
        url = reverse('chemical_detail', kwargs={'pk': self.pk})
        return url

    def edit_url(self):
        """Return the url for the detailed view of this chemical and all the
	containers of it. Looked up in urls.py.
        """
        url = reverse('chemical_edit', kwargs={'pk': self.pk})
        return url

    def is_in_stock(self):
        """Return True if a chemical has a container with material in it,
        otherwise return False.
        """
        full_containers = Container.objects.filter(chemical__id=self.pk, is_empty=False)
        return full_containers.count() > 0

    def stock_is_null(self):
        """Returns whether a chemical has no containers"""
        if Container.objects.filter(chemical__id=self.pk).count() == 0:
            return True
        return False
    
    def structure_url(self):
        try:
            cs_key = settings.CHEMSPIDER_KEY
        except AttributeError:
            log.warn('CHEMSPIDER_KEY not found in localsettings.py')
            url = 'http://discovermagazine.com/~/media/Images/Zen%20Photo/N/nanoputian/3487.gif'
        else:
            cs = ChemSpider(cs_key)
            IUPAC = self.name
            search_results = cs.simple_search(IUPAC)
            try:
                url = search_results[0].image_url
                if url[:5] != 'https':
                    url = 'https' + url[4:]     # add https to url for added security
            except IndexError:
                url = None
        return url

    def get_absolute_url(self):
        return reverse('chemical_detail', kwargs={'pk': self.pk})

    @property
    def empty_container_set(self):
        return self.container_set.filter(is_empty=True)

    def has_expired(self):
        expired_qs = Container.objects.filter(
            chemical__id=self.pk,
            expiration_date__lte=datetime.date.today()
        )
        return expired_qs.count() > 0

    def not_empty_but_expired(self):
        expired_qs = Container.objects.filter(
            chemical__id=self.pk,
            expiration_date__lte=datetime.date.today(),
            is_empty=False
        )
        if expired_qs.count() > 0:
            return True
        return False


@receiver(signals.pre_save, sender=Chemical)
def strip_formula(sender, instance, raw, using, update_fields, *args, **kwargs):
    """Strips the formula supplied to remove underscores and carrots,
    saves it as the stripped_formula field. Used for formula
    searching.
    """
    instance.stripped_formula = instance.formula.replace("_","").replace("^","")


class Glove(models.Model):
    """Different chemicals have different glove compatibility. The `name`
    field should provide some indication of the material from which it
    is made.
    """
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
    owner = models.ForeignKey(User, null=True, blank=True)
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
        containers of it. Looked up in urls.py.
        """
        url = reverse('container_edit', kwargs={'pk': self.pk})
        return url

    def detail_url(self):
        """Return the url for the detailed view of this chemical and all the
        containers of it. Looked up in urls.py.
        """
        url = reverse('chemical_detail', kwargs={'pk': self.chemical_id})
        return url

    def save(self, *args, **kwargs):
        """Automatically set the user if necessary."""
        ret = super().save(*args, **kwargs)
        return ret

    def is_expired(self):
        return self.expiration_date <= datetime.date.today()

    def get_absolute_url(self):
        return reverse('chemical_detail', kwargs={'pk': self.chemical_id})

    def print_label(self):
        """Pass the information from the container to subprocess, convert it
        to a csv file and merge with the gLabel template.
        """
        if settings.DEBUG:
            # Can only be run in production mode
            msg = 'Cannot print label with settings.DEBUG set to True'
            raise ImproperlyConfigured(msg)
        name = str(self.chemical.name)[:35]
        location = str(self.location)[:25]
        barcode_identifier = str(self.pk).zfill(6)
        expiration = self.expiration_date.strftime("%m/%d/%y")
        working_directory = 'chemical_inventory/label_printing'
        with open(os.path.join(working_directory, 'input.csv'), 'w', newline='') as f:
            input = csv.writer(f, delimiter=',')
            data = (name, location, barcode_identifier, expiration)
            input.writerow(data)
        subprocess.call(['scp',
                         '-o UserKnownHostsFile=' + settings.HOSTS,
                         '-i'+ settings.PRINTER_KEY,
                         os.path.join(working_directory, 'input.csv'),
                         settings.PRINTING_IP + ':/home/pi/label_printing'])
        subprocess.Popen(['ssh',
                          '-o UserKnownHostsFile=' + settings.HOSTS,
                          '-i'+ settings.PRINTER_KEY,
                          settings.PRINTING_IP,
                          '/home/pi/label_printing/bash_print.sh'])

    def mark_as_empty(self, *args, **kwargs):
        self.container.is_empty = True
        self.save()

    def quantity_string(self):
        s = "{quantity} {unit_of_measure}"
        return s.format(quantity=self.quantity,
                        unit_of_measure=self.unit_of_measure)


class StandardOperatingProcedure(models.Model):
    """A document that is required to be signed before working with
    associated chemicals
    """
    name = models.CharField(max_length=50)
    verified_users = models.ManyToManyField(User,
                                            related_name='sop',
                                            blank=True)
    associated_chemicals = models.ManyToManyField('Chemical',
                                                  related_name='sop',
                                                  blank=True)
    file = models.FileField(upload_to='SOPs')

    def __str__(self):
        plural_list = ["","s"]
        name = self.name
        user_count = len(self.verified_users.all())
        if user_count==1:
                plural = plural_list[0]
        else:
                plural = plural_list[1]
        s = "{name} ({user_count} verified user{plural})"
        return s.format(name=name, user_count=user_count, plural=plural)

    class Meta:
        verbose_name = "Standard Operating Procedure (SOP)"
        verbose_name_plural = "Standard Operating Procedures (SOPs)"
        ordering = ['name']

def expired_containers(date=None):
    # Default to today
    if date is None:
        date = datetime.date.today()
        return Container.objects.filter(expiration_date__lte=date,
                                        is_empty=False)


class SupportingDocument(models.Model):
    """A document that characterizes the given container. Ex. XRD, TGA,
    vendor CofA.
    """
    name = models.CharField(max_length=50)
    container = models.ForeignKey('Container')
    file = models.FileField(upload_to='supporting_documents')
    comment = models.TextField(blank=True)
    owner = models.ForeignKey(User, blank=True, null=True)
    date_added = models.DateTimeField(auto_now=True)

    def __str__(self):
        s = "{name} ({chemical}: {container_id})"
        return s.format(name=self.name,
                        chemical=self.container.chemical,
                        container_id=self.container.id)


class Location(ScoreMixin, models.Model):
    name = models.CharField(max_length=50, blank=True)
    room_number = models.CharField(max_length=20)
    building = models.CharField(max_length=30)
    msds_location = models.CharField(max_length=60, blank=True)
    compatible_hazards = models.ManyToManyField('Hazard')

    def __str__(self):
        s = "{name} ({room} {bldg})"
        return s.format(name=self.name, room=self.room_number,
                        bldg=self.building)

    @property
    def active_container_set(self):
        return self.container_set.filter(is_empty=False)


class Supplier(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta():
        ordering = ['name']

