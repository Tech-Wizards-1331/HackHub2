import os
import sys

path = '/home/AnshPatoliya/syntra/backend'
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'syntra.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()