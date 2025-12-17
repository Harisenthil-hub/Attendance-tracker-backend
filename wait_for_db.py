import time
import os
import django
from django.db import connections
from django.db.utils import OperationalError

os.environ.setdefault('DJANGO_SETTINGS_MODULE','myproject.settings')
django.setup()

print('Waiting for Database')

db_up = False
while not db_up:
    try:
        connections['default'].cursor()
        db_up = True
    except OperationalError:
        print('Database not yet Ready. Waiting for 2 seconds to  try again.')
        time.sleep(2)

print("Database is ready!")