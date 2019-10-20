from django.contrib.sessions.models import Session

Session.objects.all()
Session.objects.all().delete()
