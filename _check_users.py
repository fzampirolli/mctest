# python3 manage.py shell < _check_users.py

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mctest.settings')
import django
django.setup()
from django.contrib.sessions.models import Session
from django.utils import timezone
from account.models import User

# Remova as sessões expiradas
Session.objects.filter(expire_date__lt=timezone.now()).delete()

# Obtenha a lista de usuários atualmente logados
sessions = Session.objects.filter(expire_date__gte=timezone.now())
uid_list = [data.get('_auth_user_id', None) for data in [session.get_decoded() for session in sessions]]
users_now = User.objects.filter(id__in=uid_list)
print(users_now.count())