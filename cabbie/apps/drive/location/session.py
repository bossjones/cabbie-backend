from django.conf import settings

from cabbie.utils.ioloop import delay
from cabbie.utils.log import LoggableMixin
from cabbie.utils.meta import SingletonMixin
from cabbie.utils.pubsub import PubsubMixin


class SessionBufferManager(LoggableMixin, SingletonMixin, PubsubMixin):

    def __init__(self):
        super(SessionBufferManager, self).__init__()
        self._session_buffers = {}

    def get_or_create(self, user_id):
        session_buffer = self._session_buffers.get(user_id)

        from cabbie.apps.drive.location.server import SessionBuffer
        if session_buffer is None:
            # create new one
            session_buffer = SessionBuffer(user_id)
            self.add(user_id, session_buffer)
        else:
            self.debug('Session buffer cached for {0}'.format(user_id))

        return session_buffer
 
    def add(self, user_id, session_buffer):
        self._session_buffers[user_id] = session_buffer
        self.debug('Session buffer for {0} added'.format(user_id))

    def remove(self, user_id):
        try:
            del self._session_buffers[user_id]
            self.info('Remove user {id} session buffer'.format(id=user_id))
        except KeyError:
            self.error('Failed to remove {0} session buffer'.format(user_id))

              
        

       

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
        self.info('Add user {id} session {session}'.format(id=user_id, session=hex(id(session))))
        self.publish('{role}_opened'.format(role=session.role),
                     user_id, session)

    def remove(self, user_id, session):
        old_session = self._sessions.get(user_id, None)

        if old_session is not None and id(session) != id(old_session):
            self.info('Don\'t remove old_session {0} because closed one is {1}'.format(hex(id(old_session)), hex(id(session))))
            return

        try:
            del self._sessions[user_id]
            self.info('Remove user {id} session {session}'.format(id=user_id, session=hex(id(old_session))))
        except KeyError:
            self.error('Failed to remove {0} session'.format(user_id))

        # Have buffer before broadcasting the session-closed event
        def on_delay():
            if user_id not in self._sessions:
                self.publish('{role}_closed'.format(role=old_session.role),
                            user_id, old_session)
        delay(self.session_close_timeout, on_delay)
