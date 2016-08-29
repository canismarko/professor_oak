from django.db import models
from datetime import datetime, date
import os

from chemical_inventory.models import Container
from .static import inventory_reader as ir
from django.conf import settings

#sending emails
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.models import User
from templated_email import send_templated_mail

root_file_storage = 'oak_utilities/chemical_inventory_data/'

def update_filename(instance, filename):
	format = 'stock_take-' + str(date.today()) + '.txt'
	return os.path.join(root_file_storage, format)

def send_email(template_name, payload):
	'''Emails all active users from the gmail set up for the server. Text is the primary format but alternative html is rendered and sent as well.'''
	active_users = User.objects.filter(is_active=True)
	active_users_email = []
	for user in active_users:
		active_users_email.append(user.email)
	
	active_users_email = ['plews2@uic.edu'] #[DEBUG]remove this line before commiting
	
	send_templated_mail(
		template_name=template_name,
		from_email='Cabana Server',
		recipient_list=active_users_email,
		context = payload,
		template_suffix="html",
)

class stock_take(models.Model):
	"""Turns a .csv or .txt file that contains, in a single list, barcode numbers corresponding to id's of containers into a stock_take object'"""
	name = models.DateTimeField(default=datetime.now)
	file = models.FileField(upload_to=update_filename)

	def __str__(self):
		return str(self.name)

	def email_results(self):
		uploaded_file_name = str(self.file)
		containers = Container.objects.all()
		
		#Iterate over containers that are not empty to form a list of container id's
		database = []
		for item in containers:
			database.append(item.id)

		#Create actual list from uploaded file and run comparison
#		file_upload = settings.BASE_DIR + '/' + settings.MEDIA_ROOT + '/' + uploaded_file_name
		file_upload = '{0}/{1}/{2}'.format(settings.BASE_DIR, settings.MEDIA_ROOT, uploaded_file_name)
		actual = ir.create_barcode_actual(str(file_upload))
		accounted_for, not_in_db, not_in_actual = ir.analyse(actual, database)
		
		accounted_for_count = Container.objects.filter(id__in=accounted_for).count()
		not_in_db_empty_count = Container.objects.filter(id__in=not_in_db).count()
		not_in_db_count = len(not_in_db)
		not_in_actual_count = Container.objects.filter(id__in=not_in_actual, is_empty=False).count()

		payload = {
			'active_stock_id':self.id,
			'active_stock_name':self.name,
			'accounted_for_count':accounted_for_count,
			'not_in_db_count':not_in_db_count,
			'not_in_actual_count':not_in_actual_count,
			}

		send_email('inventory_results', payload)
