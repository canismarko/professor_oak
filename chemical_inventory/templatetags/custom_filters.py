from django import template

register = template.Library()

@register.filter(name='subscript')
def subscript(self):
    def insert_maths_boundary(string, index):
        return string[:index] + '$' + string[index:index+2] + '$' + string[index+2:]

    formula = self
    x = 0
    while x in range (0, len(formula)):
        if formula[x] in ('_'):
            formula = insert_maths_boundary(formula, x)
            x += 1
        x += 1
    return formula