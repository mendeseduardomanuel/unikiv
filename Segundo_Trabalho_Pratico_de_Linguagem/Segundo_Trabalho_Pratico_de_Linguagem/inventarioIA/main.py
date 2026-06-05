"""
=============================================================================
INSTITUTO POLITÉCNICO - UNIKIVI
Linguagem de Programação VI (Python)
=============================================================================
Ficheiro: main.py
Descrição: Ponto de entrada da aplicação InventárioIA.
           Inicializa a base de dados, configura o logging, e lança a GUI.
=============================================================================
"""

import sys
import os
import logging
from pathlib import Path

# Adiciona a raiz do projecto ao PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

import customtkinter as ctk

from config.settings import (
    APPEARANCE_MODE,
    COLOR_THEME,
    APP_TITLE,
)
from database.connection import DatabaseConnection


# =============================================================================
# Configuração do Logging
# =============================================================================
def configurar_logging() -> None:
    """
    Configura o sistema de logging da aplicação.
    - Nível DEBUG em consola durante desenvolvimento.
    - Ficheiro de log para auditoria.
    """
    os.makedirs("logs", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(
                f"logs/inventario_ia.log",
                encoding="utf-8",
                mode="a",
            ),
        ],
    )
    # Reduz verbosidade de bibliotecas externas
    logging.getLogger("mongoengine").setLevel(logging.WARNING)
    logging.getLogger("pymongo").setLevel(logging.WARNING)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)


# =============================================================================
# Inicialização da Base de Dados
# =============================================================================
def inicializar_base_dados() -> DatabaseConnection:
    """
    Estabelece a ligação ao MongoDB e cria o administrador padrão.

    Returns:
        DatabaseConnection: Instância da ligação activa.

    Raises:
        SystemExit: Se não for possível conectar ao MongoDB.
    """
    logger = logging.getLogger(__name__)
    db = DatabaseConnection.get_instance()

    try:
        db.connect()
        logger.info("MongoDB inicializado com sucesso.")

        # Garante que existe pelo menos um utilizador admin
        from services.auth_service import AuthService
        AuthService.garantir_admin_padrao()

        return db

    except ConnectionError as e:
        logger.critical(f"Falha crítica ao conectar ao MongoDB: {e}")
        # Mostra diálogo de erro antes de sair
        _mostrar_erro_conexao(str(e))
        sys.exit(1)


def _mostrar_erro_conexao(mensagem: str) -> None:
    """Mostra uma janela de erro de conexão simples."""
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Erro de Conexão — InventárioIA",
            f"Não foi possível conectar ao MongoDB.\n\n"
            f"{mensagem}\n\n"
            "Solução:\n"
            "1. Abra o terminal.\n"
            "2. Execute: mongod --dbpath ./data/db\n"
            "3. Reinicie a aplicação.",
        )
        root.destroy()
    except Exception:
        print(f"\n[ERRO CRÍTICO] {mensagem}")
        print("Verifique se o MongoDB está em execução.")


# =============================================================================
# Inicialização dos Serviços
# =============================================================================
def criar_servicos() -> tuple:
    """
    Instancia todos os serviços da aplicação.
    Implementa o padrão de Injecção de Dependências.

    Returns:
        tuple: (auth_svc, produto_svc, venda_svc, ia_svc)
    """
    from services.auth_service import AuthService
    from services.produto_service import ProdutoService
    from services.venda_service import VendaService
    from services.ia_service import IAService

    auth_svc    = AuthService()
    produto_svc = ProdutoService()
    ia_svc      = IAService()
    venda_svc   = VendaService(produto_service=produto_svc)

    # Tenta carregar modelo IA previamente treinado
    ia_svc.carregar_modelo()

    return auth_svc, produto_svc, venda_svc, ia_svc


# =============================================================================
# Lançamento da GUI
# =============================================================================
def iniciar_login() -> None:
    """
    Lança a janela de login da aplicação.
    Após autenticação bem-sucedida, abre o Dashboard.
    """
    logger = logging.getLogger(__name__)

    # Configura aparência global do CustomTkinter
    ctk.set_appearance_mode(APPEARANCE_MODE)
    ctk.set_default_color_theme(COLOR_THEME)

    auth_svc, produto_svc, venda_svc, ia_svc = criar_servicos()

    def ao_fazer_login(utilizador) -> None:
        """Callback executado após login bem-sucedido."""
        logger.info(f"Abrindo dashboard para: {utilizador.username}")
        login_window.destroy()

        from gui.dashboard import DashboardWindow
        dashboard = DashboardWindow(
            auth_service=auth_svc,
            produto_service=produto_svc,
            venda_service=venda_svc,
            ia_service=ia_svc,
        )
        dashboard.mainloop()

    from gui.login_window import LoginWindow
    login_window = LoginWindow(
        auth_service=auth_svc,
        on_login_success=ao_fazer_login,
    )
    login_window.mainloop()


# =============================================================================
# Ponto de Entrada Principal
# =============================================================================
def main() -> None:
    """Função principal da aplicação."""
    configurar_logging()
    logger = logging.getLogger(__name__)

    logger.info("=" * 60)
    logger.info(f"  Iniciando {APP_TITLE}")
    logger.info("  Instituto Politécnico - UNIKIVI")
    logger.info("  Linguagem de Programação VI — Python")
    logger.info("=" * 60)

    # Inicializa a base de dados
    inicializar_base_dados()

    # Lança a interface gráfica
    iniciar_login()

    logger.info("Aplicação encerrada.")


if __name__ == "__main__":
    main()
