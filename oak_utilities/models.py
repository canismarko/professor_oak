from django.db import models
import datetime as dt
import os

from chemical_inventory.models import Container
from .static import inventory_reader as ir
from django.conf import settings

#sending emails
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.models import User, Group
from templated_email import send_templated_mail


root_file_storage = 'oak_utilities/chemical_inventory_data/'

def update_filename(instance, filename, date=None):
    if date is None:
        date = dt.date.today()
    format = 'stock_take-{}.txt'.format(date)
    return os.path.join(root_file_storage, format)

def send_email(template_name, payload, destination_email=""):
    '''Emails all active users from the gmail set up for the server. Text
    is the primary format but alternative html is rendered and sent as
    well.
    
    '''
    active_users = User.objects.filter(is_active=True)
    active_users_email = []
    for user in active_users:
        active_users_email.append(user.email)    
    if template_name == 'inventory_results':
        send_templated_mail(
            template_name=template_name,
            from_email='Cabana Server',
            recipient_list=active_users_email,
            context = payload,
            template_suffix="html",
    )
    elif template_name == 'ulon_expired':
        CHO_email = Group.objects.get(name='Chemical Hygiene Officer (CHO)').user_set.all()[0].email
        send_templated_mail(
            template_name=template_name,
            from_email='Cabana Server',
            recipient_list=[destination_email],
            context = payload,
            cc = [CHO_email],
    )


class stock_take(models.Model):
    """Turns a .csv or .txt file that contains, in a single list, barcode
    numbers corresponding to id's of containers into a stock_take
    object'
    
    """
    name = models.DateTimeField(default=dt.datetime.now)
    file = models.FileField(upload_to=update_filename)
    
    class Meta:
        verbose_name = "Stock Take"
        verbose_name_plural = "Stock Takes"
    
    def __str__(self):
        return str(self.name)
    
    def email_results(self):
        uploaded_file_name = str(self.file)
        containers = Container.objects.all()
        base_url = str(settings.PRODUCTION_URL)
        # Iterate over containers that are not empty to form a list of container id's
        database = []
        for item in containers:
            database.append(item.id)
        # Create actual list from uploaded file and run comparison
        file_upload = '{0}/{1}/{2}'.format(settings.BASE_DIR, settings.MEDIA_ROOT, uploaded_file_name)
        actual = ir.create_barcode_actual(str(file_upload))
        accounted_for, not_in_db, not_in_actual = ir.analyse(actual, database)
        accounted_for_count = Container.objects.filter(id__in=accounted_for).count()
        not_in_db_empty_count = Container.objects.filter(id__in=not_in_db).count()
        not_in_db_count = len(not_in_db)
        not_in_actual_count = Container.objects.filter(id__in=not_in_actual, is_empty=False).count()
        payload = {
            'active_stock_id': self.id,
            'active_stock_name': self.name,
            'accounted_for_count': accounted_for_count,
            'not_in_db_count': not_in_db_count,
            'not_in_actual_count': not_in_actual_count,
            'base_url': base_url,
            }
        send_email('inventory_results', payload)


class ULON(models.Model):
    """A basic model describing the ULON generated by the User.
    
    This is not exhaustive, only holds the produced .pdf, UL# (pk),
    date created, and user that created it. Made for the REST
    Framework integration with LabPi to email users once their ULON is
    scanned due to expiration.
    
    """
    ul = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True, blank=True)
    file = models.FileField(upload_to='ULONs', null=True, blank=True)
    title = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return str('{user} (UL{UL})').format(user=self.user, UL=str(self.ul).zfill(4))
    
    class Meta:
        verbose_name = 'ULON'
        verbose_name_plural='ULONs'
    
    def email_results(self):
        title = str(self.title)
        user = str(self.user.first_name)
        base_url = str(settings.PRODUCTION_URL)
        ul = str(self.ul)
        CHO_name = Group.objects.get(name='Chemical Hygiene Officer (CHO)').user_set.all()[0].get_full_name()
        payload = {
            'ulon_ul':ul,
            'ulon_title':title,
            'ulon_user':user,
            'base_url':base_url,
            'CHO_name':CHO_name,
            }
        user_email = self.user.email
        send_email('ulon_expired', payload, user_email)
