#pokedex/models.py
import datetime
import os

from django.core.urlresolvers import reverse
from django.core.files import File
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models import signals, Count
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

import plotly.offline as opy
import plotly.graph_objs as go

root_file_storage = './pokedex/data/'

def validate_file_extension(value):
  if not value.name.endswith(tuple(accepted_upload_extensions)):
    raise ValidationError(u'Only .jpg or .jpeg files are accepted at this time')

class Sample(models.Model):
    """A Sample refers to the resulting compound of a specific experiment
    """
    # sample_number = models.CharField(max_length=10, db_index=True)
    name = models.CharField(max_length=200, db_index=True)
    formula = models.CharField(max_length=50, db_index=True, blank=True)
    stripped_formula = models.CharField(max_length=50, db_index=True, blank=True)   

    file_XAS = models.FileField(upload_to=root_file_storage+'XAS', null=True, blank=True)
    
    beamline = models.CharField(max_length=50) 
    
    date_created = models.DateField(null=True, default=datetime.date.today)

    # associated_project = models.ManyToManyField('Project')
    edge = models.CharField(max_length=2)
    
    user = models.ForeignKey(User, blank=True, null=True)

    comment = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "{name} ({formula})".format(name=self.name, formula=self.stripped_formula)

#Order By Meta data

    def detail_url(self):
        """Return the url for the detailed view of the sample"""
        url = reverse('sample_detail', kwargs={'id': self.id})
        return url

    def edit_url(self):
        """Return the url for the edit view opf the sample"""
        url = reverse('edit_sample', kwargs={'id': self.id})
        return url

    def get_absolute_url(self):
        return reverse('sample_detail', kwargs={'id': self.id})
    
# class Project(models.Model):
#       """A Project refers to the grouping of Samples. Specific users should only be able to add a Sample to a certain Project. The name field should describe the Project with no elements or chemical names."""
#       name = models.CharField(max_length=50)
#       is_archived = models.BooleanField(default=False, verbose_name = "Archived?")    

#       class Meta:
#               ordering = ['name']
        
#       def __str__(self):
#               if self.is_archived:
#                       return "{name} (Archived)".format(name=self.name)
#               else:
#                       return "{name}".format(name=self.name)


#       def detail_url(self):
#               """Returns the url for the Project"""
#               url = reverse('samples_by_projects', kwargs={'id': self.id})
#               return url      

# class User_Project(models.Model):
#       """Describes the active projects associated with a user"""
#       user = models.OneToOneField(User)
#       active_project = models.ManyToManyField('Project')
        
#       @property
#       def first_name(self):
#               return self.user.first_name

#       @property
#       def last_name(self):
#               return self.user.last_name      

#       class Meta:
#               verbose_name ='User Project'
#               verbose_name_plural = 'User Projects'
        
#       def __str__(self):
#               return "{first} {last} (Projects: {length})".format(first=self.first_name, last=self.last_name, length=self.active_project.count(), )

@receiver(signals.pre_save, sender=Sample)
def strip_formula(sender, instance, raw, using, update_fields, *args, **kwargs):
    """Strips the formula supplied to remove underscores and carrots, saves it as the stripped_formula field. Used for formula searching."""
    instance.stripped_formula = instance.formula.replace("_","").replace("^","")  
