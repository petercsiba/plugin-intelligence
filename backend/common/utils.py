import datetime
import time

import pytz as pytz
from peewee import Model


def print_peewee_model(model: Model):
    print(model.__name__)

    for field_name, field in model._meta.fields.items():
        value = getattr(model, field_name)
        print(f"{field_name}: {value}")


def now_in_utc():
    datetime.datetime.now(pytz.UTC)


class Timer:
    def __init__(self, label):
        self.label = label

    def __enter__(self):
        self.start_time = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed_time = time.time() - self.start_time
        print("{}: {:.2f} seconds".format(self.label, elapsed_time))
