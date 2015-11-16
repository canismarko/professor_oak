import datetime

from django import template
from django.utils.html import escape, mark_safe

from ..models import Container


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

@register.filter(name='user_score')
def user_score(user):
    numerator = Container.objects.filter(owner=user, expiration_date__lte=datetime.date.today(), is_empty = False).count()
    denominator = Container.objects.filter(owner=user).count()
    return 100 - (numerator/denominator*100)
 
@register.filter(name='location_score')
def location_score(location):
    numerator = Container.objects.filter(location=location, expiration_date__lte=datetime.date.today(), is_empty = False).count()
    denominator = Container.objects.filter(location=location).count()
    return 100 - (numerator/denominator*100)
 
@register.filter(name='score_class')
def score_class(score):
    if score == 100:
        return "success"
    if 50 < score < 100:
        return "warning"
    if score < 50:
        return "danger"