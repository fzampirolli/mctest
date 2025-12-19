from django.core.cache import cache
from django.utils import timezone

class ActiveUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Salva no cache que este usuário foi visto AGORA
            # O cache expira automaticamente em 300 segundos (5 minutos)
            cache.set(f'last_seen_{request.user.id}', timezone.now(), 300)

        response = self.get_response(request)
        return response