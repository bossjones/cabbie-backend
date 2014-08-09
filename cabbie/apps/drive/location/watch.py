from collections import defaultdict

from django.conf import settings
from tornado import gen

from cabbie.apps.drive.location.loop import delay
from cabbie.apps.drive.location.geo import LocationManager
from cabbie.apps.drive.location.session import SessionManager
from cabbie.utils.log import LoggableMixin
from cabbie.utils.meta import SingletonMixin


class Watch(object):
    def __init__(self, passenger_id, location):
        self.passenger_id = passenger_id
        self.location = location
        self.assignment = None

    @property
    def is_assigned(self):
        return bool(self.assignment)

    @property
    def driver_ids(self):
        if not self.is_assigned:
            return []
        return [candidate['driver']['id']
                for candidate in self.assignment.get('candidates', [])]

    @property
    def best_driver_id(self):
        if not self.is_assigned:
            return None
        best = self.assignment.get('best')
        if not best:
            return None
        return best['driver']['id']

    def update_location(self, location):
        self.location = location


class WatchManager(LoggableMixin, SingletonMixin):
    refresh_interval = settings.LOCATION_REFRESH_INTERVAL

    def __init__(self):
        super(WatchManager, self).__init__()
        self._watches_by_passenger = {}

        self._matches_by_driver = defaultdict(set)
        self._best_matches_by_driver = {}

        # Register callbacks
        LocationManager().subscribe('activated', self.on_driver_activated)
        LocationManager().subscribe('deactivated', self.on_driver_deactivated)
        SessionManager().subscribe('passenger_closed',
                                   self.on_passenger_session_closed)

        # Start periodic refreshing
        self._refresh()

    def watch(self, passenger_id, location, immediate_assign=True):
        # Register watch
        watch = self._watches_by_passenger.get(passenger_id)
        if watch is None:
            watch = Watch(passenger_id, location)
            self._watches_by_passenger[passenger_id] = watch

        # Update passnger location
        watch.update_location(location)

        if immediate_assign:
            self.assign(passenger_id)

    def unwatch(self, passenger_id):
        watch = self._watches_by_passenger[passenger_id]
        if watch:
            self._remove_matches_by_watch(watch)
        try:
            del self._watches_by_passenger[passenger_id]
        except KeyError:
            self.error('Failed to remove {0}'.format(passenger_id))

    @gen.coroutine
    def assign(self, passenger_id):
        self.debug('Assigning for Passenger {0}'.format(passenger_id))

        watch = self._watches_by_passenger.get(passenger_id)
        if watch is None:
            self.warn('No watch for passenger {0}'.format(passenger_id))
            return

        # Clean up old assignment information
        self._remove_matches_by_watch(watch)

        old_assignment = watch.assignment

        # TODO: Consider already matched drivers
        candidates = yield LocationManager().get_driver_candidates(
            watch.location)

        best = None
        for candidate in candidates:
            driver_id = candidate['driver']['id']

            self._matches_by_driver[driver_id].add(passenger_id)

            if driver_id in self._best_matches_by_driver:
                continue
            if not best or candidate['estimate'].time < best['estimate'].time:
                best = candidate
        if not best:
            # Heuristic. First one is the closest one, FYI
            best = assignment['candidates'][0]

        self._best_matches_by_driver[best['driver']['id']] = passenger_id

        assignment = {'candidates': candidates, 'best': best}

        watch.assignment = assignment

        if not self._is_same_assignment(old_assignment, assignment):
            SessionManager().get(passenger_id).notify_passenger_assign(
                assignment)

    def on_driver_activated(self, driver_id, location):
        # FIXME: Find nearby passengers andrematch
        pass

    def on_driver_deactivated(self, driver_id, last_location):
        to_assign = set()

        passenger_id = self._best_matches_by_driver.get(driver_id)
        if passenger_id:
            del self._best_matches_by_driver[driver_id]
            to_assign.add(passenger_id)

        # Remove from matches
        passengers = self._matches_by_driver[driver_id]
        for passenger_id in passengers:
            passengers.remove(passenger_id)
            to_assign.add(passenger_id)

        self.debug(
            'Driver {driver} was deactivated so reassigning for {count} '
            'passenger(s)'.format(driver=driver_id, count=len(to_assign)))

        for passenger_id in to_assign:
            self.assign(passenger_id)

    def on_passenger_session_closed(self, user_id, old_session):
        if user_id in self._watches_by_passenger:
            self.debug('Passenger {passenger} was closed so unwatching '
                       'it'.format(passenger=user_id))
            self.unwatch(user_id)

    # Private
    # -------

    def _remove_matches_by_watch(self, watch):
        for driver_id in watch.driver_ids:
            # Remove from matches
            self._matches_by_driver[driver_id].remove(watch.passenger_id)

            # Remove from best matches
            if (self._best_matches_by_driver.get(driver_id)
                    == watch.passenger_id):
                del self._best_matches_by_driver[driver_id]

    def _is_same_assignment(self, a1, a2):
        # FIXME: Implement (deep comparison of dict and list objects)
        return False

    def _refresh(self):
        self.debug('Refreshing {0} watches'.format(len(
            self._watches_by_passenger)))

        zombies = []

        for passenger_id, watch in self._watches_by_passenger.iteritems():
            if not SessionManager().is_live(passenger_id):
                zombies.append(passenger_id)
                continue

            SessionManager().get(passenger_id).notify_passenger_assign(
                watch.assignment)

        for passenger_id in zombies:
            self.debug('It seems Passenger {passenger} was closed so '
                       'unwatching it'.format(passenger=passenger_id))
            self.unwatch(passenger_id)

        delay(self.refresh_interval, self._refresh)


