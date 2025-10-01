"""
ASGI config for bmstu project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bmstu.settings')

application = get_asgi_application()