# Biblioteca para expressões regulares (regex)
import re

# Biblioteca para envio de e-mails
import smtplib

# Template para e-mails
from email.mime.text import MIMEText

# Importando variáveis de informações
from dundie.settings import SMTP_HOST, SMTP_PORT, SMTP_TIMEOUT
from dundie.utils.log import get_logger

# Definindo um logger
log = get_logger()

# `r` indica uma "raw string", não é formato usando a tabela de caracteres
# UTF-8, será salvo e passado da exata maneira que foi escrito.
regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"


# Função para validar se um e-mail está num formato válido usando regex
def check_valid_email(address):
    """Return True if email is valid."""
    return bool(re.fullmatch(regex, address))


# Função para enviar e-mail para uma pessoa
def send_email(from_, to, subject, text):
    # Verifica se a variável dos destinatários é uma lista, senão for,
    # transforma a variável numa lista.
    if not isinstance(to, list):
        to = [to]

    try:
        # Abre um servidor de e-mail SMTP para o envio.
        with smtplib.SMTP(
            host=SMTP_HOST, port=SMTP_PORT, timeout=SMTP_TIMEOUT
        ) as server:

            # Criando uma estrutura de e-mail a partir de um template.
            message = MIMEText(text)

            # Passando o assunto, remetente e destinatário para o template.
            message["Subject"] = subject
            message["From"] = from_
            message["To"] = ",".join(to)

            # Enviando o e-mail
            server.sendmail(from_, to, message.as_string())

    # Captura qualquer exceção caso não consiga
    # se comunicar com o servidor de e-mail.
    except Exception:
        log.error("Cannot send email to %s", to)
