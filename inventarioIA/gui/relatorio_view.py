"""
=============================================================================
Ficheiro: gui/relatorio_view.py
Descrição: Módulo de relatórios com estatísticas, gráficos e exportação CSV.
=============================================================================
"""

import logging
import os
from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox, filedialog
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from services.produto_service import ProdutoService
from services.venda_service import VendaService
from services.ia_service import IAService
from utils.context_manager import CSVWriter
from config.settings import COLORS, FONTS, CSV_EXPORT_PATH

logger = logging.getLogger(__name__)


class RelatorioView(ctk.CTkFrame):
    """
    Módulo de relatórios e análises estatísticas.

    Funcionalidades:
      - Estatísticas de produtos e vendas.
      - Gráficos de distribuição por categoria.
      - Exportação de relatórios para CSV.
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
        """Constrói a interface de relatórios."""
        # Cabeçalho com botões de exportação
        frame_header = ctk.CTkFrame(
            self, fg_color=COLORS["card_bg"], corner_radius=12
        )
        frame_header.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            frame_header, text="📊  Relatórios e Análises",
            font=FONTS["subtitle"]
        ).pack(side="left", padx=20, pady=14)

        frame_btns = ctk.CTkFrame(frame_header, fg_color="transparent")
        frame_btns.pack(side="right", padx=16, pady=10)

        ctk.CTkButton(
            frame_btns,
            text="📥  Exportar Produtos (CSV)",
            height=38, font=FONTS["small"],
            fg_color=COLORS["success"], hover_color="#1e7e34",
            corner_radius=10,
            command=self._exportar_produtos_csv,
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            frame_btns,
            text="📥  Exportar Vendas (CSV)",
            height=38, font=FONTS["small"],
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            corner_radius=10,
            command=self._exportar_vendas_csv,
        ).pack(side="left", padx=4)

        # Layout de gráficos
        frame_graficos = ctk.CTkFrame(self, fg_color="transparent")
        frame_graficos.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Coluna esquerda
        frame_esq = ctk.CTkFrame(frame_graficos, fg_color="transparent")
        frame_esq.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Coluna direita
        frame_dir = ctk.CTkFrame(frame_graficos, fg_color="transparent")
        frame_dir.pack(side="right", fill="both", expand=True, padx=(10, 0))

        # Gráfico 1: distribuição por categoria
        frame_g1 = ctk.CTkFrame(frame_esq, fg_color=COLORS["card_bg"], corner_radius=12)
        frame_g1.pack(fill="both", expand=True, pady=(0, 10))
        self._grafico_categorias(frame_g1)

        # Gráfico 2: top 5 produtos por stock
        frame_g2 = ctk.CTkFrame(frame_esq, fg_color=COLORS["card_bg"], corner_radius=12)
        frame_g2.pack(fill="both", expand=True)
        self._grafico_top_stock(frame_g2)

        # Painel de estatísticas
        frame_stats = ctk.CTkFrame(frame_dir, fg_color=COLORS["card_bg"], corner_radius=12)
        frame_stats.pack(fill="both", expand=True)
        self._painel_estatisticas(frame_stats)

    # =================================================================
    # Gráficos
    # =================================================================

    def _grafico_categorias(self, parent) -> None:
        """Gráfico de pizza — distribuição de produtos por categoria."""
        ctk.CTkLabel(
            parent, text="🗂  Produtos por Categoria",
            font=FONTS["body"]
        ).pack(padx=16, pady=(12, 4), anchor="w")

        try:
            produtos = self._produto_svc.obter_todos()
            if not produtos:
                ctk.CTkLabel(
                    parent, text="Sem dados.",
                    text_color=COLORS["text_secondary"], font=FONTS["body"]
                ).pack(expand=True, pady=30)
                return

            contagem: dict = {}
            for p in produtos:
                contagem[p.categoria] = contagem.get(p.categoria, 0) + 1

            fig, ax = plt.subplots(figsize=(4.5, 2.8))
            fig.patch.set_facecolor("#2b2b2b")
            ax.set_facecolor("#2b2b2b")

            cores = [
                "#1f6aa5", "#28a745", "#ffc107", "#dc3545",
                "#9b59b6", "#1abc9c", "#e67e22", "#3498db",
            ]
            wedges, texts, autotexts = ax.pie(
                list(contagem.values()),
                labels=list(contagem.keys()),
                autopct="%1.0f%%",
                colors=cores[: len(contagem)],
                startangle=90,
                wedgeprops={"edgecolor": "#2b2b2b", "linewidth": 2},
            )
            for text in texts:
                text.set_color("white")
                text.set_fontsize(8)
            for autotext in autotexts:
                autotext.set_color("white")
                autotext.set_fontsize(8)

            plt.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=(0, 10))
            plt.close(fig)

        except Exception as e:
            ctk.CTkLabel(parent, text=f"Erro: {e}", text_color=COLORS["danger"]).pack(pady=20)

    def _grafico_top_stock(self, parent) -> None:
        """Gráfico de barras — Top 5 produtos com mais stock."""
        ctk.CTkLabel(
            parent, text="📦  Top 5 — Maior Stock",
            font=FONTS["body"]
        ).pack(padx=16, pady=(12, 4), anchor="w")

        try:
            produtos = sorted(
                self._produto_svc.obter_todos(),
                key=lambda p: p.stock,
                reverse=True,
            )[:5]

            if not produtos:
                ctk.CTkLabel(
                    parent, text="Sem dados.",
                    text_color=COLORS["text_secondary"]
                ).pack(expand=True, pady=30)
                return

            nomes = [p.nome[:16] + ("…" if len(p.nome) > 16 else "") for p in produtos]
            stocks = [p.stock for p in produtos]

            fig, ax = plt.subplots(figsize=(4.5, 2.8))
            fig.patch.set_facecolor("#2b2b2b")
            ax.set_facecolor("#2b2b2b")

            bars = ax.barh(nomes, stocks, color=COLORS["primary"], height=0.55)
            for bar, val in zip(bars, stocks):
                ax.text(
                    bar.get_width() + max(stocks) * 0.02,
                    bar.get_y() + bar.get_height() / 2,
                    str(val),
                    va="center", color="white", fontsize=9,
                )

            ax.tick_params(colors="white", labelsize=8)
            ax.spines[:].set_color("#444")
            ax.invert_yaxis()
            plt.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=(0, 10))
            plt.close(fig)

        except Exception as e:
            ctk.CTkLabel(parent, text=f"Erro: {e}", text_color=COLORS["danger"]).pack(pady=20)

    # =================================================================
    # Painel de Estatísticas
    # =================================================================

    def _painel_estatisticas(self, parent) -> None:
        """Constrói o painel de estatísticas resumidas."""
        ctk.CTkLabel(
            parent, text="📈  Resumo Estatístico",
            font=FONTS["subtitle"]
        ).pack(padx=20, pady=(16, 8), anchor="w")

        try:
            stats_p = self._produto_svc.obter_estatisticas()
            stats_v = self._venda_svc.obter_estatisticas_gerais()
        except Exception:
            stats_p = {}
            stats_v = {}

        items = [
            ("PRODUTOS", None, None),
            ("Total de Produtos",      str(stats_p.get("total_produtos", 0)),          COLORS["primary"]),
            ("Categorias",             str(stats_p.get("total_categorias", 0)),         COLORS["text_secondary"]),
            ("Stock Baixo / Crítico",  str(stats_p.get("produtos_stock_baixo", 0)),     COLORS["warning"]),
            ("Sem Stock",              str(stats_p.get("produtos_sem_stock", 0)),        COLORS["danger"]),
            ("Valor Total Inventário", f"{stats_p.get('valor_total_inventario', 0):,.2f} AOA", "#9b59b6"),
            ("VENDAS", None, None),
            ("Total de Vendas",        str(stats_v.get("total_vendas", 0)),              COLORS["primary"]),
            ("Vendas Hoje",            str(stats_v.get("vendas_hoje", 0)),               COLORS["success"]),
            ("Vendas Este Mês",        str(stats_v.get("vendas_mes", 0)),                COLORS["success"]),
            ("Receita Total",          f"{stats_v.get('receita_total', 0):,.2f} AOA",   COLORS["success"]),
            ("Receita Este Mês",       f"{stats_v.get('receita_mes', 0):,.2f} AOA",     COLORS["warning"]),
            ("Valor Médio/Venda",      f"{stats_v.get('media_por_venda', 0):,.2f} AOA", COLORS["text_secondary"]),
        ]

        frame_scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        frame_scroll.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        for item in items:
            if item[1] is None:
                # Separador de secção
                ctk.CTkLabel(
                    frame_scroll, text=f"  ── {item[0]} ──",
                    font=("Segoe UI", 11, "bold"),
                    text_color=COLORS["primary"]
                ).pack(anchor="w", pady=(10, 2))
                continue

            titulo, valor, cor = item
            f = ctk.CTkFrame(frame_scroll, fg_color=COLORS["secondary"], corner_radius=8)
            f.pack(fill="x", pady=2)
            ctk.CTkLabel(
                f, text=titulo, font=FONTS["small"],
                text_color=COLORS["text_secondary"], anchor="w"
            ).pack(side="left", padx=12, pady=8)
            ctk.CTkLabel(
                f, text=valor, font=("Segoe UI", 12, "bold"),
                text_color=cor
            ).pack(side="right", padx=12)

        # Data de geração
        ctk.CTkLabel(
            parent,
            text=f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"],
        ).pack(pady=(0, 12))

    # =================================================================
    # Exportação CSV
    # =================================================================

    def _exportar_produtos_csv(self) -> None:
        """Exporta o inventário de produtos para CSV."""
        caminho = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            initialfile=f"produtos_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            title="Guardar Relatório de Produtos",
        )
        if not caminho:
            return

        try:
            produtos = self._produto_svc.obter_todos()
            cabecalhos = [
                "ID", "Nome", "Categoria", "Preço (AOA)", "Stock",
                "Stock Mínimo", "Estado Stock", "Valor Total Stock (AOA)",
                "Descrição", "Criado Em",
            ]
            with CSVWriter(caminho, cabecalhos) as writer:
                for p in produtos:
                    d = p.to_dict()
                    writer.write_row([
                        d["id"], d["nome"], d["categoria"],
                        d["preco"], d["stock"], d["stock_minimo"],
                        d["estado_stock"], d["valor_total_stock"],
                        d["descricao"], d["criado_em"],
                    ])

            messagebox.showinfo(
                "Exportação Concluída",
                f"Relatório de produtos exportado com sucesso!\n\n{caminho}",
                parent=self,
            )
        except Exception as e:
            messagebox.showerror("Erro na Exportação", str(e), parent=self)

    def _exportar_vendas_csv(self) -> None:
        """Exporta o histórico de vendas para CSV."""
        caminho = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            initialfile=f"vendas_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            title="Guardar Relatório de Vendas",
        )
        if not caminho:
            return

        try:
            vendas = self._venda_svc.obter_todos()
            cabecalhos = [
                "ID", "Data/Hora", "Produto", "Quantidade",
                "Preço Unit. (AOA)", "Total (AOA)", "Operador", "Observações",
            ]
            with CSVWriter(caminho, cabecalhos) as writer:
                for v in vendas:
                    d = v.to_dict()
                    writer.write_row([
                        d["id"], d["data_venda"], d["produto_nome"],
                        d["quantidade"], d["preco_unitario"], d["total"],
                        d["vendido_por"], d["observacoes"],
                    ])

            messagebox.showinfo(
                "Exportação Concluída",
                f"Relatório de vendas exportado com sucesso!\n\n{caminho}",
                parent=self,
            )
        except Exception as e:
            messagebox.showerror("Erro na Exportação", str(e), parent=self)
