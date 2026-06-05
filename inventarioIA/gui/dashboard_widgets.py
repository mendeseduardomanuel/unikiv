"""
=============================================================================
Ficheiro: gui/dashboard_widgets.py
Descrição: Widgets do Dashboard: cartões de KPI, gráficos Matplotlib
           e sumários de stock baixo.
=============================================================================
"""

import logging
import customtkinter as ctk
from tkinter import ttk
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.ticker as ticker

from services.produto_service import ProdutoService
from services.venda_service import VendaService
from services.ia_service import IAService
from config.settings import COLORS, FONTS

logger = logging.getLogger(__name__)


class DashboardView(ctk.CTkFrame):
    """
    Painel de Dashboard com cartões de KPI e gráficos.

    Layout:
      ┌─────────────────────────────────────────┐
      │  [KPI1] [KPI2] [KPI3] [KPI4]            │
      ├─────────────────────────────────────────┤
      │  [Gráfico de Vendas]  [Produtos Baixos] │
      └─────────────────────────────────────────┘
    """

    def __init__(
        self,
        parent,
        produto_svc: ProdutoService,
        venda_svc: VendaService,
        ia_svc: IAService,
    ) -> None:
        super().__init__(parent, fg_color="transparent")
        self._produto_svc = produto_svc
        self._venda_svc = venda_svc
        self._ia_svc = ia_svc
        self._construir()

    def _construir(self) -> None:
        """Constrói todos os widgets do dashboard."""
        # Título da secção
        ctk.CTkLabel(
            self,
            text="Visão Geral do Inventário",
            font=FONTS["subtitle"],
            text_color=COLORS["text_primary"],
        ).pack(anchor="w", padx=24, pady=(20, 6))

        ctk.CTkLabel(
            self,
            text="Resumo actualizado em tempo real",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"],
        ).pack(anchor="w", padx=24, pady=(0, 18))

        # ---- Linha de KPIs ----
        self._frame_kpis = ctk.CTkFrame(self, fg_color="transparent")
        self._frame_kpis.pack(fill="x", padx=20, pady=(0, 20))
        self._construir_kpis()

        # ---- Linha de Gráficos ----
        frame_graficos = ctk.CTkFrame(self, fg_color="transparent")
        frame_graficos.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Gráfico de vendas (esquerda)
        self._frame_grafico_vendas = ctk.CTkFrame(
            frame_graficos,
            fg_color=COLORS["card_bg"],
            corner_radius=12,
        )
        self._frame_grafico_vendas.pack(
            side="left", fill="both", expand=True, padx=(0, 10)
        )
        self._construir_grafico_vendas()

        # Lista de stock baixo (direita)
        frame_stock_baixo = ctk.CTkFrame(
            frame_graficos,
            fg_color=COLORS["card_bg"],
            corner_radius=12,
            width=280,
        )
        frame_stock_baixo.pack(side="right", fill="y", padx=(10, 0))
        frame_stock_baixo.pack_propagate(False)
        self._construir_lista_stock_baixo(frame_stock_baixo)

    # =================================================================
    # KPIs
    # =================================================================

    def _construir_kpis(self) -> None:
        """Constrói os cartões de indicadores-chave de desempenho."""
        try:
            stats_prod = self._produto_svc.obter_estatisticas()
            stats_venda = self._venda_svc.obter_estatisticas_gerais()
        except Exception as e:
            logger.error(f"Erro ao carregar estatísticas: {e}")
            stats_prod = {}
            stats_venda = {}

        # Gera previsão IA (se modelo disponível)
        previsao_ia = "—"
        try:
            if not self._ia_svc.modelo_treinado():
                self._ia_svc.carregar_modelo()
            previsoes = self._ia_svc.prever(1)
            if previsoes:
                previsao_ia = f"~{previsoes[0]:.0f} un."
        except Exception:
            pass

        kpis = [
            {
                "icone":  "📦",
                "titulo": "Total de Produtos",
                "valor":  str(stats_prod.get("total_produtos", 0)),
                "sub":    f"{stats_prod.get('total_categorias', 0)} categorias",
                "cor":    COLORS["primary"],
            },
            {
                "icone":  "⚠️",
                "titulo": "Stock Baixo",
                "valor":  str(stats_prod.get("produtos_stock_baixo", 0)),
                "sub":    f"{stats_prod.get('produtos_sem_stock', 0)} sem stock",
                "cor":    COLORS["warning"],
            },
            {
                "icone":  "💰",
                "titulo": "Receita Total",
                "valor":  f"{stats_venda.get('receita_total', 0):,.2f}",
                "sub":    f"{stats_venda.get('total_vendas', 0)} vendas",
                "cor":    COLORS["success"],
            },
            {
                "icone":  "🤖",
                "titulo": "Previsão IA",
                "valor":  previsao_ia,
                "sub":    "próximo período",
                "cor":    "#9b59b6",
            },
        ]

        for kpi in kpis:
            self._criar_cartao_kpi(
                self._frame_kpis,
                kpi["icone"],
                kpi["titulo"],
                kpi["valor"],
                kpi["sub"],
                kpi["cor"],
            )

    def _criar_cartao_kpi(
        self,
        parent,
        icone: str,
        titulo: str,
        valor: str,
        subtitulo: str,
        cor_destaque: str,
    ) -> None:
        """Cria um cartão KPI individual."""
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS["card_bg"],
            corner_radius=14,
        )
        card.pack(side="left", fill="both", expand=True, padx=8)

        # Barra colorida no topo
        ctk.CTkFrame(
            card, height=4, fg_color=cor_destaque, corner_radius=2
        ).pack(fill="x", padx=0, pady=(0, 0))

        ctk.CTkLabel(card, text=icone, font=("Segoe UI", 30)).pack(
            pady=(14, 2)
        )
        ctk.CTkLabel(
            card,
            text=titulo,
            font=FONTS["small"],
            text_color=COLORS["text_secondary"],
        ).pack()
        ctk.CTkLabel(
            card,
            text=valor,
            font=("Segoe UI", 26, "bold"),
            text_color=cor_destaque,
        ).pack(pady=(4, 2))
        ctk.CTkLabel(
            card,
            text=subtitulo,
            font=FONTS["small"],
            text_color=COLORS["text_secondary"],
        ).pack(pady=(0, 16))

    # =================================================================
    # Gráfico de Vendas (Matplotlib)
    # =================================================================

    def _construir_grafico_vendas(self) -> None:
        """Constrói o gráfico de receita mensal com Matplotlib."""
        ctk.CTkLabel(
            self._frame_grafico_vendas,
            text="📈  Receita Mensal (últimos 6 meses)",
            font=FONTS["body"],
            text_color=COLORS["text_primary"],
        ).pack(anchor="w", padx=16, pady=(14, 6))

        try:
            dados = self._venda_svc.obter_vendas_por_mes_todos_produtos()

            # Pega os últimos 6 períodos
            dados = dados[-6:] if len(dados) >= 6 else dados

            if not dados:
                ctk.CTkLabel(
                    self._frame_grafico_vendas,
                    text="Sem dados de vendas ainda.\nRegiste as primeiras vendas!",
                    font=FONTS["body"],
                    text_color=COLORS["text_secondary"],
                ).pack(expand=True, pady=60)
                return

            labels = [d["periodo"] for d in dados]
            valores = [d["total"] for d in dados]

            # Cria figura Matplotlib com fundo escuro
            fig, ax = plt.subplots(figsize=(5.5, 3.2))
            fig.patch.set_facecolor("#2b2b2b")
            ax.set_facecolor("#2b2b2b")

            # Gráfico de barras com gradiente
            bars = ax.bar(
                labels,
                valores,
                color=COLORS["primary"],
                width=0.55,
                edgecolor="none",
            )

            # Destaca a barra mais alta
            if valores:
                idx_max = valores.index(max(valores))
                bars[idx_max].set_color(COLORS["success"])

            # Linha de tendência
            if len(valores) >= 2:
                ax.plot(
                    labels,
                    valores,
                    color=COLORS["warning"],
                    linewidth=2,
                    marker="o",
                    markersize=5,
                    linestyle="--",
                    alpha=0.7,
                )

            # Valores nas barras
            for bar, val in zip(bars, valores):
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + max(valores) * 0.02,
                    f"{val:,.0f}",
                    ha="center",
                    va="bottom",
                    color="white",
                    fontsize=8,
                )

            ax.tick_params(colors="white", labelsize=8)
            ax.spines[:].set_color("#444")
            ax.yaxis.set_major_formatter(
                ticker.FuncFormatter(lambda x, _: f"{x:,.0f}")
            )
            ax.set_ylabel("Receita", color="#aaa", fontsize=8)
            plt.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=self._frame_grafico_vendas)
            canvas.draw()
            canvas.get_tk_widget().pack(
                fill="both", expand=True, padx=10, pady=(0, 14)
            )
            plt.close(fig)

        except Exception as e:
            logger.error(f"Erro ao construir gráfico de vendas: {e}")
            ctk.CTkLabel(
                self._frame_grafico_vendas,
                text=f"Erro ao carregar gráfico:\n{e}",
                text_color=COLORS["danger"],
                font=FONTS["small"],
            ).pack(pady=40)

    # =================================================================
    # Lista de Stock Baixo
    # =================================================================

    def _construir_lista_stock_baixo(self, parent) -> None:
        """Constrói a lista de produtos com stock baixo."""
        ctk.CTkLabel(
            parent,
            text="⚠️  Produtos com Stock Baixo",
            font=FONTS["body"],
            text_color=COLORS["warning"],
        ).pack(anchor="w", padx=16, pady=(14, 6))

        try:
            produtos = self._produto_svc.obter_com_stock_baixo()

            if not produtos:
                ctk.CTkLabel(
                    parent,
                    text="✓  Todos os produtos\nestão com stock normal!",
                    font=FONTS["body"],
                    text_color=COLORS["success"],
                ).pack(expand=True)
                return

            frame_scroll = ctk.CTkScrollableFrame(
                parent,
                fg_color="transparent",
                corner_radius=0,
            )
            frame_scroll.pack(fill="both", expand=True, padx=8, pady=(0, 10))

            for produto in produtos:
                frame_item = ctk.CTkFrame(
                    frame_scroll,
                    fg_color=COLORS["secondary"],
                    corner_radius=8,
                )
                frame_item.pack(fill="x", pady=3)

                # Cor do stock: vermelho se 0, laranja se baixo
                cor_stock = (
                    COLORS["danger"] if produto.stock == 0 else COLORS["warning"]
                )

                ctk.CTkLabel(
                    frame_item,
                    text=produto.nome[:22] + ("…" if len(produto.nome) > 22 else ""),
                    font=FONTS["small"],
                    text_color=COLORS["text_primary"],
                    anchor="w",
                ).pack(side="left", padx=10, pady=8)

                ctk.CTkLabel(
                    frame_item,
                    text=f"{produto.stock} un.",
                    font=("Segoe UI", 11, "bold"),
                    text_color=cor_stock,
                ).pack(side="right", padx=10)

        except Exception as e:
            logger.error(f"Erro ao listar stock baixo: {e}")
            ctk.CTkLabel(
                parent,
                text=f"Erro: {e}",
                text_color=COLORS["danger"],
                font=FONTS["small"],
            ).pack(pady=20)
