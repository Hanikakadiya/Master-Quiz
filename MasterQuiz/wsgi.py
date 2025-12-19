"""
WSGI config for MasterQuiz project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
# Import the OS module to interact with environment variables and the operating system

from django.core.wsgi import get_wsgi_application
# Import Django's function to get the WSGI application callable

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MasterQuiz.settings')
# Set the default Django settings module environment variable to 'MasterQuiz.settings'
# This tells Django which settings to use for this project

application = get_wsgi_application()
# Create the WSGI application callable that the WSGI server uses to forward requests to Django
# This 'application' variable is used by WSGI servers to serve your project
