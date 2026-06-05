"""
=============================================================================
Ficheiro: gui/usuario_view.py
Descrição: Painel de gestão de utilizadores — exclusivo para administradores.
           Permite criar, editar, bloquear/desbloquear e eliminar utilizadores.
=============================================================================
"""

import logging
import customtkinter as ctk
from tkinter import ttk, messagebox
from typing import Optional

from services.auth_service import AuthService
from models.usuario import Usuario
from exceptions.auth_exception import (
    UserAlreadyExistsException,
    InsufficientPermissionsException,
)
from config.settings import COLORS, FONTS

logger = logging.getLogger(__name__)


class UsuarioView(ctk.CTkFrame):
    """
    Módulo de gestão de utilizadores (apenas Admin).

    Funcionalidades:
      - Listar todos os utilizadores com estado e papel.
      - Criar novo utilizador (admin ou operador).
      - Editar nome completo, papel e estado.
      - Resetar palavra-passe.
      - Bloquear / Desbloquear conta.
      - Eliminar utilizador (excepto o próprio admin).
    """

    def __init__(self, parent, auth_svc: AuthService) -> None:
        super().__init__(parent, fg_color="transparent")
        self._auth = auth_svc
        self._construir()
        self._carregar_utilizadores()

    # =================================================================
    # Construção
    # =================================================================

    def _construir(self) -> None:
        # ---- Cabeçalho ----
        frame_header = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=12)
        frame_header.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            frame_header, text="👥  Gestão de Utilizadores",
            font=FONTS["subtitle"],
        ).pack(side="left", padx=20, pady=14)

        # Botões de acção
        frame_btns = ctk.CTkFrame(frame_header, fg_color="transparent")
        frame_btns.pack(side="right", padx=16, pady=10)

        ctk.CTkButton(
            frame_btns, text="➕  Novo Utilizador",
            height=38, font=FONTS["body"],
            fg_color=COLORS["success"], hover_color="#1e7e34",
            corner_radius=10, command=self._abrir_form_criar,
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            frame_btns, text="✏️  Editar",
            height=38, font=FONTS["body"],
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            corner_radius=10, command=self._editar_selecionado,
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            frame_btns, text="🔑  Reset Password",
            height=38, font=FONTS["body"],
            fg_color=COLORS["warning"], hover_color="#d39e00",
            corner_radius=10, command=self._reset_password,
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            frame_btns, text="🔄  Actualizar",
            height=38, font=FONTS["small"],
            fg_color=COLORS["secondary"], hover_color="#3a3a3a",
            corner_radius=10, command=self._carregar_utilizadores,
        ).pack(side="left", padx=4)

        # ---- Tabela ----
        frame_tabela = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=12)
        frame_tabela.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        style = ttk.Style()
        style.configure("User.Treeview",
            background=COLORS["secondary"], foreground="white",
            rowheight=38, fieldbackground=COLORS["secondary"],
            font=("Segoe UI", 12))
        style.configure("User.Treeview.Heading",
            background=COLORS["sidebar"], foreground=COLORS["primary"],
            font=("Segoe UI", 12, "bold"))
        style.map("User.Treeview", background=[("selected", COLORS["primary"])])

        colunas = ("username", "nome", "papel", "estado", "tentativas", "ultimo_login", "criado_em")
        frame_inner = ctk.CTkFrame(frame_tabela, fg_color="transparent")
        frame_inner.pack(fill="both", expand=True, padx=12, pady=12)

        self._tabela = ttk.Treeview(
            frame_inner, columns=colunas,
            show="headings", style="User.Treeview")

        self._tabela.heading("username",     text="Utilizador",     anchor="w")
        self._tabela.heading("nome",         text="Nome Completo",  anchor="w")
        self._tabela.heading("papel",        text="Papel",          anchor="center")
        self._tabela.heading("estado",       text="Estado",         anchor="center")
        self._tabela.heading("tentativas",   text="Tentativas",     anchor="center")
        self._tabela.heading("ultimo_login", text="Último Login",   anchor="w")
        self._tabela.heading("criado_em",    text="Criado Em",      anchor="w")

        self._tabela.column("username",     width=130, anchor="w")
        self._tabela.column("nome",         width=200, anchor="w")
        self._tabela.column("papel",        width=100, anchor="center")
        self._tabela.column("estado",       width=100, anchor="center")
        self._tabela.column("tentativas",   width=90,  anchor="center")
        self._tabela.column("ultimo_login", width=150, anchor="w")
        self._tabela.column("criado_em",    width=120, anchor="w")

        self._tabela.tag_configure("admin",     foreground="#9b59b6")
        self._tabela.tag_configure("bloqueado", foreground=COLORS["danger"])
        self._tabela.tag_configure("inactivo",  foreground="#7f8c8d")

        sb = ttk.Scrollbar(frame_inner, orient="vertical", command=self._tabela.yview)
        self._tabela.configure(yscrollcommand=sb.set)
        self._tabela.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # Menu de contexto (botão direito)
        self._menu_contexto = ctk.CTkFrame(self, fg_color="transparent")
        self._tabela.bind("<Button-3>", self._mostrar_menu_contexto)
        self._tabela.bind("<Double-1>", lambda e: self._editar_selecionado())

        # Painel de acções rápidas na parte inferior
        frame_acoes = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=12)
        frame_acoes.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkLabel(frame_acoes, text="Acções rápidas:",
                     font=FONTS["small"], text_color=COLORS["text_secondary"],
        ).pack(side="left", padx=16, pady=10)

        ctk.CTkButton(
            frame_acoes, text="✅  Activar Conta",
            height=34, font=FONTS["small"], width=140,
            fg_color=COLORS["success"], hover_color="#1e7e34",
            corner_radius=8, command=self._activar_conta,
        ).pack(side="left", padx=4, pady=8)

        ctk.CTkButton(
            frame_acoes, text="🔒  Bloquear Conta",
            height=34, font=FONTS["small"], width=140,
            fg_color=COLORS["warning"], hover_color="#d39e00",
            corner_radius=8, command=self._bloquear_conta,
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            frame_acoes, text="🔓  Desbloquear",
            height=34, font=FONTS["small"], width=130,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            corner_radius=8, command=self._desbloquear_conta,
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            frame_acoes, text="🗑  Eliminar",
            height=34, font=FONTS["small"], width=110,
            fg_color=COLORS["danger"], hover_color="#a71d2a",
            corner_radius=8, command=self._eliminar_utilizador,
        ).pack(side="left", padx=4)

        self._label_contador = ctk.CTkLabel(
            frame_acoes, text="",
            font=FONTS["small"], text_color=COLORS["text_secondary"],
        )
        self._label_contador.pack(side="right", padx=16)

    # =================================================================
    # Dados
    # =================================================================

    def _carregar_utilizadores(self) -> None:
        """Carrega todos os utilizadores na tabela."""
        for item in self._tabela.get_children():
            self._tabela.delete(item)
        try:
            utilizadores = list(Usuario.objects().order_by("username"))
            current_user = self._auth.current_user

            for u in utilizadores:
                bloqueado = u.is_bloqueado()
                estado = (
                    "🔒 Bloqueado" if bloqueado
                    else ("✅ Activo" if u.ativo else "❌ Inactivo")
                )
                tag = (
                    "bloqueado" if bloqueado
                    else ("admin" if u.role == "admin" else "normal")
                )
                # Marca o utilizador actual
                nome_display = u.username
                if current_user and u.username == current_user.username:
                    nome_display = f"➤ {u.username} (você)"

                self._tabela.insert("", "end", iid=str(u.id), values=(
                    nome_display,
                    u.nome_completo or "—",
                    "👑 Admin" if u.role == "admin" else "👤 Operador",
                    estado,
                    u.tentativas_login,
                    u.ultimo_login.strftime("%d/%m/%Y %H:%M") if u.ultimo_login else "Nunca",
                    u.criado_em.strftime("%d/%m/%Y") if u.criado_em else "—",
                ), tags=(tag,))

            self._label_contador.configure(
                text=f"Total: {len(utilizadores)} utilizador(es)"
            )
        except Exception as e:
            logger.error(f"Erro ao carregar utilizadores: {e}")
            messagebox.showerror("Erro", str(e), parent=self)

    def _obter_utilizador_selecionado(self) -> Optional[Usuario]:
        """Devolve o utilizador seleccionado na tabela."""
        sel = self._tabela.selection()
        if not sel:
            return None
        try:
            return Usuario.objects(id=sel[0]).first()
        except Exception:
            return None

    # =================================================================
    # Operações CRUD
    # =================================================================

    def _abrir_form_criar(self) -> None:
        FormularioUtilizador(
            parent=self.winfo_toplevel(),
            auth_svc=self._auth,
            utilizador=None,
            on_guardar=self._carregar_utilizadores,
        )

    def _editar_selecionado(self) -> None:
        u = self._obter_utilizador_selecionado()
        if not u:
            messagebox.showinfo("Seleccionar", "Seleccione um utilizador.", parent=self)
            return
        FormularioUtilizador(
            parent=self.winfo_toplevel(),
            auth_svc=self._auth,
            utilizador=u,
            on_guardar=self._carregar_utilizadores,
        )

    def _reset_password(self) -> None:
        """Diálogo para redefinir a palavra-passe de um utilizador."""
        u = self._obter_utilizador_selecionado()
        if not u:
            messagebox.showinfo("Seleccionar", "Seleccione um utilizador.", parent=self)
            return
        current = self._auth.current_user
        if current and u.username == current.username:
            messagebox.showwarning(
                "Aviso", "Para alterar a sua própria password use o perfil.", parent=self
            )
            return
        DialogoResetPassword(
            parent=self.winfo_toplevel(),
            utilizador=u,
            on_reset=self._carregar_utilizadores,
        )

    def _activar_conta(self) -> None:
        u = self._obter_utilizador_selecionado()
        if not u:
            messagebox.showinfo("Seleccionar", "Seleccione um utilizador.", parent=self)
            return
        u.ativo = True
        u.tentativas_login = 0
        u.save()
        messagebox.showinfo("Sucesso", f"Conta '{u.username}' activada.", parent=self)
        self._carregar_utilizadores()

    def _bloquear_conta(self) -> None:
        u = self._obter_utilizador_selecionado()
        if not u:
            messagebox.showinfo("Seleccionar", "Seleccione um utilizador.", parent=self)
            return
        current = self._auth.current_user
        if current and u.username == current.username:
            messagebox.showwarning("Aviso", "Não pode bloquear a sua própria conta.", parent=self)
            return
        from config.settings import MAX_LOGIN_ATTEMPTS
        u.tentativas_login = MAX_LOGIN_ATTEMPTS
        u.save()
        messagebox.showinfo("Bloqueado", f"Conta '{u.username}' bloqueada.", parent=self)
        self._carregar_utilizadores()

    def _desbloquear_conta(self) -> None:
        u = self._obter_utilizador_selecionado()
        if not u:
            messagebox.showinfo("Seleccionar", "Seleccione um utilizador.", parent=self)
            return
        u.desbloquear()
        u.ativo = True
        u.save()
        messagebox.showinfo("Desbloqueado", f"Conta '{u.username}' desbloqueada.", parent=self)
        self._carregar_utilizadores()

    def _eliminar_utilizador(self) -> None:
        u = self._obter_utilizador_selecionado()
        if not u:
            messagebox.showinfo("Seleccionar", "Seleccione um utilizador.", parent=self)
            return
        current = self._auth.current_user
        if current and u.username == current.username:
            messagebox.showwarning("Aviso", "Não pode eliminar a sua própria conta.", parent=self)
            return
        if u.role == "admin":
            total_admins = Usuario.objects(role="admin", ativo=True).count()
            if total_admins <= 1:
                messagebox.showerror(
                    "Erro",
                    "Não é possível eliminar o único administrador do sistema.",
                    parent=self,
                )
                return
        conf = messagebox.askyesno(
            "Confirmar",
            f"Eliminar definitivamente o utilizador '{u.username}'?\n\nEsta acção não pode ser desfeita.",
            icon="warning", parent=self,
        )
        if conf:
            u.delete()
            messagebox.showinfo("Eliminado", f"Utilizador '{u.username}' eliminado.", parent=self)
            self._carregar_utilizadores()

    def _mostrar_menu_contexto(self, event) -> None:
        """Selecciona a linha ao clicar com o botão direito."""
        item = self._tabela.identify_row(event.y)
        if item:
            self._tabela.selection_set(item)


# =============================================================================
# Formulário de Utilizador
# =============================================================================

class FormularioUtilizador(ctk.CTkToplevel):
    """Diálogo para criar ou editar utilizador."""

    def __init__(self, parent, auth_svc: AuthService,
                 utilizador: Optional[Usuario], on_guardar) -> None:
        super().__init__(parent)
        self._auth = auth_svc
        self._utilizador = utilizador
        self._on_guardar = on_guardar
        self._modo = "Editar" if utilizador else "Criar"

        self.title(f"{self._modo} Utilizador")
        self.geometry("480x500")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["secondary"])
        self.grab_set()
        self.focus_set()

        # Centraliza
        self.update_idletasks()
        px = parent.winfo_x() + (parent.winfo_width() - 480) // 2
        py = parent.winfo_y() + (parent.winfo_height() - 500) // 2
        self.geometry(f"480x500+{px}+{py}")
        self._construir()
        if utilizador:
            self._preencher(utilizador)

    def _criar_campo(self, parent, label, placeholder, show="") -> ctk.CTkEntry:
        ctk.CTkLabel(parent, text=label, font=FONTS["small"],
                     text_color=COLORS["text_secondary"], anchor="w").pack(fill="x", pady=(10, 2))
        entry = ctk.CTkEntry(parent, placeholder_text=placeholder,
                             height=40, font=FONTS["body"], corner_radius=8, show=show)
        entry.pack(fill="x", pady=(0, 4))
        return entry

    def _construir(self) -> None:
        # Cabeçalho
        frame_h = ctk.CTkFrame(self, fg_color=COLORS["primary"], corner_radius=0)
        frame_h.pack(fill="x")
        ctk.CTkLabel(frame_h,
            text=f"{'➕' if self._modo == 'Criar' else '✏️'}  {self._modo} Utilizador",
            font=FONTS["subtitle"], text_color="white").pack(padx=24, pady=14)

        frame_form = ctk.CTkScrollableFrame(self, fg_color="transparent")
        frame_form.pack(fill="both", expand=True, padx=24, pady=16)

        self._entry_username  = self._criar_campo(frame_form, "Nome de Utilizador *", "ex: joao.silva")
        self._entry_nome      = self._criar_campo(frame_form, "Nome Completo",        "ex: João Silva")

        # Papel
        ctk.CTkLabel(frame_form, text="Papel *", font=FONTS["small"],
                     text_color=COLORS["text_secondary"], anchor="w").pack(fill="x", pady=(10, 2))
        self._combo_role = ctk.CTkComboBox(
            frame_form, values=["operador", "admin"],
            height=40, font=FONTS["body"], corner_radius=8)
        self._combo_role.set("operador")
        self._combo_role.pack(fill="x", pady=(0, 4))

        # Password (só no modo criar)
        if self._modo == "Criar":
            self._entry_pass  = self._criar_campo(frame_form, "Palavra-passe *", "mínimo 6 caracteres", show="•")
            self._entry_pass2 = self._criar_campo(frame_form, "Confirmar Palavra-passe *", "repita a password", show="•")

        # Estado (só no modo editar)
        if self._modo == "Editar":
            ctk.CTkLabel(frame_form, text="Estado", font=FONTS["small"],
                         text_color=COLORS["text_secondary"], anchor="w").pack(fill="x", pady=(10, 2))
            self._combo_estado = ctk.CTkComboBox(
                frame_form, values=["activo", "inactivo"],
                height=40, font=FONTS["body"], corner_radius=8)
            self._combo_estado.set("activo")
            self._combo_estado.pack(fill="x", pady=(0, 4))

        self._label_msg = ctk.CTkLabel(frame_form, text="", font=FONTS["small"],
                                       text_color=COLORS["danger"], wraplength=400)
        self._label_msg.pack(pady=6)

        # Botões
        frame_btns = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=0)
        frame_btns.pack(fill="x", side="bottom")

        ctk.CTkButton(frame_btns, text="Cancelar", height=42,
            fg_color=COLORS["secondary"], hover_color="#3a3a3a",
            font=FONTS["body"], corner_radius=10,
            command=self.destroy).pack(side="left", padx=(16, 8), pady=12)

        ctk.CTkButton(frame_btns,
            text=f"💾  {'Criar' if self._modo == 'Criar' else 'Guardar'} Utilizador",
            height=42, font=FONTS["button"],
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            corner_radius=10, command=self._guardar).pack(side="right", padx=(8, 16), pady=12)

    def _preencher(self, u: Usuario) -> None:
        self._entry_username.insert(0, u.username)
        self._entry_username.configure(state="disabled")
        self._entry_nome.insert(0, u.nome_completo or "")
        self._combo_role.set(u.role)
        if hasattr(self, "_combo_estado"):
            self._combo_estado.set("activo" if u.ativo else "inactivo")

    def _guardar(self) -> None:
        username = self._entry_username.get().strip()
        nome     = self._entry_nome.get().strip()
        role     = self._combo_role.get()

        if not username:
            self._label_msg.configure(text="⚠  Username é obrigatório.")
            return

        try:
            if self._modo == "Criar":
                password  = self._entry_pass.get()
                password2 = self._entry_pass2.get()
                if len(password) < 6:
                    self._label_msg.configure(text="⚠  Password deve ter pelo menos 6 caracteres.")
                    return
                if password != password2:
                    self._label_msg.configure(text="⚠  As passwords não coincidem.")
                    return
                self._auth.criar_utilizador(username, password, role=role, nome_completo=nome)
                messagebox.showinfo("Sucesso", f"Utilizador '{username}' criado!", parent=self)
            else:
                self._utilizador.nome_completo = nome
                self._utilizador.role = role
                if hasattr(self, "_combo_estado"):
                    self._utilizador.ativo = (self._combo_estado.get() == "activo")
                self._utilizador.save()
                messagebox.showinfo("Sucesso", f"Utilizador '{username}' actualizado!", parent=self)

            self._on_guardar()
            self.destroy()

        except UserAlreadyExistsException as e:
            self._label_msg.configure(text=f"⚠  {e.message}")
        except Exception as e:
            self._label_msg.configure(text=f"⚠  Erro: {e}")


# =============================================================================
# Diálogo de Reset de Password
# =============================================================================

class DialogoResetPassword(ctk.CTkToplevel):
    """Diálogo para redefinir a palavra-passe de um utilizador."""

    def __init__(self, parent, utilizador: Usuario, on_reset) -> None:
        super().__init__(parent)
        self._utilizador = utilizador
        self._on_reset = on_reset

        self.title("🔑  Redefinir Palavra-passe")
        self.geometry("420x320")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["secondary"])
        self.grab_set()
        self.focus_set()

        self.update_idletasks()
        px = parent.winfo_x() + (parent.winfo_width() - 420) // 2
        py = parent.winfo_y() + (parent.winfo_height() - 320) // 2
        self.geometry(f"420x320+{px}+{py}")
        self._construir()

    def _construir(self) -> None:
        frame_h = ctk.CTkFrame(self, fg_color=COLORS["warning"], corner_radius=0)
        frame_h.pack(fill="x")
        ctk.CTkLabel(frame_h, text=f"🔑  Reset Password — {self._utilizador.username}",
                     font=FONTS["body"], text_color="white").pack(padx=20, pady=12)

        frame_form = ctk.CTkFrame(self, fg_color="transparent")
        frame_form.pack(fill="both", expand=True, padx=24, pady=16)

        ctk.CTkLabel(frame_form, text="Nova Palavra-passe *", font=FONTS["small"],
                     text_color=COLORS["text_secondary"], anchor="w").pack(fill="x", pady=(0, 2))
        self._entry_pass = ctk.CTkEntry(frame_form, placeholder_text="mínimo 6 caracteres",
                                        height=40, show="•", font=FONTS["body"], corner_radius=8)
        self._entry_pass.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(frame_form, text="Confirmar Palavra-passe *", font=FONTS["small"],
                     text_color=COLORS["text_secondary"], anchor="w").pack(fill="x", pady=(0, 2))
        self._entry_pass2 = ctk.CTkEntry(frame_form, placeholder_text="repita a password",
                                         height=40, show="•", font=FONTS["body"], corner_radius=8)
        self._entry_pass2.pack(fill="x")

        self._label_msg = ctk.CTkLabel(frame_form, text="", font=FONTS["small"],
                                       text_color=COLORS["danger"])
        self._label_msg.pack(pady=8)

        frame_btns = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=0)
        frame_btns.pack(fill="x", side="bottom")
        ctk.CTkButton(frame_btns, text="Cancelar", height=40,
                      fg_color=COLORS["secondary"], hover_color="#3a3a3a",
                      font=FONTS["body"], corner_radius=10,
                      command=self.destroy).pack(side="left", padx=(16, 8), pady=12)
        ctk.CTkButton(frame_btns, text="🔑  Redefinir Password", height=40,
                      fg_color=COLORS["warning"], hover_color="#d39e00",
                      font=FONTS["button"], corner_radius=10,
                      command=self._guardar).pack(side="right", padx=(8, 16), pady=12)

    def _guardar(self) -> None:
        p1 = self._entry_pass.get()
        p2 = self._entry_pass2.get()
        if len(p1) < 6:
            self._label_msg.configure(text="⚠  Mínimo 6 caracteres.")
            return
        if p1 != p2:
            self._label_msg.configure(text="⚠  As passwords não coincidem.")
            return
        self._utilizador.alterar_password(p1)
        self._utilizador.tentativas_login = 0
        self._utilizador.save()
        messagebox.showinfo("Sucesso",
            f"Password de '{self._utilizador.username}' redefinida com sucesso!\n"
            "O utilizador pode fazer login com a nova password.", parent=self)
        self._on_reset()
        self.destroy()
