# encoding: utf-8

import random

from django.conf import settings

from cabbie.apps.drive.bot.base import Bot
from cabbie.utils.geo import move, distance
from cabbie.utils.ioloop import delay
from cabbie.utils.rand import Dice, random_int


class DriverBot(Bot):
    # States
    (
        INITIALIZED,
        REQUESTED,
        APPROVED,
        ARRIVED,
        BOARDED,
    ) = range(5)

    role = 'driver'
    update_location_interval = 1
    update_direction_interval = 1
    update_charge_type_interval = 1
    move_interval = 0.5
    board_delay = 5
    gentle_delay = 1
    distance_error_bound = 25

    reject_reason_dice = Dice(
        (u'기분이 별로 안좋아서 지금은 안되겠습니다.', 5),
        (u'목적지가 마음에 들지 않습니다.', 3),
        (u'차에 기름이 부족합니다.', 2),
        (u'그냥 싫습니다.', 1),
    )

    def __init__(self, instance, start_location, speed, reject_dice,
                 charge_type_change_dice, direction_change_dice):
        super(DriverBot, self).__init__(instance)
        self._location = start_location
        self._speed = speed
        self._reject_dice = reject_dice
        self._charge_type_change_dice = charge_type_change_dice
        self._direction_change_dice = direction_change_dice

        self._activated = True
        self._state = None
        self._target_location = None
        self._source = None
        self._destination = None

        self._charge_type = None
        self._direction = None

        self.subscribe('move', self.on_move)

    @property
    def is_bounded(self):
        return (
            settings.BOT_LONGITUDE_RANGE[0] <= self._location[0]
            <= settings.BOT_LONGITUDE_RANGE[1]
            and settings.BOT_LATITUDE_RANGE[0] <= self._location[1]
            <= settings.BOT_LATITUDE_RANGE[1])

    # Handlers
    # --------

    def handle_auth_succeeded(self):
        self.info('Auth succeded')

        self._state = self.INITIALIZED

        self._update_direction()
        self._update_charge_type()
        self._update_location()
        self._move()

    def handle_driver_requested(self, source, destination, passenger):
        self.info('Requested from {0}'.format(passenger))

        if self._reject_dice.roll():
            delay(self.gentle_delay, self._reject)
        else:
            self._source = source
            self._destination = destination
            delay(self.gentle_delay, self._approve)

    def handle_driver_canceled(self):
        self.info('Canceled')

        self._head_to(None)
        self._state = self.INITIALIZED

    def handle_driver_disconnected(self):
        self.info('Disconnected')

        self._head_to(None)
        self._state = self.INITIALIZED

    # Pubsub
    # ------

    def on_move(self, new_location, old_location, meters):
        if (self._target_location
                and distance(self._location, self._target_location)
                     <= self.distance_error_bound):
            self._target_location = None
            if self._state == self.APPROVED:
                self._arrive()
            elif self._state == self.BOARDED:
                self._complete()

    # Actions
    # -------

    def _deactivate(self):
        self.info('Deactivating')
        self._activated = False

    def _approve(self):
        self.info('Approving')
        self.send('driver_approve')
        self._state = self.APPROVED

        self._head_to(self._source['location'])

    def _reject(self, reason=None):
        self.info('Rejecting')
        self.send('driver_reject', {
            'reason': reason or self.reject_reason_dice.roll(),
        })
        self._state = self.INITIALIZED

    def _arrive(self):
        self.info('Arriving')
        self.send('driver_arrive')
        self._state = self.ARRIVED

        delay(self.board_delay, self._board)

    def _board(self):
        self.info('Boarding')
        self.send('driver_board')
        self._state = self.BOARDED
        self._head_to(self._destination['location'])

    def _complete(self):
        self.info('Completing')
        # TODO: Change this test data
        self.send('driver_complete', {
            'summary': {
                'distance': 'test',
                'time': 'test',
            }
        })
        self._state = self.INITIALIZED

    # Private
    # -------

    def _head_to(self, target_location):
        self.info('Heading to {0}'.format(target_location))
        self._target_location = target_location

    def _move(self):
        if self._stopped:
            return

        if self._state in (self.INITIALIZED, self.APPROVED, self.BOARDED):
            old_location = self._location
            meters = self._speed * self.move_interval * 1000 / 3600.0
            self._location = move(self._location, meters, self._direction)
            self.publish('move', self._location, old_location, meters)

        delay(self.move_interval, self._move)

    def _update_direction(self):
        if self._stopped:
            return

        if self._target_location:
            self._direction = map(sum, zip(self._target_location,
                                        map(lambda x: x * -1, self._location)))
        elif not self.is_bounded:
            self.debug('Boundary reached, so reversing the direction')
            self._direction = map(lambda x: x * -1, self._direction)
        elif self._direction is None or self._direction_change_dice.roll():
            while True:
                self._direction = (random_int(-10, 10), random_int(-10, 10))
                if sum(self._direction):
                    self.debug('Changing direction to {0}'.format(
                        self._direction))
                    break

        delay(self.update_direction_interval, self._update_direction)

    def _update_charge_type(self):
        if self._stopped:
            return

        if self._charge_type is None or self._charge_type_change_dice.roll():
            self._charge_type = random.choice(['0', '1000', '2000'])
            self.debug('Changing charge type to `{0}`'.format(
                self._charge_type))

        delay(self.update_charge_type_interval, self._update_charge_type)

    def _update_location(self):
        if self._stopped:
            return

        if (self._activated and self._state in (
                self.INITIALIZED, self.APPROVED, self.BOARDED)):
            self.send('driver_update_location', {
                'charge_type': self._charge_type,
                'location': self._location,
            })

        delay(self.update_location_interval, self._update_location)
