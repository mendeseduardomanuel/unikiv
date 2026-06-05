"""
=============================================================================
Ficheiro: gui/dashboard.py
Descrição: Janela principal com sidebar completa, controlo de acesso por papel
           (admin vs operador), botão de logout visível e navegação completa.
=============================================================================
"""

import logging
import customtkinter as ctk
from tkinter import messagebox
from typing import Optional
from datetime import datetime

from services.auth_service import AuthService
from services.produto_service import ProdutoService
from services.venda_service import VendaService
from services.ia_service import IAService
from config.settings import COLORS, FONTS, APP_TITLE, APP_VERSION

logger = logging.getLogger(__name__)


class DashboardWindow(ctk.CTk):
    """
    Janela principal após autenticação.

    Sidebar dinâmica baseada no papel do utilizador:
      ADMIN    → vê tudo + Utilizadores + Admin
      OPERADOR → Dashboard, Produtos (só leitura), Vendas, Relatórios
    """

    def __init__(self, auth_service, produto_service, venda_service, ia_service) -> None:
        super().__init__()
        self._auth        = auth_service
        self._produto_svc = produto_service
        self._venda_svc   = venda_service
        self._ia_svc      = ia_service
        self._botoes_menu: dict = {}

        self._configurar_janela()
        self._construir_sidebar()
        self._construir_area_principal()
        self._navegar("dashboard")

    # =================================================================
    # Janela
    # =================================================================

    def _configurar_janela(self) -> None:
        user = self._auth.current_user
        nome = user.nome_completo or user.username if user else ""
        papel = "👑 Admin" if (user and user.is_admin()) else "👤 Operador"
        self.title(f"{APP_TITLE}  —  {nome}  [{papel}]")
        self.geometry("1300x730")
        self.minsize(1000, 600)
        self.configure(fg_color=COLORS["secondary"])
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - 1300) // 2
        y = (self.winfo_screenheight() - 730)  // 2
        self.geometry(f"1300x730+{x}+{y}")
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # =================================================================
    # Sidebar
    # =================================================================

    def _construir_sidebar(self) -> None:
        self._sidebar = ctk.CTkFrame(self, width=230, corner_radius=0, fg_color=COLORS["sidebar"])
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)

        # Logo
        ctk.CTkLabel(self._sidebar, text="📦", font=("Segoe UI", 42)).pack(pady=(24, 4))
        ctk.CTkLabel(self._sidebar, text="InventárioIA",
                     font=FONTS["subtitle"], text_color=COLORS["primary"]).pack(pady=(0, 2))
        ctk.CTkLabel(self._sidebar, text=f"v{APP_VERSION}",
                     font=FONTS["small"], text_color=COLORS["text_secondary"]).pack(pady=(0, 12))

        # Separador
        ctk.CTkFrame(self._sidebar, height=1, fg_color=COLORS["primary"]).pack(fill="x", padx=20, pady=(0, 14))

        user = self._auth.current_user
        is_admin = user and user.is_admin()

        # ── Menu comum ──────────────────────────────────────────────
        itens_comuns = [
            ("🏠  Dashboard",    "dashboard"),
            ("📦  Produtos",     "produtos"),
            ("🛒  Vendas",       "vendas"),
            ("🤖  IA Previsão",  "ia"),
            ("📊  Relatórios",   "relatorios"),
        ]

        for texto, chave in itens_comuns:
            self._criar_botao_menu(texto, chave)

        # ── Secção Admin ────────────────────────────────────────────
        if is_admin:
            ctk.CTkFrame(self._sidebar, height=1,
                         fg_color=COLORS["sidebar_hover"]).pack(fill="x", padx=20, pady=(12, 8))
            ctk.CTkLabel(self._sidebar, text="  ADMINISTRAÇÃO",
                         font=("Segoe UI", 10, "bold"),
                         text_color=COLORS["warning"]).pack(anchor="w", padx=20, pady=(0, 6))

            itens_admin = [
                ("👥  Utilizadores",  "utilizadores"),
                ("⚙️  Admin Panel",   "admin_panel"),
            ]
            for texto, chave in itens_admin:
                self._criar_botao_menu(texto, chave, cor_hover="#2c1e0f")

        # Espaço flexível
        ctk.CTkFrame(self._sidebar, fg_color="transparent").pack(fill="y", expand=True)

        # ── Separador ───────────────────────────────────────────────
        ctk.CTkFrame(self._sidebar, height=1,
                     fg_color=COLORS["sidebar_hover"]).pack(fill="x", padx=20, pady=8)

        # ── Info do utilizador ──────────────────────────────────────
        frame_user = ctk.CTkFrame(self._sidebar, fg_color=COLORS["sidebar_hover"], corner_radius=10)
        frame_user.pack(fill="x", padx=12, pady=(0, 8))

        if user:
            papel_icone = "👑" if user.is_admin() else "👤"
            ctk.CTkLabel(frame_user,
                         text=f"{papel_icone}  {user.username}",
                         font=("Segoe UI", 12, "bold"),
                         text_color=COLORS["text_primary"]).pack(padx=12, pady=(8, 2), anchor="w")
            ctk.CTkLabel(frame_user,
                         text=user.nome_completo or "—",
                         font=FONTS["small"],
                         text_color=COLORS["text_secondary"]).pack(padx=12, pady=(0, 4), anchor="w")
            ctk.CTkLabel(frame_user,
                         text="Admin" if user.is_admin() else "Operador",
                         font=("Segoe UI", 10, "bold"),
                         text_color=COLORS["warning"] if user.is_admin() else COLORS["primary"],
                         ).pack(padx=12, pady=(0, 8), anchor="w")

        # ── Botão Perfil ────────────────────────────────────────────
        ctk.CTkButton(self._sidebar,
            text="👤  O Meu Perfil",
            width=206, height=36,
            font=FONTS["small"],
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            corner_radius=8,
            command=lambda: self._navegar("perfil"),
        ).pack(padx=12, pady=(0, 6))

        # ── Botão Logout (sempre visível e vermelho) ────────────────
        ctk.CTkButton(self._sidebar,
            text="⬅  Terminar Sessão",
            width=206, height=40,
            font=("Segoe UI", 13, "bold"),
            fg_color=COLORS["danger"],
            hover_color="#a71d2a",
            corner_radius=8,
            command=self._logout,
        ).pack(padx=12, pady=(0, 16))

    def _criar_botao_menu(self, texto: str, chave: str, cor_hover: str = None) -> None:
        """Cria e regista um botão do menu lateral."""
        btn = ctk.CTkButton(
            self._sidebar,
            text=texto,
            width=206, height=42,
            anchor="w",
            font=FONTS["body"],
            fg_color="transparent",
            hover_color=cor_hover or COLORS["sidebar_hover"],
            text_color=COLORS["text_primary"],
            corner_radius=8,
            command=lambda c=chave: self._navegar(c),
        )
        btn.pack(padx=12, pady=2)
        self._botoes_menu[chave] = btn

    # =================================================================
    # Área Principal
    # =================================================================

    def _construir_area_principal(self) -> None:
        self._area_principal = ctk.CTkFrame(self, corner_radius=0, fg_color=COLORS["secondary"])
        self._area_principal.pack(side="right", fill="both", expand=True)

        # Topbar
        self._topbar = ctk.CTkFrame(self._area_principal, height=56,
                                    corner_radius=0, fg_color=COLORS["card_bg"])
        self._topbar.pack(fill="x")
        self._topbar.pack_propagate(False)

        self._label_titulo_pagina = ctk.CTkLabel(
            self._topbar, text="Dashboard",
            font=FONTS["subtitle"], text_color=COLORS["text_primary"])
        self._label_titulo_pagina.pack(side="left", padx=24, pady=10)

        # Relógio
        self._label_hora = ctk.CTkLabel(
            self._topbar, text="",
            font=FONTS["small"], text_color=COLORS["text_secondary"])
        self._label_hora.pack(side="right", padx=20)
        self._actualizar_hora()

        # Botão logout na topbar (redundante mas conveniente)
        ctk.CTkButton(
            self._topbar,
            text="⬅ Logout",
            width=100, height=32,
            font=FONTS["small"],
            fg_color=COLORS["danger"],
            hover_color="#a71d2a",
            corner_radius=8,
            command=self._logout,
        ).pack(side="right", padx=(0, 8), pady=10)

        # Conteúdo
        self._frame_conteudo = ctk.CTkScrollableFrame(
            self._area_principal,
            fg_color=COLORS["secondary"], corner_radius=0)
        self._frame_conteudo.pack(fill="both", expand=True)

    def _actualizar_hora(self) -> None:
        hora = datetime.now().strftime("%d/%m/%Y  %H:%M:%S")
        self._label_hora.configure(text=hora)
        self.after(1000, self._actualizar_hora)

    # =================================================================
    # Navegação com controlo de acesso
    # =================================================================

    def _navegar(self, destino: str) -> None:
        """Navega para o módulo pedido com verificação de permissões."""
        user = self._auth.current_user
        is_admin = user and user.is_admin()

        # Páginas exclusivas de admin
        PAGINAS_ADMIN = {"utilizadores", "admin_panel"}
        if destino in PAGINAS_ADMIN and not is_admin:
            messagebox.showwarning(
                "Acesso Negado",
                "Esta funcionalidade é exclusiva de Administradores.",
                parent=self,
            )
            return

        # Actualiza estilo dos botões
        for chave, btn in self._botoes_menu.items():
            btn.configure(
                fg_color=COLORS["primary"] if chave == destino else "transparent",
                text_color=COLORS["text_primary"],
            )

        # Limpa conteúdo anterior
        for widget in self._frame_conteudo.winfo_children():
            widget.destroy()

        titulos = {
            "dashboard":    "🏠  Dashboard",
            "produtos":     "📦  Gestão de Produtos",
            "vendas":       "🛒  Registo de Vendas",
            "ia":           "🤖  IA — Previsão de Demanda",
            "relatorios":   "📊  Relatórios e Estatísticas",
            "utilizadores": "👥  Gestão de Utilizadores",
            "admin_panel":  "⚙️  Painel de Administração",
            "perfil":       "👤  O Meu Perfil",
        }
        self._label_titulo_pagina.configure(text=titulos.get(destino, destino.capitalize()))

        # Carrega a vista correcta
        if destino == "dashboard":
            from gui.dashboard_widgets import DashboardView
            DashboardView(self._frame_conteudo, self._produto_svc,
                          self._venda_svc, self._ia_svc).pack(fill="both", expand=True)

        elif destino == "produtos":
            from gui.produto_view import ProdutoView
            ProdutoView(self._frame_conteudo, self._produto_svc,
                        self._auth).pack(fill="both", expand=True)

        elif destino == "vendas":
            from gui.venda_view import VendaView
            VendaView(self._frame_conteudo, self._venda_svc,
                      self._produto_svc, self._auth).pack(fill="both", expand=True)

        elif destino == "ia":
            from gui.ia_view import IAView
            IAView(self._frame_conteudo, self._ia_svc,
                   self._venda_svc, self._produto_svc).pack(fill="both", expand=True)

        elif destino == "relatorios":
            from gui.relatorio_view import RelatorioView
            RelatorioView(self._frame_conteudo, self._produto_svc,
                          self._venda_svc, self._ia_svc).pack(fill="both", expand=True)

        elif destino == "utilizadores":
            from gui.usuario_view import UsuarioView
            UsuarioView(self._frame_conteudo, self._auth).pack(fill="both", expand=True)

        elif destino == "admin_panel":
            from gui.admin_panel import AdminPanel
            AdminPanel(self._frame_conteudo, self._auth,
                       self._produto_svc, self._venda_svc).pack(fill="both", expand=True)

        elif destino == "perfil":
            from gui.perfil_view import PerfilView
            PerfilView(self._frame_conteudo, self._auth).pack(fill="both", expand=True)

    # =================================================================
    # Logout
    # =================================================================

    def _logout(self) -> None:
        if messagebox.askyesno("Terminar Sessão",
                               "Tem a certeza que deseja terminar a sessão?",
                               parent=self):
            self._auth.logout()
            self.destroy()
            from main import iniciar_login
            iniciar_login()

    def _on_close(self) -> None:
        if messagebox.askyesno("Sair", "Fechar a aplicação?", parent=self):
            logger.info("Aplicação encerrada.")
            self.destroy()
