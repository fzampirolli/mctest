import ssl
from django.core.mail.backends.smtp import EmailBackend

class WeakSSLEmailBackend(EmailBackend):
    """
    Backend personalizado para permitir conexão com servidores SMTP antigos
    (como o da UFABC) que usam chaves DH curtas.
    Força o SECLEVEL=1 apenas para o envio de e-mail.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Cria um contexto SSL que aceita segurança legada (Nível 1)
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.set_ciphers('DEFAULT@SECLEVEL=1')
