from collections import namedtuple

from django import template

register = template.Library()

XY = namedtuple('XY', ('x', 'y'))

class NfpaBox():
    def __init__(self, center, diagonal, color, rating='-'):
        self.center = center
        self.diagonal = diagonal
        self.color = color
        self.rating = rating

    def points(self):
        """Generate a string of points for the vertices of the box to put into
        the <polygon> tags."""
        # Determine vertices based on size
        left = XY(self.center.x - self.diagonal/2, self.center.y)
        right = XY(self.center.x + self.diagonal/2, self.center.y)
        top = XY(self.center.x, self.center.y - self.diagonal/2)
        bottom = XY(self.center.x, self.center.y + self.diagonal/2)
        # Construct points string for inclusion in html tag
        points = ""
        for vertex in [left, top, right, bottom]:
            points += "{x},{y} ".format(x=int(vertex.x), y=int(vertex.y))
        return points

    def text_position(self):
        return 'x={} y={}'.format(int(self.center.x), int(self.center.y))

    def style(self):
        """Print CSS styles appropriate for inline."""
        style = "fill:{color}".format(color=self.color)
        return style


@register.inclusion_tag('nfpa_diamond.html')
def nfpa_diamond(chemical, size=120):
    """Show the NFPA 704 hazard diamond."""
    diagonal = size/2
    health_box = NfpaBox(center=XY(size/4, size/2),
                         diagonal=diagonal,
                         color="#6691ff",
                         rating=chemical.health)
    flammability_box = NfpaBox(center=XY(size/2, size/4),
                               diagonal=diagonal,
                               color="#ff6666",
                               rating=chemical.flammability)
    instability_box = NfpaBox(center=XY(3*size/4, size/2),
                              diagonal=diagonal,
                              color="#fcff66",
                              rating=chemical.instability)
    special_hazards_box = NfpaBox(center=XY(size/2, 3*size/4),
                                  diagonal=diagonal,
                                  color="#ffffff",
                                  rating=chemical.special_hazards)
    context = {
        'size': size,
        'font_size': str(int(size*0.22)) + "px",
        'health': health_box,
        'flammability': flammability_box,
        'instability': instability_box,
        'special_hazards': special_hazards_box,
    }
    return context
