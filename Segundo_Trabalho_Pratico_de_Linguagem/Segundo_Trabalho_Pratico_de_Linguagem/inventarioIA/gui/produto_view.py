"""
=============================================================================
Ficheiro: gui/produto_view.py
Descrição: Interface gráfica completa para gestão de produtos (CRUD).
           Tabela com pesquisa, formulário de edição em diálogo.
=============================================================================
"""

import logging
import customtkinter as ctk
from tkinter import ttk, messagebox
from typing import Optional

from services.produto_service import ProdutoService
from models.produto import Produto
from exceptions.stock_exception import (
    DuplicateProductException,
    ProductNotFoundException,
    InvalidProductDataException,
)
from config.settings import COLORS, FONTS

logger = logging.getLogger(__name__)


class ProdutoView(ctk.CTkFrame):
    """
    Módulo de gestão de produtos com operações CRUD completas.

    Funcionalidades:
      - Listagem em tabela com estilo moderno (ttk.Treeview).
      - Pesquisa em tempo real por nome ou categoria.
      - Formulário para Adicionar / Editar produto (diálogo modal).
      - Confirmação antes de eliminar.
      - Indicadores visuais de stock baixo.
    """

    def __init__(self, parent, produto_svc: ProdutoService, auth_svc=None) -> None:
        super().__init__(parent, fg_color="transparent")
        self._produto_svc = produto_svc
        self._auth = auth_svc
        self._is_admin = (auth_svc and auth_svc.current_user and auth_svc.current_user.is_admin())
        self._produto_selecionado: Optional[Produto] = None
        self._construir()
        self._carregar_produtos()

    # =================================================================
    # Construção da Interface
    # =================================================================

    def _construir(self) -> None:
        """Constrói todos os widgets da vista de produtos."""
        # ---- Barra de Acções ----
        frame_acoes = ctk.CTkFrame(
            self, fg_color=COLORS["card_bg"], corner_radius=12
        )
        frame_acoes.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            frame_acoes,
            text="📦  Gestão de Produtos",
            font=FONTS["subtitle"],
        ).pack(side="left", padx=20, pady=14)

        # Botões de acção (direita)
        frame_btns = ctk.CTkFrame(frame_acoes, fg_color="transparent")
        frame_btns.pack(side="right", padx=16, pady=10)

        # Botões de escrita só visíveis para admin
        if getattr(self, "_is_admin", True):
            ctk.CTkButton(
                frame_btns,
                text="➕  Novo Produto",
                height=38, font=FONTS["body"],
                fg_color=COLORS["success"], hover_color="#1e7e34",
                corner_radius=10, command=self._abrir_formulario_adicionar,
            ).pack(side="left", padx=6)
            ctk.CTkButton(
                frame_btns,
                text="✏️  Editar",
                height=38, font=FONTS["body"],
                fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
                corner_radius=10, command=self._editar_selecionado,
            ).pack(side="left", padx=6)
            ctk.CTkButton(
                frame_btns,
                text="🗑  Eliminar",
                height=38, font=FONTS["body"],
                fg_color=COLORS["danger"], hover_color="#a71d2a",
                corner_radius=10, command=self._eliminar_selecionado,
            ).pack(side="left", padx=6)
        else:
            ctk.CTkLabel(
                frame_btns,
                text="🔒  Somente leitura — contacte um Admin para modificar",
                font=FONTS["small"], text_color=COLORS["warning"],
            ).pack(side="left", padx=10)

        ctk.CTkButton(
            frame_btns,
            text="🔄  Actualizar",
            height=38,
            font=FONTS["body"],
            fg_color=COLORS["secondary"],
            hover_color="#3a3a3a",
            corner_radius=10,
            command=self._carregar_produtos,
        ).pack(side="left", padx=6)

        # ---- Barra de Pesquisa ----
        frame_pesquisa = ctk.CTkFrame(
            self, fg_color=COLORS["card_bg"], corner_radius=12
        )
        frame_pesquisa.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(
            frame_pesquisa, text="🔍", font=("Segoe UI", 16)
        ).pack(side="left", padx=(16, 4), pady=10)

        self._entry_pesquisa = ctk.CTkEntry(
            frame_pesquisa,
            placeholder_text="Pesquisar por nome...",
            height=38,
            width=280,
            font=FONTS["body"],
            corner_radius=8,
        )
        self._entry_pesquisa.pack(side="left", padx=6, pady=10)
        self._entry_pesquisa.bind("<KeyRelease>", lambda e: self._pesquisar())

        # Filtro por categoria
        ctk.CTkLabel(
            frame_pesquisa,
            text="Categoria:",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"],
        ).pack(side="left", padx=(16, 4))

        self._combo_categoria = ctk.CTkComboBox(
            frame_pesquisa,
            values=["Todas"] + self._produto_svc.obter_categorias(),
            width=180,
            height=38,
            font=FONTS["body"],
            command=self._filtrar_categoria,
        )
        self._combo_categoria.set("Todas")
        self._combo_categoria.pack(side="left", padx=6)

        # Contador de resultados
        self._label_contador = ctk.CTkLabel(
            frame_pesquisa,
            text="",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"],
        )
        self._label_contador.pack(side="right", padx=20)

        # ---- Tabela de Produtos ----
        frame_tabela = ctk.CTkFrame(
            self, fg_color=COLORS["card_bg"], corner_radius=12
        )
        frame_tabela.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self._tabela = self._criar_tabela(frame_tabela)

    def _criar_tabela(self, parent) -> ttk.Treeview:
        """Cria e configura a tabela ttk.Treeview."""
        # Estilo escuro para a tabela
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Inventario.Treeview",
            background=COLORS["secondary"],
            foreground="white",
            rowheight=36,
            fieldbackground=COLORS["secondary"],
            borderwidth=0,
            font=("Segoe UI", 12),
        )
        style.configure(
            "Inventario.Treeview.Heading",
            background=COLORS["sidebar"],
            foreground=COLORS["primary"],
            font=("Segoe UI", 12, "bold"),
            relief="flat",
        )
        style.map(
            "Inventario.Treeview",
            background=[("selected", COLORS["primary"])],
        )

        colunas = ("nome", "categoria", "preco", "stock", "estado", "valor_total")

        frame_inner = ctk.CTkFrame(parent, fg_color="transparent")
        frame_inner.pack(fill="both", expand=True, padx=12, pady=12)

        tabela = ttk.Treeview(
            frame_inner,
            columns=colunas,
            show="headings",
            style="Inventario.Treeview",
            selectmode="browse",
        )

        # Cabeçalhos
        tabela.heading("nome",       text="Nome do Produto",  anchor="w")
        tabela.heading("categoria",  text="Categoria",         anchor="w")
        tabela.heading("preco",      text="Preço (AOA)",       anchor="e")
        tabela.heading("stock",      text="Stock",             anchor="center")
        tabela.heading("estado",     text="Estado",            anchor="center")
        tabela.heading("valor_total",text="Valor em Stock",    anchor="e")

        # Larguras das colunas
        tabela.column("nome",        width=240, minwidth=140, anchor="w")
        tabela.column("categoria",   width=140, minwidth=80,  anchor="w")
        tabela.column("preco",       width=120, minwidth=80,  anchor="e")
        tabela.column("stock",       width=80,  minwidth=60,  anchor="center")
        tabela.column("estado",      width=110, minwidth=80,  anchor="center")
        tabela.column("valor_total", width=130, minwidth=90,  anchor="e")

        # Tags de cor por estado
        tabela.tag_configure("critico", foreground=COLORS["danger"])
        tabela.tag_configure("baixo",   foreground=COLORS["warning"])
        tabela.tag_configure("normal",  foreground="white")

        # Scrollbar vertical
        scrollbar = ttk.Scrollbar(frame_inner, orient="vertical", command=tabela.yview)
        tabela.configure(yscrollcommand=scrollbar.set)
        tabela.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Duplo clique para editar
        tabela.bind("<Double-1>", lambda e: self._editar_selecionado())

        self._tabela_ref = tabela
        return tabela

    # =================================================================
    # Carregamento de Dados
    # =================================================================

    def _carregar_produtos(self, produtos=None) -> None:
        """
        Carrega (ou recarrega) a lista de produtos na tabela.

        Parâmetros:
            produtos: Lista opcional de Produto. Se None, busca todos.
        """
        # Limpa tabela
        for item in self._tabela_ref.get_children():
            self._tabela_ref.delete(item)

        try:
            lista = produtos if produtos is not None else self._produto_svc.obter_todos()

            for produto in lista:
                # Determina a tag de cor
                estado = produto.estado_stock
                if estado in ("Sem Stock", "Crítico"):
                    tag = "critico"
                elif estado == "Baixo":
                    tag = "baixo"
                else:
                    tag = "normal"

                self._tabela_ref.insert(
                    "",
                    "end",
                    iid=str(produto.id),
                    values=(
                        produto.nome,
                        produto.categoria,
                        f"{produto.preco:,.2f}",
                        produto.stock,
                        estado,
                        f"{produto.valor_total_stock:,.2f}",
                    ),
                    tags=(tag,),
                )

            self._label_contador.configure(
                text=f"Total: {len(lista)} produto(s)"
            )

            # Actualiza o combobox de categorias
            cats = ["Todas"] + self._produto_svc.obter_categorias()
            self._combo_categoria.configure(values=cats)

        except Exception as e:
            logger.error(f"Erro ao carregar produtos: {e}")
            messagebox.showerror("Erro", f"Erro ao carregar produtos:\n{e}", parent=self)

    def _pesquisar(self) -> None:
        """Filtra produtos pelo texto de pesquisa."""
        texto = self._entry_pesquisa.get().strip()
        categoria = self._combo_categoria.get()

        filtros: dict = {}
        if texto:
            filtros["nome"] = texto
        if categoria and categoria != "Todas":
            filtros["categoria"] = categoria

        if filtros:
            resultados = self._produto_svc.pesquisar(filtros)
        else:
            resultados = self._produto_svc.obter_todos()

        self._carregar_produtos(resultados)

    def _filtrar_categoria(self, categoria: str) -> None:
        """Filtra produtos pela categoria seleccionada."""
        self._pesquisar()

    def _obter_produto_selecionado(self) -> Optional[Produto]:
        """Obtém o produto seleccionado na tabela."""
        selecao = self._tabela_ref.selection()
        if not selecao:
            return None
        produto_id = selecao[0]
        return self._produto_svc.obter_por_id(produto_id)

    # =================================================================
    # Operações CRUD
    # =================================================================

    def _abrir_formulario_adicionar(self) -> None:
        """Abre o diálogo para adicionar um novo produto."""
        FormularioProduto(
            parent=self.winfo_toplevel(),
            produto_svc=self._produto_svc,
            produto=None,
            on_guardar=self._carregar_produtos,
        )

    def _editar_selecionado(self) -> None:
        """Abre o formulário de edição para o produto seleccionado."""
        produto = self._obter_produto_selecionado()
        if not produto:
            messagebox.showinfo(
                "Seleccionar", "Por favor, seleccione um produto na tabela.",
                parent=self
            )
            return
        FormularioProduto(
            parent=self.winfo_toplevel(),
            produto_svc=self._produto_svc,
            produto=produto,
            on_guardar=self._carregar_produtos,
        )

    def _eliminar_selecionado(self) -> None:
        """Elimina o produto seleccionado após confirmação."""
        produto = self._obter_produto_selecionado()
        if not produto:
            messagebox.showinfo(
                "Seleccionar", "Por favor, seleccione um produto na tabela.",
                parent=self
            )
            return

        confirmado = messagebox.askyesno(
            "Confirmar Eliminação",
            f"Tem a certeza que deseja desactivar o produto:\n\n"
            f"'{produto.nome}'\n\n"
            "Esta acção marca o produto como inactivo.",
            icon="warning",
            parent=self,
        )
        if not confirmado:
            return

        try:
            self._produto_svc.eliminar(str(produto.id))
            messagebox.showinfo(
                "Sucesso",
                f"Produto '{produto.nome}' desactivado com sucesso.",
                parent=self,
            )
            self._carregar_produtos()
        except ProductNotFoundException as e:
            messagebox.showerror("Erro", str(e), parent=self)
        except Exception as e:
            messagebox.showerror("Erro Inesperado", str(e), parent=self)


# =============================================================================
# Formulário de Produto (Diálogo Modal)
# =============================================================================

class FormularioProduto(ctk.CTkToplevel):
    """
    Diálogo modal para adicionar ou editar um produto.

    POO: Herança - herda de ctk.CTkToplevel (janela secundária).
    """

    CATEGORIAS = [
        "Alimentação", "Bebidas", "Higiene", "Limpeza",
        "Electrónica", "Vestuário", "Ferramentas", "Material Escolar",
        "Farmácia", "Agricultura", "Construção", "Geral",
    ]

    def __init__(
        self,
        parent,
        produto_svc: ProdutoService,
        produto: Optional[Produto],
        on_guardar,
    ) -> None:
        super().__init__(parent)
        self._produto_svc = produto_svc
        self._auth = auth_svc
        self._is_admin = (auth_svc and auth_svc.current_user and auth_svc.current_user.is_admin())
        self._produto = produto
        self._on_guardar = on_guardar

        self._modo = "Editar" if produto else "Adicionar"
        self.title(f"{self._modo} Produto")
        self.geometry("520x580")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["secondary"])
        self.grab_set()  # Modal
        self.focus_set()

        # Centraliza relativo ao pai
        self.update_idletasks()
        px = parent.winfo_x() + (parent.winfo_width() - 520) // 2
        py = parent.winfo_y() + (parent.winfo_height() - 580) // 2
        self.geometry(f"520x580+{px}+{py}")

        self._construir()
        if produto:
            self._preencher_formulario(produto)

    def _construir(self) -> None:
        """Constrói o formulário."""
        # Cabeçalho
        frame_header = ctk.CTkFrame(
            self, fg_color=COLORS["primary"], corner_radius=0
        )
        frame_header.pack(fill="x")
        ctk.CTkLabel(
            frame_header,
            text=f"{'➕' if self._modo == 'Adicionar' else '✏️'}  {self._modo} Produto",
            font=FONTS["subtitle"],
            text_color="white",
        ).pack(padx=24, pady=16)

        # Frame do formulário
        frame_form = ctk.CTkScrollableFrame(
            self, fg_color="transparent"
        )
        frame_form.pack(fill="both", expand=True, padx=24, pady=20)

        # ---- Nome ----
        self._entry_nome = self._criar_campo(frame_form, "Nome do Produto *", "ex: Arroz 5kg")

        # ---- Categoria ----
        ctk.CTkLabel(
            frame_form, text="Categoria *", font=FONTS["small"],
            text_color=COLORS["text_secondary"], anchor="w"
        ).pack(fill="x", pady=(10, 2))
        self._combo_cat = ctk.CTkComboBox(
            frame_form,
            values=self.CATEGORIAS,
            height=40,
            font=FONTS["body"],
            corner_radius=8,
        )
        self._combo_cat.set("Geral")
        self._combo_cat.pack(fill="x", pady=(0, 6))

        # ---- Preço ----
        self._entry_preco = self._criar_campo(frame_form, "Preço Unitário (AOA) *", "ex: 1500.00")

        # ---- Stock ----
        self._entry_stock = self._criar_campo(frame_form, "Stock Actual *", "ex: 100")

        # ---- Stock Mínimo ----
        self._entry_stock_min = self._criar_campo(frame_form, "Stock Mínimo (alerta)", "ex: 10")
        self._entry_stock_min.insert(0, "10")

        # ---- Descrição ----
        ctk.CTkLabel(
            frame_form, text="Descrição", font=FONTS["small"],
            text_color=COLORS["text_secondary"], anchor="w"
        ).pack(fill="x", pady=(10, 2))
        self._text_desc = ctk.CTkTextbox(
            frame_form, height=80, font=FONTS["body"], corner_radius=8
        )
        self._text_desc.pack(fill="x", pady=(0, 6))

        # ---- Mensagem ----
        self._label_msg = ctk.CTkLabel(
            frame_form, text="", font=FONTS["small"],
            text_color=COLORS["danger"], wraplength=440
        )
        self._label_msg.pack(pady=4)

        # ---- Botões ----
        frame_btns = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=0)
        frame_btns.pack(fill="x", side="bottom")

        ctk.CTkButton(
            frame_btns,
            text="Cancelar",
            height=42,
            font=FONTS["body"],
            fg_color=COLORS["secondary"],
            hover_color="#3a3a3a",
            corner_radius=10,
            command=self.destroy,
        ).pack(side="left", padx=(16, 8), pady=14)

        ctk.CTkButton(
            frame_btns,
            text=f"💾  {self._modo} Produto",
            height=42,
            font=FONTS["button"],
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            corner_radius=10,
            command=self._guardar,
        ).pack(side="right", padx=(8, 16), pady=14)

    def _criar_campo(self, parent, label: str, placeholder: str) -> ctk.CTkEntry:
        """Helper para criar um campo de formulário."""
        ctk.CTkLabel(
            parent, text=label, font=FONTS["small"],
            text_color=COLORS["text_secondary"], anchor="w"
        ).pack(fill="x", pady=(10, 2))
        entry = ctk.CTkEntry(
            parent, placeholder_text=placeholder,
            height=40, font=FONTS["body"], corner_radius=8
        )
        entry.pack(fill="x", pady=(0, 6))
        return entry

    def _preencher_formulario(self, produto: Produto) -> None:
        """Preenche o formulário com os dados do produto a editar."""
        self._entry_nome.insert(0, produto.nome)
        self._combo_cat.set(produto.categoria)
        self._entry_preco.insert(0, str(produto.preco))
        self._entry_stock.insert(0, str(produto.stock))
        self._entry_stock_min.delete(0, "end")
        self._entry_stock_min.insert(0, str(produto.stock_minimo))
        if produto.descricao:
            self._text_desc.insert("1.0", produto.descricao)

    def _guardar(self) -> None:
        """Valida e guarda o produto."""
        # Recolhe dados
        nome       = self._entry_nome.get().strip()
        categoria  = self._combo_cat.get()
        preco_str  = self._entry_preco.get().strip()
        stock_str  = self._entry_stock.get().strip()
        stockm_str = self._entry_stock_min.get().strip()
        descricao  = self._text_desc.get("1.0", "end").strip()

        # Validação
        if not nome:
            self._label_msg.configure(text="⚠  O nome é obrigatório.")
            return
        try:
            preco = float(preco_str.replace(",", "."))
            if preco < 0:
                raise ValueError
        except ValueError:
            self._label_msg.configure(text="⚠  Preço inválido. Use formato numérico.")
            return
        try:
            stock = int(stock_str)
            if stock < 0:
                raise ValueError
        except ValueError:
            self._label_msg.configure(text="⚠  Stock inválido. Use número inteiro ≥ 0.")
            return
        try:
            stock_min = int(stockm_str) if stockm_str else 10
        except ValueError:
            stock_min = 10

        dados = {
            "nome": nome,
            "categoria": categoria,
            "preco": preco,
            "stock": stock,
            "stock_minimo": stock_min,
            "descricao": descricao,
        }

        try:
            if self._produto:
                self._produto_svc.actualizar(str(self._produto.id), dados)
                msg = f"Produto '{nome}' actualizado com sucesso!"
            else:
                self._produto_svc.criar(dados)
                msg = f"Produto '{nome}' adicionado com sucesso!"

            messagebox.showinfo("Sucesso", msg, parent=self)
            self._on_guardar()
            self.destroy()

        except DuplicateProductException as e:
            self._label_msg.configure(text=f"⚠  {e.message}")
        except InvalidProductDataException as e:
            self._label_msg.configure(text=f"⚠  {e.message}")
        except Exception as e:
            self._label_msg.configure(text=f"⚠  Erro: {e}")
