import datetime

from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from chemspipy import ChemSpider
# from django.utils.safestring import mark_safe

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
        return "{name} ({formula})".format(name=self.name, formula=self.formula)
	
    def subscript(self):
        def insert_maths_boundary(string, index):
	        return string[:index] + '$' + string[index:index+2] + '$' + string[index+2:]

        formula = self.formula
        x = 0
        while x in range (0, len(formula)):
	        if formula[x] in ('_'):
	        	formula = insert_maths_boundary(formula, x)
	        	x += 1
	        x += 1
        return formula
	
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
        try:
            cs_key = settings.CHEMSPIDER_KEY
        except AttributeError:
            url = 'http://i.imgur.com/X17puIB.gif'
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
    owner = models.ForeignKey(User)
    quantity = models.FloatField(null=True, blank=True)
    unit_of_measure = models.CharField(max_length=20, null=True)
    empty_status = models.BooleanField(default=False)
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
