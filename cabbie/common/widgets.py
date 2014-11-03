from django.contrib.gis.geos import Point
from django.forms.widgets import Textarea


class PointWidget(Textarea):
    def render(self, name, value, attrs=None):
        if value is not None:
            value = u'\n'.join([unicode(c) for c in value.coords])
        return super(PointWidget, self).render(name, value, attrs)

    def value_from_datadict(self, data, files, name):
        value = super(PointWidget, self).value_from_datadict(data, files, name)
        return Point(*[float(c) for c in value.split('\n')])
