from django.conf import settings

from cabbie.utils.ioloop import delay
from cabbie.utils.log import LoggableMixin
from cabbie.utils.meta import SingletonMixin
from cabbie.utils.pubsub import PubsubMixin


class SessionManager(LoggableMixin, SingletonMixin, PubsubMixin):
    """Central point to manage all concurrent (web)socket connections."""

    # TODO: Heartbeating periodically to check if connection is live (ping)
    # TODO: Buffer session-related function calls when a session is temporarily
    # unavailable

    session_close_timeout = settings.SESSION_CLOSE_TIMEOUT

    def __init__(self):
        super(SessionManager, self).__init__()
        self._sessions = {}

    def is_live(self, user_id):
        return user_id in self._sessions

    def get(self, user_id):
        return self._sessions.get(user_id)

    def add(self, user_id, session):
        self._sessions[user_id] = session
        self.publish('{role}_opened'.format(role=session.role),
                     user_id, session)

    def remove(self, user_id):
        old_session = self._sessions.get(user_id)
        try:
            del self._sessions[user_id]
        except KeyError:
            self.error('Failed to remove {0}'.format(user_id))

        # Have buffer before broadcasting the session-closed event
        def on_delay():
            if user_id not in self._sessions:
                self.publish('{role}_closed'.format(role=old_session.role),
                            user_id, old_session)
        delay(self.session_close_timeout, on_delay)
