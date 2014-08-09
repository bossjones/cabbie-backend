class Location(list):
    """Represents longitude and latitude pair. Should be updated regularly."""

    def __init__(self, *args, **kwargs):
        super(Location, self).__init__(*args, **kwargs)
        self._ensure_size()

    def __unicode__(self):
        return u'Location({location})'.format(location=list(self))

    __repr__ = __str__ = __unicode__

    def update(self, location):
        assert len(location) == 2, 'Wrong size'
        for i, coord in enumerate(location):
            self[i] = coord

    def _ensure_size(self):
        while len(self) < 2:
            self.append(0)
