# marty mcfly imports
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

# stdlib imports
import codecs
import datetime
import sys


UTF8Writer = codecs.getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)


def logger(message, level='INFO'):
    """
    Logs a given message to stdout (via print atm, should probably use a real
    logging framework)
    """
    now = datetime.datetime.utcnow()
    print(u"[{0}] {1}: {2}".format(now.strftime('%Y-%m-%d %H:%M:%S'), level, message))
