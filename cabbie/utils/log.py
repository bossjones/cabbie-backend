import logging

from cabbie.utils.text import convert_to_byte

try:
    import curses
    curses.setupterm()
except ImportError:
    curses = None


class LoggableMixin(object):
    LOG_FORMAT = u'{label:20} {msg}'

    def __init__(self, *args, **kwargs):
        super(LoggableMixin, self).__init__(*args, **kwargs)
        self._logger = None
        self._logger_label = None

    def __unicode__(self):
        return self.__class__.__name__

    def __repr__(self):
        return self.__unicode__()

    @property
    def logger_label(self):
        return self._logger_label or self.__unicode__()

    @property
    def logger(self):
        if self._logger is None:
            self._logger = logging.getLogger(self.__class__.__module__)
        return self._logger

    def set_logger_label(self, label):
        self._logger_label = label

    def debug(self, msg):
        self.logger.debug(self.LOG_FORMAT.format(
            label=self.logger_label, msg=msg))

    def info(self, msg):
        self.logger.info(self.LOG_FORMAT.format(
            label=self.logger_label, msg=msg))

    def warn(self, msg):
        self.logger.warn(self.LOG_FORMAT.format(
            label=self.logger_label, msg=msg))

    def error(self, msg):
        self.logger.error(self.LOG_FORMAT.format(
            label=self.logger_label, msg=msg))

    def critical(self, msg):
        self.logger.critical(self.LOG_FORMAT.format(
            label=self.logger_label, msg=msg))



# Formatters
# ----------

class ColorFormatter(logging.Formatter):
    def __init__(self, color=True, *args, **kwargs):
        super(ColorFormatter, self).__init__(*args, **kwargs)

        self._color = color
        self._color_map = None

    @property
    def color_map(self):
        if self._color_map is None:
            fg_color = (curses.tigetstr('setaf') or
                        curses.tigetstr('setf') or '')
            self._color_map = {
                logging.INFO: unicode(curses.tparm(fg_color, 2),     # Green
                                      'ascii'),
                logging.WARNING: unicode(curses.tparm(fg_color, 3),  # Yellow
                                         'ascii'),
                logging.ERROR: unicode(curses.tparm(fg_color, 1),    # Red
                                       'ascii'),
                logging.CRITICAL: unicode(curses.tparm(fg_color, 1), # Red
                                          'ascii'),
            }
            self._normal_color = unicode(curses.tigetstr('sgr0'), 'ascii')
        return self._color_map

    def format(self, record):
        formatted = super(ColorFormatter, self).format(record)
        if self._color:
            prefix = self.color_map.get(record.levelno, self._normal_color)
            formatted = \
                convert_to_byte(prefix) \
                + convert_to_byte(formatted) \
                + convert_to_byte(self._normal_color)
        return formatted
