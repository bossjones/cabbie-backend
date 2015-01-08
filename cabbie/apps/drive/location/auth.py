from rest_framework.authtoken.models import Token

from cabbie.utils.log import LoggableMixin
from cabbie.utils.meta import SingletonMixin


class Authenticator(LoggableMixin, SingletonMixin):
    """Authenticates (web)socket connections with token."""

    # TODO: Cache (token, user_id) pair

    def authenticate(self, token, role):
        try:
            user = Token.objects.select_related('user').get(key=token).user
        except Token.DoesNotExist:
            return None
        else:
            # Double check if the user has specified role
            role = user.get_role(role)
            return user if role is not None else None
