"""
=============================================================================
Ficheiro: gui/venda_view.py
Descrição: Interface gráfica para registo de vendas e consulta de histórico.
=============================================================================
"""

import logging
import customtkinter as ctk
from tkinter import ttk, messagebox
from typing import Optional

from services.venda_service import VendaService
from services.produto_service import ProdutoService
from services.auth_service import AuthService
from exceptions.stock_exception import (
    InsufficientStockException,
    ProductNotFoundException,
)
from config.settings import COLORS, FONTS

logger = logging.getLogger(__name__)


class VendaView(ctk.CTkFrame):
    """
    Módulo de registo de vendas e consulta de histórico.

    Funcionalidades:
      - Formulário de registo de venda (produto + quantidade).
      - Actualização automática do stock após venda.
      - Histórico de vendas em tabela filtrada por data.
      - Totais e estatísticas do período.
    """

    def __init__(
        self,
        parent,
        venda_svc: VendaService,
        produto_svc: ProdutoService,
        auth_svc: AuthService,
    ) -> None:
        super().__init__(parent, fg_color="transparent")
        self._venda_svc = venda_svc
        self._produto_svc = produto_svc
        self._auth_svc = auth_svc
        self._lista_produtos = []
        self._construir()
        self._carregar_historico()

    # =================================================================
    # Construção
    # =================================================================

    def _construir(self) -> None:
        """Constrói a interface de vendas."""
        # Layout de duas colunas
        frame_esq = ctk.CTkFrame(self, fg_color="transparent", width=360)
        frame_esq.pack(side="left", fill="y", padx=(20, 10), pady=20)
        frame_esq.pack_propagate(False)

        frame_dir = ctk.CTkFrame(self, fg_color="transparent")
        frame_dir.pack(side="right", fill="both", expand=True, padx=(10, 20), pady=20)

        self._construir_formulario(frame_esq)
        self._construir_historico(frame_dir)

    def _construir_formulario(self, parent) -> None:
        """Constrói o formulário de registo de venda."""
        frame = ctk.CTkFrame(parent, fg_color=COLORS["card_bg"], corner_radius=14)
        frame.pack(fill="both", expand=True)

        ctk.CTkLabel(
            frame, text="🛒  Nova Venda",
            font=FONTS["subtitle"], text_color=COLORS["text_primary"]
        ).pack(padx=20, pady=(20, 4), anchor="w")

        ctk.CTkLabel(
            frame, text="Registe a venda e o stock é actualizado automaticamente.",
            font=FONTS["small"], text_color=COLORS["text_secondary"],
            wraplength=300
        ).pack(padx=20, pady=(0, 16), anchor="w")

        # ---- Produto ----
        ctk.CTkLabel(
            frame, text="Produto *", font=FONTS["small"],
            text_color=COLORS["text_secondary"]
        ).pack(padx=20, anchor="w")

        self._lista_produtos = self._produto_svc.obter_todos()
        nomes_produtos = [p.nome for p in self._lista_produtos]

        self._combo_produto = ctk.CTkComboBox(
            frame,
            values=nomes_produtos if nomes_produtos else ["Sem produtos"],
            height=42,
            font=FONTS["body"],
            corner_radius=8,
            command=self._ao_seleccionar_produto,
        )
        self._combo_produto.pack(fill="x", padx=20, pady=(4, 0))

        # Info do produto seleccionado
        self._frame_info_produto = ctk.CTkFrame(
            frame, fg_color=COLORS["secondary"], corner_radius=8
        )
        self._frame_info_produto.pack(fill="x", padx=20, pady=(8, 12))

        self._label_info_produto = ctk.CTkLabel(
            self._frame_info_produto,
            text="Seleccione um produto para ver detalhes.",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"],
            wraplength=280,
        )
        self._label_info_produto.pack(padx=14, pady=10)

        # ---- Quantidade ----
        ctk.CTkLabel(
            frame, text="Quantidade *", font=FONTS["small"],
            text_color=COLORS["text_secondary"]
        ).pack(padx=20, anchor="w")

        frame_qtd = ctk.CTkFrame(frame, fg_color="transparent")
        frame_qtd.pack(fill="x", padx=20, pady=(4, 14))

        ctk.CTkButton(
            frame_qtd, text="−", width=42, height=42,
            font=("Segoe UI", 18, "bold"),
            fg_color=COLORS["secondary"],
            hover_color=COLORS["danger"],
            corner_radius=8,
            command=lambda: self._ajustar_quantidade(-1)
        ).pack(side="left")

        self._entry_qtd = ctk.CTkEntry(
            frame_qtd, width=100, height=42,
            font=("Segoe UI", 16, "bold"),
            justify="center", corner_radius=8
        )
        self._entry_qtd.insert(0, "1")
        self._entry_qtd.pack(side="left", padx=6)

        ctk.CTkButton(
            frame_qtd, text="+", width=42, height=42,
            font=("Segoe UI", 18, "bold"),
            fg_color=COLORS["secondary"],
            hover_color=COLORS["success"],
            corner_radius=8,
            command=lambda: self._ajustar_quantidade(1)
        ).pack(side="left")

        # ---- Observações ----
        ctk.CTkLabel(
            frame, text="Observações (opcional)", font=FONTS["small"],
            text_color=COLORS["text_secondary"]
        ).pack(padx=20, anchor="w")

        self._entry_obs = ctk.CTkTextbox(
            frame, height=60, font=FONTS["body"], corner_radius=8
        )
        self._entry_obs.pack(fill="x", padx=20, pady=(4, 16))

        # ---- Mensagem de Feedback ----
        self._label_msg = ctk.CTkLabel(
            frame, text="", font=FONTS["small"],
            text_color=COLORS["danger"], wraplength=300
        )
        self._label_msg.pack(pady=4)

        # ---- Botão Registar ----
        ctk.CTkButton(
            frame,
            text="✓  Registar Venda",
            height=48,
            font=FONTS["button"],
            fg_color=COLORS["success"],
            hover_color="#1e7e34",
            corner_radius=12,
            command=self._registrar_venda,
        ).pack(fill="x", padx=20, pady=(0, 20))

        # Selecciona o primeiro produto se existir
        if nomes_produtos:
            self._combo_produto.set(nomes_produtos[0])
            self._ao_seleccionar_produto(nomes_produtos[0])

    def _construir_historico(self, parent) -> None:
        """Constrói a tabela de histórico de vendas."""
        # Cabeçalho
        frame_header = ctk.CTkFrame(
            parent, fg_color=COLORS["card_bg"], corner_radius=12
        )
        frame_header.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            frame_header, text="📋  Histórico de Vendas",
            font=FONTS["subtitle"]
        ).pack(side="left", padx=20, pady=14)

        ctk.CTkButton(
            frame_header, text="🔄 Actualizar", width=130, height=36,
            font=FONTS["small"],
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            corner_radius=8,
            command=self._carregar_historico,
        ).pack(side="right", padx=16, pady=12)

        # Estatísticas rápidas
        frame_stats = ctk.CTkFrame(
            parent, fg_color=COLORS["card_bg"], corner_radius=12
        )
        frame_stats.pack(fill="x", pady=(0, 10))
        self._frame_stats = frame_stats
        self._construir_stats()

        # Tabela
        frame_tabela = ctk.CTkFrame(
            parent, fg_color=COLORS["card_bg"], corner_radius=12
        )
        frame_tabela.pack(fill="both", expand=True)

        style = ttk.Style()
        style.configure(
            "Venda.Treeview",
            background=COLORS["secondary"],
            foreground="white",
            rowheight=32,
            fieldbackground=COLORS["secondary"],
            font=("Segoe UI", 11),
        )
        style.configure(
            "Venda.Treeview.Heading",
            background=COLORS["sidebar"],
            foreground=COLORS["primary"],
            font=("Segoe UI", 11, "bold"),
        )
        style.map("Venda.Treeview", background=[("selected", COLORS["primary"])])

        colunas = ("data", "produto", "quantidade", "preco_unit", "total", "operador")
        frame_inner = ctk.CTkFrame(frame_tabela, fg_color="transparent")
        frame_inner.pack(fill="both", expand=True, padx=12, pady=12)

        self._tabela = ttk.Treeview(
            frame_inner, columns=colunas, show="headings",
            style="Venda.Treeview"
        )
        self._tabela.heading("data",       text="Data/Hora",    anchor="w")
        self._tabela.heading("produto",    text="Produto",      anchor="w")
        self._tabela.heading("quantidade", text="Qtd",          anchor="center")
        self._tabela.heading("preco_unit", text="Preço Unit.",  anchor="e")
        self._tabela.heading("total",      text="Total (AOA)",  anchor="e")
        self._tabela.heading("operador",   text="Operador",     anchor="w")

        self._tabela.column("data",        width=140, anchor="w")
        self._tabela.column("produto",     width=200, anchor="w")
        self._tabela.column("quantidade",  width=60,  anchor="center")
        self._tabela.column("preco_unit",  width=110, anchor="e")
        self._tabela.column("total",       width=120, anchor="e")
        self._tabela.column("operador",    width=100, anchor="w")

        sb = ttk.Scrollbar(frame_inner, orient="vertical", command=self._tabela.yview)
        self._tabela.configure(yscrollcommand=sb.set)
        self._tabela.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    def _construir_stats(self) -> None:
        """Constrói o painel de estatísticas de vendas."""
        for w in self._frame_stats.winfo_children():
            w.destroy()

        try:
            stats = self._venda_svc.obter_estatisticas_gerais()
        except Exception:
            stats = {}

        itens = [
            ("Total Vendas", str(stats.get("total_vendas", 0)), COLORS["primary"]),
            ("Hoje",         str(stats.get("vendas_hoje", 0)),  COLORS["success"]),
            ("Este Mês",     str(stats.get("vendas_mes", 0)),   COLORS["warning"]),
            ("Receita Total",f"{stats.get('receita_total', 0):,.2f}", "#9b59b6"),
        ]

        for titulo, valor, cor in itens:
            f = ctk.CTkFrame(self._frame_stats, fg_color="transparent")
            f.pack(side="left", expand=True, padx=14, pady=12)
            ctk.CTkLabel(f, text=titulo, font=FONTS["small"],
                         text_color=COLORS["text_secondary"]).pack()
            ctk.CTkLabel(f, text=valor, font=("Segoe UI", 20, "bold"),
                         text_color=cor).pack()

    # =================================================================
    # Lógica
    # =================================================================

    def _ao_seleccionar_produto(self, nome: str) -> None:
        """Actualiza as informações do produto seleccionado."""
        produto = next((p for p in self._lista_produtos if p.nome == nome), None)
        if not produto:
            self._label_info_produto.configure(text="Produto não encontrado.")
            return

        cor = COLORS["warning"] if produto.tem_stock_baixo else COLORS["success"]
        info = (
            f"  Categoria: {produto.categoria}\n"
            f"  Preço:       {produto.preco:,.2f} AOA\n"
            f"  Stock:       {produto.stock} unidades"
        )
        self._label_info_produto.configure(
            text=info, text_color=cor
        )

    def _ajustar_quantidade(self, delta: int) -> None:
        """Ajusta a quantidade ±1."""
        try:
            atual = int(self._entry_qtd.get())
            nova = max(1, atual + delta)
            self._entry_qtd.delete(0, "end")
            self._entry_qtd.insert(0, str(nova))
        except ValueError:
            self._entry_qtd.delete(0, "end")
            self._entry_qtd.insert(0, "1")

    def _registrar_venda(self) -> None:
        """Processa o registo de uma nova venda."""
        nome_produto = self._combo_produto.get()
        qtd_str      = self._entry_qtd.get().strip()
        observacoes  = self._entry_obs.get("1.0", "end").strip()

        # Validação
        if not nome_produto or nome_produto == "Sem produtos":
            self._label_msg.configure(text="⚠  Seleccione um produto.")
            return
        try:
            quantidade = int(qtd_str)
            if quantidade <= 0:
                raise ValueError
        except ValueError:
            self._label_msg.configure(text="⚠  Quantidade inválida. Use número inteiro > 0.")
            return

        # Obtém o produto
        produto = next((p for p in self._lista_produtos if p.nome == nome_produto), None)
        if not produto:
            self._label_msg.configure(text="⚠  Produto não encontrado.")
            return

        # Obtém o utilizador actual
        user = self._auth_svc.current_user
        vendido_por = user.username if user else "sistema"

        # Confirmação
        total_prev = produto.preco * quantidade
        confirmar = messagebox.askyesno(
            "Confirmar Venda",
            f"Confirma a seguinte venda?\n\n"
            f"  Produto   : {produto.nome}\n"
            f"  Quantidade: {quantidade} unidades\n"
            f"  Total     : {total_prev:,.2f} AOA\n",
            parent=self,
        )
        if not confirmar:
            return

        try:
            self._venda_svc.registrar_venda(
                produto_id=str(produto.id),
                quantidade=quantidade,
                vendido_por=vendido_por,
                observacoes=observacoes,
            )

            self._label_msg.configure(
                text=f"✓  Venda registada! Total: {total_prev:,.2f} AOA",
                text_color=COLORS["success"],
            )
            # Limpa formulário
            self._entry_qtd.delete(0, "end")
            self._entry_qtd.insert(0, "1")
            self._entry_obs.delete("1.0", "end")

            # Recarrega dados
            self._lista_produtos = self._produto_svc.obter_todos()
            nomes = [p.nome for p in self._lista_produtos]
            self._combo_produto.configure(values=nomes)
            self._ao_seleccionar_produto(nome_produto)
            self._carregar_historico()

        except InsufficientStockException as e:
            self._label_msg.configure(
                text=f"⚠  {e.message}", text_color=COLORS["danger"]
            )
        except Exception as e:
            self._label_msg.configure(
                text=f"⚠  Erro: {e}", text_color=COLORS["danger"]
            )

    def _carregar_historico(self) -> None:
        """Carrega o histórico de vendas na tabela."""
        for item in self._tabela.get_children():
            self._tabela.delete(item)

        try:
            vendas = self._venda_svc.obter_todos()
            for venda in vendas:
                self._tabela.insert(
                    "", "end",
                    values=(
                        venda.data_formatada,
                        venda.nome_produto,
                        venda.quantidade,
                        f"{venda.preco_unitario:,.2f}",
                        f"{venda.total:,.2f}",
                        venda.vendido_por,
                    ),
                )
            self._construir_stats()
        except Exception as e:
            logger.error(f"Erro ao carregar histórico: {e}")
