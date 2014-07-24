import functools
import re

from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


class UsernameValidator(validators.RegexValidator):
    regex = re.compile('^[\w.+-]{3,30}$')
    message = _('Must contain only letters, numbers and ./+/-/_ characters '
                'and have 6~30 characters.')
    code = 'username'


class PasswordValidator(validators.RegexValidator):
    regex = re.compile('^.{6,30}$')
    message = _('Must have 6~30 characters.')
    code = 'password'


class PhoneValidator(validators.RegexValidator):
    regex = re.compile('^\d{10,11}$')
    message = _('Must be 10 or 11 digits')
    code = 'phone'


validate_username = UsernameValidator()
validate_password = PasswordValidator()
validate_phone = PhoneValidator()
validate_email = validators.validate_email
validate_url = validators.URLValidator()


def _validation_wrapper(validator, value):
    try:
        validator(value)
    except ValidationError:
        return False
    else:
        return True

is_valid_username = functools.partial(_validation_wrapper, validate_username)
is_valid_password = functools.partial(_validation_wrapper, validate_password)
is_valid_phone = functools.partial(_validation_wrapper, validate_phone)
is_valid_url = functools.partial(_validation_wrapper, validate_url)
is_valid_email = functools.partial(_validation_wrapper, validate_email)
