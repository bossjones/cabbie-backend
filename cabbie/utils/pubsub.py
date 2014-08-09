from collections import defaultdict


class PubsubMixin(object):
    def __init__(self, *args, **kwargs):
        super(PubsubMixin, self).__init__(*args, **kwargs)
        self._callbacks = defaultdict(list)

    def subscribe(self, name, callback):
        self._callbacks[name].append(callback)

    def publish(self, name, *args, **kwargs):
        for callback in self._callbacks[name]:
            callback(*args, **kwargs)
