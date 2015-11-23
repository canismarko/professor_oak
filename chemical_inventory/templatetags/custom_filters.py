import datetime

from django import template
from django.utils.html import escape, mark_safe

from ..models import Container, expired_containers, Location
from django.contrib.auth.models import User

register = template.Library()

@register.filter
def subtract(value, arg):
    return value - arg

@register.filter(name='formula_markup')
def formula_markup(formula):
    def insert_subscript(string, index):
        return string[:index] + '<sub>' + string[index:index+2] + '</sub>' + string[index+2:]
    def insert_superscript(string, index):
        return string[:index] + '<sup>' + string[index:index+2] + '</sup>' + string[index+2:]

    formula = escape(formula)
    x = 0
    while x in range (0, len(formula)):
        if formula[x] in ('_'):
            formula = insert_subscript(formula, x)
            x += 5
        if formula[x] in ('^'):
            formula = insert_superscript(formula, x)
            x += 5
        x += 1
    formula = formula.replace("_","").replace("^", "")
    return mark_safe(formula)

@register.assignment_tag(name='top_user')
def top_user():
    max_list = []
    for user in User.objects.all():
        max_list.append(Container.objects.filter(is_empty=False, owner=user).count())
    return max(max_list)

@register.filter(name='user_red_number')
def user_red_number(user):
    return expired_containers().filter(owner=user).count()
        
@register.filter(name='user_red_score')
def user_red_score(user):
    return (user_red_number(user) / top_user()) * 100

@register.filter(name='user_green_number')
def user_green_number(user):
    return Container.objects.filter(is_empty=False, owner=user, expiration_date__gte=datetime.date.today()).count()   
    
@register.filter(name='user_green_score')
def user_green_score(user):
    return (user_green_number(user) / top_user()) * 100

@register.assignment_tag(name='top_location')
def top_location():
    max_location_list = []
    for location in Location.objects.all():
        max_location_list.append(Container.objects.filter(is_empty=False, location=location).count())
    return max(max_location_list)

@register.filter(name='location_red_number')
def location_red_number(location):
    return expired_containers().filter(location=location).count()
        
@register.filter(name='location_red_score')
def location_red_score(location):
    return (location_red_number(location) / top_location()) * 100

@register.filter(name='location_green_number')
def location_green_number(location):
    return Container.objects.filter(is_empty=False, location=location, expiration_date__gte=datetime.date.today()).count()   
    
@register.filter(name='location_green_score')
def location_green_score(location):
    return (location_green_number(location) / top_location()) * 100
   