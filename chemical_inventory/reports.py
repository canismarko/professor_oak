import csv
import datetime

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.views.generic.base import TemplateView

from professor_oak.views import breadcrumb, BreadcrumbsMixin
from professor_oak.models import OakUser
from .views import inventory_breadcrumb
from .models import Container, Chemical, Location

container_csv_header = ['Barcode',
                        'Chemical Name',
                        'Batch',
                        'Location',
                        'Quantity',
                        'Units',
                        'Expiration Date',
                        'State',
                        'Container',
                        'Owner',]

def container_csv_row(container):
    """Convert a container object into a list suitable for passing to a
    csv writer writerow() method."""
    return [
        container.id,
        container.chemical.name,
        container.batch,
        container.location,
        container.quantity,
        container.unit_of_measure,
        container.expiration_date,
        container.state,
        container.container_type,
        container.owner.get_full_name(),
    ]

class ReportsList(BreadcrumbsMixin, TemplateView):
    """List of all available reports. New reports must be added to
    urls.py and the reports_list.html template.
    """
    template_name = "reports/report_list.html"

    def breadcrumbs(self):
        return [
            inventory_breadcrumb(),
            'reports'
            ]


class ReportView(BreadcrumbsMixin, TemplateView):
    template_name = 'reports/generic_report.html'
    formats = []
    report_name = 'Report'
    """Base class for showing a specific report."""

    def get_queryset(self):
        msg = 'No `get_queryset()` method defined for {cls}'
        raise NotImplementedError(msg.format(cls=self.__class__))

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['report_name'] = self.report_name
        context['objects'] = self.get_queryset()
        # Check which formats this view supports
        context['csv_available'] = hasattr(self, 'write_csv')
        return context

    def get(self, request, *args, **kwargs):
        format = request.GET.get('format')
        if format == 'csv':
            # Prepare a CSV response object
            response = HttpResponse(content_type='text/csv')
            disposition = 'attachment; filename="{}.csv"'.format(self.url_name)
            response['Content-Disposition'] = disposition
            self.write_csv(response)
        else:
            response = super().get(request, *args, **kwargs)
        return response

    def breadcrumbs(self):
        breadcrumbs = [
            inventory_breadcrumb(),
            'reports',
        ]
        # Try and determine this reports navigation trail from the name and url
        try:
            breadcrumbs.append((self.report_name, reverse(self.url_name)))
        except AttributeError:
            pass
        print(breadcrumbs)
        return breadcrumbs


##############################
# Specific Report view go here
##############################
class AllChemicals(ReportView):
    template_name = "reports/all_chemicals.html"
    url_name = 'all_chemicals'
    report_name = "All Chemicals"

    def get_queryset(self):
        return Chemical.objects.all()

    def write_csv(self, response):
        writer = csv.writer(response)
        # Write column headings
        writer.writerow(['Chemical name', 'Formula', 'Received', 'Emptied', 'Remaining'])
        # Write chemical data to rows
        for chemical in self.get_queryset():
            row = [
                chemical.name,
                chemical.stripped_formula,
                chemical.container_set.count(),
                chemical.empty_container_set.count(),
                chemical.container_set.count() - chemical.empty_container_set.count()
            ]
            writer.writerow(row)
        return response


class ContainersReport(ReportView):
    template_name = "reports/containers_report.html"

    def write_csv(self, response):
        writer = csv.writer(response)
        # Write column headings
        writer.writerow(container_csv_header)
        # Write chemical data to rows
        for container in self.get_queryset():
            row = container_csv_row(container)
            writer.writerow(row)
        return response


class ActiveContainers(ContainersReport):
    url_name = 'active_containers'
    report_name = "Active Containers"

    def get_queryset(self):
        return Container.objects.filter(is_empty=False)


class ExpiredContainers(ContainersReport):
    url_name = 'expired_containers'
    report_name = "Expired Containers"

    def get_queryset(self):
        today = datetime.date.today()
        return Container.objects.filter(is_empty=False,
                                        expiration_date__lte=today)


class ContainersByLocation(ReportView):
    template_name = "reports/containers_by_location.html"
    url_name = 'containers_by_location'
    report_name = 'Containers by Location'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # A 'context' is the data that the template can use
        max_containers, list_of_locations = [],[]
        for location in Location.objects.all():
            max_containers.append(Container.objects.filter(location=location).count())
        context.update({
            'max_location': max(max_containers)
        })
        return context
    
    def get_queryset(self):
        locations = Location.objects.all()
        return locations

    def write_csv(self, response):
        writer = csv.writer(response)
        # Write header
        writer.writerow(['Location'] + container_csv_header)
        for location in self.get_queryset():
            # Put location name in a column
            writer.writerow([location])
            # Write container data
            for container in location.active_container_set:
                writer.writerow([''] + container_csv_row(container))
        return response


class ContainersByOwner(ReportView):
    template_name = "reports/containers_by_owner.html"
    url_name = 'containers_by_owner'
    report_name = 'Containers by Owner'

    def get_queryset(self):
        users = OakUser.objects.all()
        return users

    def write_csv(self, response):
        writer = csv.writer(response)
        # Write header
        writer.writerow(['Owner'] + container_csv_header)
        for user in self.get_queryset():
            # Put location name in a column
            writer.writerow([user.get_full_name()])
            # Write container data
            for container in user.container_set.all():
                if not container.is_empty:
                    writer.writerow([''] + container_csv_row(container))
        return response
