"""
=============================================================================
INSTITUTO POLITÉCNICO - UNIKIVI
Linguagem de Programação VI (Python)
Trabalho Prático - Sistema Inteligente de Gestão de Inventário com IA
=============================================================================
Ficheiro: config/settings.py
Descrição: Configurações globais da aplicação (base de dados, GUI, IA).
=============================================================================
"""

# ---------------------------------------------------------------------------
# Configurações da Base de Dados (MongoDB)
# ---------------------------------------------------------------------------
MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_DATABASE = "inventario_ia_db"
MONGO_URI = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/{MONGO_DATABASE}"

# ---------------------------------------------------------------------------
# Configurações da Aplicação GUI
# ---------------------------------------------------------------------------
APP_TITLE = "InventárioIA - Sistema Inteligente de Gestão de Inventário"
APP_WIDTH = 1200
APP_HEIGHT = 700
APP_MIN_WIDTH = 900
APP_MIN_HEIGHT = 600

# Tema e aparência (customtkinter)
APPEARANCE_MODE = "dark"          # "dark" | "light" | "system"
COLOR_THEME = "blue"              # "blue" | "green" | "dark-blue"

# Paleta de cores personalizada
COLORS = {
    "primary":        "#1f6aa5",   # Azul principal
    "primary_hover":  "#144870",   # Azul escuro (hover)
    "secondary":      "#2b2b2b",   # Fundo secundário
    "sidebar":        "#1a1a2e",   # Fundo do menu lateral
    "sidebar_hover":  "#16213e",   # Hover no menu lateral
    "card_bg":        "#2b2b2b",   # Fundo dos cartões do dashboard
    "success":        "#28a745",   # Verde (sucesso / stock OK)
    "warning":        "#ffc107",   # Amarelo (atenção / stock baixo)
    "danger":         "#dc3545",   # Vermelho (erro / stock crítico)
    "text_primary":   "#ffffff",   # Texto principal
    "text_secondary": "#a0a0a0",   # Texto secundário
}

# Fontes
FONTS = {
    "title":    ("Segoe UI", 24, "bold"),
    "subtitle": ("Segoe UI", 16, "bold"),
    "body":     ("Segoe UI", 13),
    "small":    ("Segoe UI", 11),
    "button":   ("Segoe UI", 13, "bold"),
    "mono":     ("Consolas",  12),
}

# ---------------------------------------------------------------------------
# Configurações de Negócio
# ---------------------------------------------------------------------------
# Stock mínimo considerado "baixo"
STOCK_LOW_THRESHOLD = 10

# Número de meses de histórico para alimentar o modelo de IA
IA_HISTORY_MONTHS = 12

# Número de meses futuros para prever
IA_FORECAST_MONTHS = 3

# Caminho para guardar o modelo treinado (pickle)
MODEL_SAVE_PATH = "reports/modelo_ia.pkl"

# Caminho padrão para exportação CSV
CSV_EXPORT_PATH = "reports/"

# ---------------------------------------------------------------------------
# Configurações de Segurança
# ---------------------------------------------------------------------------
# Número máximo de tentativas de login antes de bloquear
MAX_LOGIN_ATTEMPTS = 5

# Tempo de sessão em minutos (0 = sem expiração)
SESSION_TIMEOUT_MINUTES = 60

# ---------------------------------------------------------------------------
# Versão
# ---------------------------------------------------------------------------
APP_VERSION = "1.0.0"
APP_AUTHOR  = "Instituto Politécnico - UNIKIVI"
APP_YEAR    = "2026"
