from cabbie.utils.log import LoggableMixin
from cabbie.utils.meta import SingletonMixin
from cabbie.utils.pubsub import PubsubMixin


class SessionManager(LoggableMixin, SingletonMixin, PubsubMixin):
    """Central point to manage all concurrent (web)socket connections."""

    # TODO: Heartbeating periodically to check if connection is live (ping)

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
        self.publish('{role}_closed'.format(role=old_session.role),
                     user_id, old_session)
