# Arquivo para constantes úteis.

# Biblioteca que permite o acesso ao SO
import os

# Host do servidor de email
SMTP_HOST: str = "localhost"
# Porta do servidor de email
SMTP_PORT: int = 8025
# Tempo permitido de espera do envio, antes de gerar erro
SMTP_TIMEOUT: int = 5

# Email principal da aplicação
EMAIL_FROM: str = "master@dundie.com"

# Caminho raiz do app
ROOT_PATH: str = os.path.dirname(__file__)
# Caminho do banco de dados principal
DATABASE_PATH: str = os.path.join(ROOT_PATH, "..", "assets", "database.json")
