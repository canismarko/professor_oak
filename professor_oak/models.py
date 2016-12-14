import datetime

from django.contrib.auth.models import User


class ScoreMixin():

    @classmethod
    def top_count(Cls):
        """Get the count of the maximum active containers owned by any single user."""
        max_list = [user.active_containers.count() for user in Cls.objects.all()]
        return max(max_list)

    @property
    def active_containers(self):
        containers = self.container_set
        containers = containers.filter(is_empty=False)
        return containers

    @property
    def expired_containers(self):
        containers = self.active_containers
        today = datetime.date.today()
        containers = containers.filter(expiration_date__lte=today)
        return containers

    @property
    def nonexpired_containers(self):
        containers = self.active_containers
        today = datetime.date.today()
        containers = containers.filter(expiration_date__gt=today)
        return containers

    def red_score(self):
        """Per-cent of containers that are expired."""
        expired = self.expired_containers.count()
        active = self.active_containers.count()
        score = expired / self.top_count() * 100
        return score

    def green_score(self):
        """Per-cent of containers that are not expired."""
        nonexpired = self.nonexpired_containers.count()
        score = nonexpired / self.top_count() * 100
        return score



class OakUser(ScoreMixin, User):
    """Proxy model for a user with some extra methods added on."""
    class Meta:
        proxy = True

