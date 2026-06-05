"""
=============================================================================
Ficheiro: gui/admin_panel.py
Descrição: Painel exclusivo do administrador com visão global do sistema,
           estatísticas avançadas e operações administrativas.
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

from services.auth_service import AuthService
from services.produto_service import ProdutoService
from services.venda_service import VendaService
from models.usuario import Usuario
from models.produto import Produto
from models.venda import Venda
from config.settings import COLORS, FONTS

logger = logging.getLogger(__name__)


class AdminPanel(ctk.CTkFrame):
    """
    Painel de administração — exclusivo para o papel Admin.

    Secções:
      - Resumo global do sistema (utilizadores, produtos, vendas)
      - Gráfico de actividade por operador
      - Operações de manutenção (limpar logs, backup, etc.)
      - Lista de actividade recente
    """

    def __init__(self, parent, auth_svc: AuthService,
                 produto_svc: ProdutoService, venda_svc: VendaService) -> None:
        super().__init__(parent, fg_color="transparent")
        self._auth        = auth_svc
        self._produto_svc = produto_svc
        self._venda_svc   = venda_svc
        self._construir()

    def _construir(self) -> None:
        # ── Cabeçalho ──────────────────────────────────────────────
        frame_h = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=12)
        frame_h.pack(fill="x", padx=20, pady=(20, 10))
        ctk.CTkLabel(frame_h, text="⚙️  Painel de Administração",
                     font=FONTS["subtitle"]).pack(side="left", padx=20, pady=14)
        ctk.CTkLabel(frame_h,
                     text=f"Sessão: {self._auth.current_user.username if self._auth.current_user else '—'}  |  "
                          f"{datetime.now().strftime('%d/%m/%Y %H:%M')}",
                     font=FONTS["small"],
                     text_color=COLORS["text_secondary"]).pack(side="right", padx=20)

        # ── KPIs do Sistema ─────────────────────────────────────────
        frame_kpis = ctk.CTkFrame(self, fg_color="transparent")
        frame_kpis.pack(fill="x", padx=20, pady=(0, 10))
        self._construir_kpis(frame_kpis)

        # ── Layout principal ────────────────────────────────────────
        frame_main = ctk.CTkFrame(self, fg_color="transparent")
        frame_main.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Coluna esquerda
        frame_esq = ctk.CTkFrame(frame_main, fg_color="transparent")
        frame_esq.pack(side="left", fill="both", expand=True, padx=(0, 10))

        frame_grafico = ctk.CTkFrame(frame_esq, fg_color=COLORS["card_bg"], corner_radius=12)
        frame_grafico.pack(fill="both", expand=True, pady=(0, 10))
        self._construir_grafico_operadores(frame_grafico)

        frame_manutencao = ctk.CTkFrame(frame_esq, fg_color=COLORS["card_bg"], corner_radius=12)
        frame_manutencao.pack(fill="x")
        self._construir_manutencao(frame_manutencao)

        # Coluna direita
        frame_dir = ctk.CTkFrame(frame_main, fg_color=COLORS["card_bg"],
                                 corner_radius=12, width=320)
        frame_dir.pack(side="right", fill="y")
        frame_dir.pack_propagate(False)
        self._construir_actividade_recente(frame_dir)

    # =================================================================
    # KPIs
    # =================================================================

    def _construir_kpis(self, parent) -> None:
        try:
            n_users    = Usuario.objects().count()
            n_admins   = Usuario.objects(role="admin").count()
            n_bloq     = sum(1 for u in Usuario.objects() if u.is_bloqueado())
            n_produtos = Produto.objects(ativo=True).count()
            n_vendas   = Venda.objects().count()
            stats_v    = self._venda_svc.obter_estatisticas_gerais()
        except Exception:
            n_users = n_admins = n_bloq = n_produtos = n_vendas = 0
            stats_v = {}

        kpis = [
            ("👥", "Utilizadores",  str(n_users),   f"{n_admins} admin(s)", COLORS["primary"]),
            ("🔒", "Bloqueados",    str(n_bloq),     "contas bloqueadas",   COLORS["danger"]),
            ("📦", "Produtos",      str(n_produtos), "produtos activos",    COLORS["success"]),
            ("🛒", "Total Vendas",  str(n_vendas),   "desde o início",      COLORS["warning"]),
            ("💰", "Receita",       f"{stats_v.get('receita_total', 0):,.0f}", "AOA total", "#9b59b6"),
        ]

        for icone, titulo, valor, sub, cor in kpis:
            card = ctk.CTkFrame(parent, fg_color=COLORS["card_bg"], corner_radius=12)
            card.pack(side="left", fill="both", expand=True, padx=6)
            ctk.CTkFrame(card, height=4, fg_color=cor, corner_radius=2).pack(fill="x")
            ctk.CTkLabel(card, text=icone, font=("Segoe UI", 28)).pack(pady=(10, 2))
            ctk.CTkLabel(card, text=titulo, font=FONTS["small"],
                         text_color=COLORS["text_secondary"]).pack()
            ctk.CTkLabel(card, text=valor, font=("Segoe UI", 22, "bold"),
                         text_color=cor).pack(pady=(2, 2))
            ctk.CTkLabel(card, text=sub, font=FONTS["small"],
                         text_color=COLORS["text_secondary"]).pack(pady=(0, 12))

    # =================================================================
    # Gráfico de vendas por operador
    # =================================================================

    def _construir_grafico_operadores(self, parent) -> None:
        ctk.CTkLabel(parent, text="📈  Vendas por Operador",
                     font=FONTS["body"]).pack(padx=16, pady=(14, 6), anchor="w")
        try:
            vendas = list(Venda.objects())
            if not vendas:
                ctk.CTkLabel(parent, text="Sem dados de vendas ainda.",
                             font=FONTS["body"], text_color=COLORS["text_secondary"]
                             ).pack(expand=True, pady=40)
                return

            contagem: dict = {}
            for v in vendas:
                op = v.vendido_por or "sistema"
                contagem[op] = contagem.get(op, 0) + v.total

            operadores = list(contagem.keys())
            totais     = [contagem[o] for o in operadores]

            fig, ax = plt.subplots(figsize=(5.5, 3))
            fig.patch.set_facecolor("#2b2b2b")
            ax.set_facecolor("#2b2b2b")

            cores = [COLORS["primary"], COLORS["success"], COLORS["warning"],
                     COLORS["danger"], "#9b59b6", "#1abc9c"]
            bars = ax.bar(operadores, totais,
                          color=cores[:len(operadores)], width=0.5, edgecolor="none")
            for bar, val in zip(bars, totais):
                ax.text(bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + max(totais) * 0.02,
                        f"{val:,.0f}", ha="center", color="white", fontsize=8)

            ax.tick_params(colors="white", labelsize=9)
            ax.spines[:].set_color("#444")
            ax.set_ylabel("Receita (AOA)", color="#aaa", fontsize=8)
            plt.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 12))
            plt.close(fig)

        except Exception as e:
            ctk.CTkLabel(parent, text=f"Erro: {e}",
                         text_color=COLORS["danger"]).pack(pady=20)

    # =================================================================
    # Manutenção
    # =================================================================

    def _construir_manutencao(self, parent) -> None:
        ctk.CTkLabel(parent, text="🛠  Manutenção do Sistema",
                     font=FONTS["body"]).pack(padx=16, pady=(14, 8), anchor="w")

        frame_btns = ctk.CTkFrame(parent, fg_color="transparent")
        frame_btns.pack(fill="x", padx=12, pady=(0, 14))

        acoes = [
            ("🗑  Limpar Logs",          self._limpar_logs,            COLORS["secondary"]),
            ("📥  Exportar Tudo (CSV)",  self._exportar_tudo,          COLORS["primary"]),
            ("🔄  Actualizar Dados",     self._actualizar_dados,       COLORS["success"]),
            ("⚠️  Limpar Modelo IA",     self._limpar_modelo_ia,       COLORS["warning"]),
        ]

        for i, (texto, cmd, cor) in enumerate(acoes):
            ctk.CTkButton(
                frame_btns, text=texto,
                height=36, font=FONTS["small"],
                fg_color=cor, hover_color="#3a3a3a" if cor == COLORS["secondary"] else cor,
                corner_radius=8, command=cmd,
            ).grid(row=i // 2, column=i % 2, padx=6, pady=4, sticky="ew")

        frame_btns.columnconfigure(0, weight=1)
        frame_btns.columnconfigure(1, weight=1)

    # =================================================================
    # Actividade recente
    # =================================================================

    def _construir_actividade_recente(self, parent) -> None:
        ctk.CTkLabel(parent, text="🕐  Actividade Recente",
                     font=FONTS["body"]).pack(padx=16, pady=(14, 6), anchor="w")
        try:
            vendas_recentes = list(Venda.objects().order_by("-data_venda").limit(15))
            if not vendas_recentes:
                ctk.CTkLabel(parent, text="Sem actividade recente.",
                             font=FONTS["small"],
                             text_color=COLORS["text_secondary"]).pack(pady=30)
                return

            frame_scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
            frame_scroll.pack(fill="both", expand=True, padx=8, pady=(0, 10))

            for v in vendas_recentes:
                f = ctk.CTkFrame(frame_scroll, fg_color=COLORS["secondary"], corner_radius=8)
                f.pack(fill="x", pady=2)
                ctk.CTkLabel(f,
                             text=f"🛒  {v.vendido_por}",
                             font=("Segoe UI", 11, "bold"),
                             text_color=COLORS["primary"]).pack(side="left", padx=10, pady=6)
                ctk.CTkLabel(f,
                             text=f"{v.nome_produto[:18]}  |  {v.total:,.0f} AOA",
                             font=FONTS["small"],
                             text_color=COLORS["text_secondary"]).pack(side="left")
                ctk.CTkLabel(f,
                             text=v.data_venda.strftime("%d/%m %H:%M"),
                             font=("Segoe UI", 10),
                             text_color=COLORS["text_secondary"]).pack(side="right", padx=10)
        except Exception as e:
            ctk.CTkLabel(parent, text=f"Erro: {e}",
                         text_color=COLORS["danger"]).pack(pady=20)

    # =================================================================
    # Acções de manutenção
    # =================================================================

    def _limpar_logs(self) -> None:
        if not messagebox.askyesno("Limpar Logs",
                                   "Eliminar todos os ficheiros de log?\n"
                                   "Esta acção não pode ser desfeita.", parent=self):
            return
        try:
            import glob
            logs = glob.glob("logs/*.log")
            for f in logs:
                open(f, "w").close()
            messagebox.showinfo("Concluído",
                                f"{len(logs)} ficheiro(s) de log limpos.", parent=self)
        except Exception as e:
            messagebox.showerror("Erro", str(e), parent=self)

    def _exportar_tudo(self) -> None:
        caminho = filedialog.askdirectory(title="Seleccionar pasta de destino")
        if not caminho:
            return
        from utils.context_manager import CSVWriter
        ts = datetime.now().strftime("%Y%m%d_%H%M")
        try:
            # Produtos
            produtos = self._produto_svc.obter_todos()
            with CSVWriter(os.path.join(caminho, f"produtos_{ts}.csv"),
                           ["ID","Nome","Categoria","Preço","Stock","Estado"]) as w:
                for p in produtos:
                    w.write_row([str(p.id), p.nome, p.categoria,
                                 p.preco, p.stock, p.estado_stock])
            # Vendas
            vendas = self._venda_svc.obter_todos()
            with CSVWriter(os.path.join(caminho, f"vendas_{ts}.csv"),
                           ["ID","Data","Produto","Qtd","Total","Operador"]) as w:
                for v in vendas:
                    w.write_row([str(v.id), v.data_formatada, v.nome_produto,
                                 v.quantidade, v.total, v.vendido_por])
            # Utilizadores
            users = list(Usuario.objects())
            with CSVWriter(os.path.join(caminho, f"utilizadores_{ts}.csv"),
                           ["Username","Nome","Papel","Activo","Criado Em"]) as w:
                for u in users:
                    w.write_row([u.username, u.nome_completo, u.role,
                                 u.ativo, u.criado_em.strftime("%d/%m/%Y") if u.criado_em else ""])

            messagebox.showinfo("Exportação Completa",
                                f"3 ficheiros CSV exportados para:\n{caminho}", parent=self)
        except Exception as e:
            messagebox.showerror("Erro", str(e), parent=self)

    def _actualizar_dados(self) -> None:
        # Limpa cache dos serviços
        try:
            if hasattr(self._produto_svc.obter_estatisticas, "clear_cache"):
                self._produto_svc.obter_estatisticas.clear_cache()
            messagebox.showinfo("Actualizado",
                                "Cache limpa. Os dados serão recarregados.", parent=self)
        except Exception as e:
            messagebox.showinfo("Actualizado", "Dados actualizados.", parent=self)

    def _limpar_modelo_ia(self) -> None:
        from config.settings import MODEL_SAVE_PATH
        if not messagebox.askyesno("Limpar Modelo IA",
                                   "Eliminar o modelo IA treinado?\n"
                                   "Terá de re-treinar o modelo.", parent=self):
            return
        try:
            if os.path.exists(MODEL_SAVE_PATH):
                os.remove(MODEL_SAVE_PATH)
                messagebox.showinfo("Concluído",
                                    "Modelo IA eliminado com sucesso.", parent=self)
            else:
                messagebox.showinfo("Info", "Nenhum modelo guardado encontrado.", parent=self)
        except Exception as e:
            messagebox.showerror("Erro", str(e), parent=self)
