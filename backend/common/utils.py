import datetime

import pytz as pytz


def now_in_utc():
    datetime.datetime.now(pytz.UTC)
