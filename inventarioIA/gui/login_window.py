"""
=============================================================================
Ficheiro: gui/login_window.py
Descrição: Janela de autenticação (Login) construída com CustomTkinter.
           Design moderno com validação em tempo real e feedback visual.
=============================================================================
"""

import logging
import customtkinter as ctk
from tkinter import messagebox
from typing import Callable, Optional

from services.auth_service import AuthService
from exceptions.auth_exception import (
    AuthException,
    MaxLoginAttemptsException,
    SessionExpiredException,
)
from config.settings import (
    APP_TITLE,
    COLORS,
    FONTS,
    APP_VERSION,
    APP_AUTHOR,
)

logger = logging.getLogger(__name__)


class LoginWindow(ctk.CTk):
    """
    Janela de Login da aplicação.

    Funcionalidades:
      - Formulário de login com username e password.
      - Botão de mostrar/ocultar password.
      - Mensagens de erro/sucesso inline.
      - Tecla Enter para submeter o formulário.
      - Indicador visual de tentativas restantes.
      - Link para criar conta (se autorizado).
    """

    def __init__(
        self,
        auth_service: AuthService,
        on_login_success: Callable,
    ) -> None:
        """
        Parâmetros:
            auth_service     : Serviço de autenticação injectado.
            on_login_success : Callback chamado após login bem-sucedido.
        """
        super().__init__()

        self._auth_service = auth_service
        self._on_login_success = on_login_success
        self._tentativas: int = 0
        self._password_visivel: bool = False

        self._configurar_janela()
        self._construir_interface()

    # =================================================================
    # Configuração da Janela
    # =================================================================

    def _configurar_janela(self) -> None:
        """Configura propriedades base da janela."""
        self.title(f"Login — {APP_TITLE}")
        self.geometry("480x580")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["secondary"])

        # Centraliza a janela no ecrã
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 480) // 2
        y = (self.winfo_screenheight() - 580) // 2
        self.geometry(f"480x580+{x}+{y}")

        # Handler para fechar a janela
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # =================================================================
    # Construção da Interface
    # =================================================================

    def _construir_interface(self) -> None:
        """Constrói todos os widgets da janela de login."""
        # Frame principal centralizado
        frame_principal = ctk.CTkFrame(
            self,
            fg_color=COLORS["card_bg"],
            corner_radius=20,
        )
        frame_principal.pack(
            fill="both", expand=True, padx=40, pady=40
        )

        # ---- Logo / Ícone ----
        label_icone = ctk.CTkLabel(
            frame_principal,
            text="📦",
            font=("Segoe UI", 64),
        )
        label_icone.pack(pady=(30, 5))

        # ---- Título ----
        label_titulo = ctk.CTkLabel(
            frame_principal,
            text="InventárioIA",
            font=FONTS["title"],
            text_color=COLORS["primary"],
        )
        label_titulo.pack(pady=(0, 4))

        # ---- Subtítulo ----
        label_subtitulo = ctk.CTkLabel(
            frame_principal,
            text="Sistema Inteligente de Gestão de Inventário",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"],
        )
        label_subtitulo.pack(pady=(0, 25))

        # ---- Campo Username ----
        ctk.CTkLabel(
            frame_principal,
            text="Nome de Utilizador",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"],
            anchor="w",
        ).pack(fill="x", padx=30)

        self._entry_username = ctk.CTkEntry(
            frame_principal,
            placeholder_text="  ex: admin",
            height=44,
            font=FONTS["body"],
            corner_radius=10,
        )
        self._entry_username.pack(fill="x", padx=30, pady=(4, 14))
        self._entry_username.bind("<Return>", lambda e: self._entry_password.focus())

        # ---- Campo Password ----
        ctk.CTkLabel(
            frame_principal,
            text="Palavra-passe",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"],
            anchor="w",
        ).pack(fill="x", padx=30)

        frame_password = ctk.CTkFrame(
            frame_principal, fg_color="transparent"
        )
        frame_password.pack(fill="x", padx=30, pady=(4, 5))

        self._entry_password = ctk.CTkEntry(
            frame_password,
            placeholder_text="  ••••••••",
            show="•",
            height=44,
            font=FONTS["body"],
            corner_radius=10,
        )
        self._entry_password.pack(side="left", fill="x", expand=True)
        self._entry_password.bind("<Return>", lambda e: self._realizar_login())

        self._btn_toggle_pass = ctk.CTkButton(
            frame_password,
            text="👁",
            width=44,
            height=44,
            corner_radius=10,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            command=self._toggle_password,
        )
        self._btn_toggle_pass.pack(side="right", padx=(6, 0))

        # ---- Mensagem de Erro/Sucesso ----
        self._label_mensagem = ctk.CTkLabel(
            frame_principal,
            text="",
            font=FONTS["small"],
            text_color=COLORS["danger"],
            wraplength=360,
        )
        self._label_mensagem.pack(pady=(8, 4))

        # ---- Botão de Login ----
        self._btn_login = ctk.CTkButton(
            frame_principal,
            text="Entrar no Sistema",
            height=46,
            font=FONTS["button"],
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            corner_radius=12,
            command=self._realizar_login,
        )
        self._btn_login.pack(fill="x", padx=30, pady=(10, 8))

        # ---- Separador ----
        ctk.CTkLabel(
            frame_principal,
            text="─────────────────────────────",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"],
        ).pack(pady=(4, 4))

        # ---- Rodapé ----
        ctk.CTkLabel(
            frame_principal,
            text=f"{APP_AUTHOR}  •  v{APP_VERSION}",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"],
        ).pack(pady=(0, 20))

        # Foco inicial no campo username
        self._entry_username.focus()

    # =================================================================
    # Lógica de Login
    # =================================================================

    def _realizar_login(self) -> None:
        """Processa a tentativa de login."""
        username = self._entry_username.get().strip()
        password = self._entry_password.get()

        # Validação básica dos campos
        if not username:
            self._mostrar_erro("Por favor, introduza o nome de utilizador.")
            self._entry_username.focus()
            return

        if not password:
            self._mostrar_erro("Por favor, introduza a palavra-passe.")
            self._entry_password.focus()
            return

        # Desactiva o botão durante o processamento
        self._btn_login.configure(state="disabled", text="A verificar...")
        self.update()

        try:
            utilizador = self._auth_service.verificar_credenciais(username, password)

            # Login bem-sucedido
            self._mostrar_sucesso(
                f"Bem-vindo, {utilizador.nome_completo or utilizador.username}!"
            )
            self.update()

            # Aguarda brevemente para mostrar a mensagem de sucesso
            self.after(800, lambda: self._on_login_success(utilizador))

        except MaxLoginAttemptsException as e:
            self._tentativas += 1
            self._mostrar_erro(str(e))
            self._btn_login.configure(state="disabled", text="Conta Bloqueada")
            logger.warning(f"Login bloqueado: '{username}'")

        except AuthException as e:
            self._tentativas += 1
            self._mostrar_erro(str(e).replace("[InvalidCredentialsException] ", "")
                               .replace("[UserNotFoundException] ", ""))
            self._entry_password.delete(0, "end")
            self._entry_password.focus()
            # Reactiva o botão
            self._btn_login.configure(state="normal", text="Entrar no Sistema")

        except ConnectionError as e:
            self._mostrar_erro(
                "Erro de ligação à base de dados.\n"
                "Verifique se o MongoDB está em execução."
            )
            self._btn_login.configure(state="normal", text="Entrar no Sistema")
            logger.error(f"Erro de conexão no login: {e}")

        except Exception as e:
            self._mostrar_erro(f"Erro inesperado: {e}")
            self._btn_login.configure(state="normal", text="Entrar no Sistema")
            logger.error(f"Erro inesperado no login: {e}")

    def _toggle_password(self) -> None:
        """Alterna a visibilidade da palavra-passe."""
        self._password_visivel = not self._password_visivel
        self._entry_password.configure(
            show="" if self._password_visivel else "•"
        )
        self._btn_toggle_pass.configure(
            text="🔒" if self._password_visivel else "👁"
        )

    # =================================================================
    # Mensagens de Feedback
    # =================================================================

    def _mostrar_erro(self, mensagem: str) -> None:
        """Exibe mensagem de erro em vermelho."""
        self._label_mensagem.configure(
            text=f"⚠  {mensagem}", text_color=COLORS["danger"]
        )

    def _mostrar_sucesso(self, mensagem: str) -> None:
        """Exibe mensagem de sucesso em verde."""
        self._label_mensagem.configure(
            text=f"✓  {mensagem}", text_color=COLORS["success"]
        )

    def _limpar_mensagem(self) -> None:
        """Limpa a mensagem de feedback."""
        self._label_mensagem.configure(text="")

    # =================================================================
    # Handlers de Janela
    # =================================================================

    def _on_close(self) -> None:
        """Handler para fechar a aplicação."""
        if messagebox.askyesno(
            "Sair",
            "Tem a certeza que deseja sair da aplicação?",
            parent=self,
        ):
            logger.info("Aplicação encerrada pelo utilizador.")
            self.destroy()
