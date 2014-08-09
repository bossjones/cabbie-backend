class Location(list):
    """Represents longitude and latitude pair. Should be updated regularly."""

    def __init__(self, *args, **kwargs):
        super(Location, self).__init__(*args, **kwargs)
        self._ensure_size()

    def update(self, location):
        assert len(location) == 2, 'Wrong size'
        for i, coord in enumerate(location):
            self[i] = coord

    def _ensure_size(self):
        while len(self) < 2:
            self.append(0)
