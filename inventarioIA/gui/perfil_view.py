"""
=============================================================================
Ficheiro: gui/perfil_view.py
Descrição: Painel de perfil do utilizador actual.
           Permite alterar nome completo e palavra-passe própria.
=============================================================================
"""

import logging
from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox

from services.auth_service import AuthService
from config.settings import COLORS, FONTS

logger = logging.getLogger(__name__)


class PerfilView(ctk.CTkFrame):
    """Módulo de perfil do utilizador autenticado."""

    def __init__(self, parent, auth_svc: AuthService) -> None:
        super().__init__(parent, fg_color="transparent")
        self._auth = auth_svc
        self._construir()

    def _construir(self) -> None:
        user = self._auth.current_user
        if not user:
            ctk.CTkLabel(self, text="Sem sessão activa.", font=FONTS["body"]).pack(pady=40)
            return

        # ---- Cabeçalho ----
        frame_header = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=12)
        frame_header.pack(fill="x", padx=20, pady=(20, 10))
        ctk.CTkLabel(frame_header, text="👤  O Meu Perfil",
                     font=FONTS["subtitle"]).pack(side="left", padx=20, pady=14)

        # ---- Layout 2 colunas ----
        frame_main = ctk.CTkFrame(self, fg_color="transparent")
        frame_main.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Coluna esquerda — info + editar perfil
        frame_esq = ctk.CTkFrame(frame_main, fg_color=COLORS["card_bg"], corner_radius=12)
        frame_esq.pack(side="left", fill="both", expand=True, padx=(0, 10))

        ctk.CTkLabel(frame_esq, text="📋  Informações da Conta",
                     font=FONTS["body"]).pack(padx=20, pady=(16, 8), anchor="w")

        info = [
            ("👤  Utilizador",   user.username),
            ("🏷  Nome Completo", user.nome_completo or "—"),
            ("🎭  Papel",         "👑 Administrador" if user.is_admin() else "👤 Operador"),
            ("📅  Membro desde",  user.criado_em.strftime("%d/%m/%Y") if user.criado_em else "—"),
            ("🕐  Último Login",  user.ultimo_login.strftime("%d/%m/%Y %H:%M") if user.ultimo_login else "Nunca"),
        ]

        for label, valor in info:
            f = ctk.CTkFrame(frame_esq, fg_color=COLORS["secondary"], corner_radius=8)
            f.pack(fill="x", padx=16, pady=3)
            ctk.CTkLabel(f, text=label, font=FONTS["small"],
                         text_color=COLORS["text_secondary"]).pack(side="left", padx=12, pady=10)
            ctk.CTkLabel(f, text=valor, font=("Segoe UI", 12, "bold"),
                         text_color=COLORS["text_primary"]).pack(side="right", padx=12)

        # Editar nome
        ctk.CTkLabel(frame_esq, text="Alterar Nome Completo",
                     font=FONTS["small"], text_color=COLORS["text_secondary"],
                     anchor="w").pack(fill="x", padx=16, pady=(16, 4))
        self._entry_nome = ctk.CTkEntry(
            frame_esq, height=40, font=FONTS["body"], corner_radius=8)
        self._entry_nome.insert(0, user.nome_completo or "")
        self._entry_nome.pack(fill="x", padx=16, pady=(0, 8))

        self._label_msg_nome = ctk.CTkLabel(frame_esq, text="", font=FONTS["small"],
                                            text_color=COLORS["success"])
        self._label_msg_nome.pack(padx=16)

        ctk.CTkButton(frame_esq, text="💾  Guardar Nome",
                      height=38, font=FONTS["body"],
                      fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
                      corner_radius=10, command=self._guardar_nome,
        ).pack(padx=16, pady=(4, 20), anchor="w")

        # Coluna direita — alterar password
        frame_dir = ctk.CTkFrame(frame_main, fg_color=COLORS["card_bg"],
                                 corner_radius=12, width=340)
        frame_dir.pack(side="right", fill="y")
        frame_dir.pack_propagate(False)

        ctk.CTkLabel(frame_dir, text="🔑  Alterar Palavra-passe",
                     font=FONTS["body"]).pack(padx=20, pady=(16, 8), anchor="w")

        def campo_pass(label, placeholder):
            ctk.CTkLabel(frame_dir, text=label, font=FONTS["small"],
                         text_color=COLORS["text_secondary"], anchor="w"
                         ).pack(fill="x", padx=16, pady=(8, 2))
            e = ctk.CTkEntry(frame_dir, placeholder_text=placeholder,
                             height=40, show="•", font=FONTS["body"], corner_radius=8)
            e.pack(fill="x", padx=16, pady=(0, 4))
            return e

        self._entry_pass_atual  = campo_pass("Password Actual *",  "introduza a password actual")
        self._entry_pass_nova   = campo_pass("Nova Password *",     "mínimo 6 caracteres")
        self._entry_pass_conf   = campo_pass("Confirmar Password *","repita a nova password")

        self._label_msg_pass = ctk.CTkLabel(frame_dir, text="", font=FONTS["small"],
                                            text_color=COLORS["danger"], wraplength=280)
        self._label_msg_pass.pack(padx=16, pady=6)

        ctk.CTkButton(frame_dir, text="🔑  Alterar Password",
                      height=42, font=FONTS["button"],
                      fg_color=COLORS["warning"], hover_color="#d39e00",
                      corner_radius=10, command=self._alterar_password,
        ).pack(fill="x", padx=16, pady=(0, 20))

        # Info de sessão
        frame_sessao = ctk.CTkFrame(frame_dir, fg_color=COLORS["secondary"], corner_radius=8)
        frame_sessao.pack(fill="x", padx=16, pady=(0, 16))
        info_sessao = self._auth.get_session_info()
        ctk.CTkLabel(frame_sessao,
                     text=f"🕐  Sessão iniciada: {info_sessao.get('session_start', '—')}  |  "
                          f"Duração: {info_sessao.get('session_duration_min', 0)} min",
                     font=FONTS["small"], text_color=COLORS["text_secondary"],
        ).pack(padx=12, pady=8)

    def _guardar_nome(self) -> None:
        user = self._auth.current_user
        if not user:
            return
        novo_nome = self._entry_nome.get().strip()
        user.nome_completo = novo_nome
        user.save()
        self._label_msg_nome.configure(text="✓  Nome actualizado com sucesso!")
        self.after(3000, lambda: self._label_msg_nome.configure(text=""))

    def _alterar_password(self) -> None:
        user = self._auth.current_user
        if not user:
            return
        atual = self._entry_pass_atual.get()
        nova  = self._entry_pass_nova.get()
        conf  = self._entry_pass_conf.get()

        if not user.verificar_password(atual):
            self._label_msg_pass.configure(text="⚠  Password actual incorrecta.", text_color=COLORS["danger"])
            return
        if len(nova) < 6:
            self._label_msg_pass.configure(text="⚠  Nova password: mínimo 6 caracteres.", text_color=COLORS["danger"])
            return
        if nova != conf:
            self._label_msg_pass.configure(text="⚠  As passwords não coincidem.", text_color=COLORS["danger"])
            return

        user.alterar_password(nova)
        for e in (self._entry_pass_atual, self._entry_pass_nova, self._entry_pass_conf):
            e.delete(0, "end")
        self._label_msg_pass.configure(text="✓  Password alterada com sucesso!", text_color=COLORS["success"])
        self.after(3000, lambda: self._label_msg_pass.configure(text=""))
        messagebox.showinfo("Sucesso", "Password alterada!\nUse a nova password no próximo login.", parent=self)
