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

from image_cropping import ImageCropField, ImageRatioField

root_file_storage = './pokedex/data/'

accepted_upload_extensions = [".jpg", ".jpeg"]

def validate_file_extension(value):
    if not value.name.endswith(tuple(accepted_upload_extensions)):
        raise ValidationError(u'Only .jpg or .jpeg files are accepted at this time')

class Sample(models.Model):
	"""A Sample refers to the resulting compound of a specific experiment
	"""
	sample_number = models.CharField(max_length=10, db_index=True)
	name = models.CharField(max_length=200, db_index=True)
	formula = models.CharField(max_length=50, db_index=True, blank=True)
	stripped_formula = models.CharField(max_length=50, db_index=True, blank=True)

	AVAILABLE_MEDIUMS = [
		('Ballmill', 'Ballmill'), 
		('Tube: Borosilicate', 'Tube: Borosilicate'),
		('Tube: Quartz', 'Tube: Quartz'), 
		('Tube: Alumina', 'Tube: Alumina'),
	]
	AVAILABLE_ATMOSPHERES = [
		('Argon', 'Argon'), 
		('5%H2:95%N2', '5%H2:95%N2'), 
		('Oxygen', 'Oxygen'),
		('Nitrogen', 'Nitrogen'), 
		('Air', 'Air'),
	]

	experiment_medium = models.CharField(max_length=50, choices=AVAILABLE_MEDIUMS)
	experiment_atmosphere = models.CharField(max_length=50, choices=AVAILABLE_ATMOSPHERES)
	experiment_variable = models.FloatField(null=True, blank=True)
	experiment_time = models.FloatField(blank=True, null=True)
	experiment_equation = models.TextField(blank=True)
	variable_units = models.CharField(max_length=5, blank=True)	

	file_photo = ImageCropField(blank=True, null=True, upload_to=root_file_storage+'Photo')

	cropping = ImageRatioField('file_photo', '300x300')

	file_XRD = models.FileField(upload_to=root_file_storage+'XRD', null=True, blank=True, validators=[validate_file_extension])
	file_EC = models.FileField(upload_to=root_file_storage+'EC', null=True, blank=True, validators=[validate_file_extension])
	file_TEM = models.FileField(upload_to=root_file_storage+'TEM', null=True, blank=True, validators=[validate_file_extension])
	file_TGA = models.FileField(upload_to=root_file_storage+'TGA', null=True, blank=True, validators=[validate_file_extension])
	file_XAS = models.FileField(upload_to=root_file_storage+'XAS', null=True, blank=True, validators=[validate_file_extension])

	start_date = models.DateField(null=True, default=datetime.date.today)
	end_date = models.DateField(null=True, default=datetime.date.today)

	associated_project = models.ManyToManyField('Project')

	user = models.ForeignKey(User, blank=True, null=True)

	comment = models.TextField(blank=True)

	class Meta:
		ordering = ['sample_number']

	def __str__(self):
		return "{sample_number} ({formula})".format(sample_number=self.sample_number, formula=self.stripped_formula)

#Order By Meta data


	def detail_url(self):
		"""Return the url for the detailed view of the sample"""
		url = reverse('sample_detail', kwargs={'id': self.id})
		return url

	def edit_url(self):
		"""Return the url for the edit view opf the sample"""
		url = reverse('edit_sample', kwargs={'id': self.id})
		return url

	def edit_photo_url(self):
		"""Return the url for the photo edit view of the sample"""
		url = reverse('edit_sample_photo', kwargs={'id': self.id})
		return url

	def get_absolute_url(self):
		return reverse('sample_detail', kwargs={'id': self.id})

	@property
	def is_archived(self):
		projects = Project.objects.all().filter(is_archived = True).values_list('id', flat=True)
		if Sample.objects.all().filter(associated_project__in=projects, id=self.id):
			return True
		else:	
			return False

class Project(models.Model):
	"""A Project refers to the grouping of Samples. Specific users should only be able to add a Sample to a certain Project. The name field should describe the Project with no elements or chemical names."""
	name = models.CharField(max_length=50)
	is_archived = models.BooleanField(default=False, verbose_name = "Archived?")	

	class Meta:
		ordering = ['name']
	
	def __str__(self):
		if self.is_archived:
			return "{name} (Archived)".format(name=self.name)
		else:
			return "{name}".format(name=self.name)


	def detail_url(self):
		"""Returns the url for the Project"""
		url = reverse('samples_by_projects', kwargs={'id': self.id})
		return url	

class User_Project(models.Model):
	"""Describes the active projects associated with a user"""
	user = models.OneToOneField(User)
	active_project = models.ManyToManyField('Project')
	
	@property
	def first_name(self):
		return self.user.first_name

	@property
	def last_name(self):
		return self.user.last_name	

	class Meta:
		verbose_name ='User Project'
		verbose_name_plural = 'User Projects'
	
	def __str__(self):
		return "{first} {last} (Projects: {length})".format(first=self.first_name, last=self.last_name, length=self.active_project.count(), )

@receiver(signals.pre_save, sender=Sample)
def strip_formula(sender, instance, raw, using, update_fields, *args, **kwargs):
	"""Strips the formula supplied to remove underscores and carrots, saves it as the stripped_formula field. Used for formula searching."""
	instance.stripped_formula = instance.formula.replace("_","").replace("^","")	

@receiver(signals.pre_save, sender=Sample)
def add_variable_units(sender, instance, raw, using, update_fields, *args, **kwargs):
	"""Adds the variable units of the experiment_variable field depending on the experiment_medium"""
	if 'Tube:' in instance.experiment_medium:
		instance.variable_units = '^oC'
	elif 'Ballmill' in instance.experiment_medium:
		instance.variable_units = ' rpm'
