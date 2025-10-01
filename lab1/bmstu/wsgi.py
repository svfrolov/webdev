"""
WSGI config for bmstu project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bmstu.settings')

application = get_wsgi_application()