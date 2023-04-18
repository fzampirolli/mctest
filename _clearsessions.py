# python manage.py shell < _clearsessions.py

from django.contrib.sessions.models import Session

Session.objects.all()
Session.objects.all().delete()
