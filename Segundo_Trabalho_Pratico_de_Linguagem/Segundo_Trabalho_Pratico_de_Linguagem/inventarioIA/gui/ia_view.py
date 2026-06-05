"""
=============================================================================
Ficheiro: gui/ia_view.py
Descrição: Interface gráfica do módulo de Inteligência Artificial.
           Treino do modelo, visualização de previsões e métricas.
=============================================================================
"""

import logging
import threading
import customtkinter as ctk
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from services.ia_service import IAService
from services.venda_service import VendaService
from services.produto_service import ProdutoService
from config.settings import COLORS, FONTS, IA_FORECAST_MONTHS

logger = logging.getLogger(__name__)


class IAView(ctk.CTkFrame):
    """
    Módulo de Inteligência Artificial — Previsão de Demanda.

    Funcionalidades:
      - Selecção de produto para análise.
      - Botão para treinar/re-treinar o modelo.
      - Gráfico de histórico + linha de tendência + previsão futura.
      - Painel de métricas (R², MAE, RMSE).
      - Relatório textual detalhado.
    """

    def __init__(
        self,
        parent,
        ia_svc: IAService,
        venda_svc: VendaService,
        produto_svc: ProdutoService,
    ) -> None:
        super().__init__(parent, fg_color="transparent")
        self._ia_svc = ia_svc
        self._venda_svc = venda_svc
        self._produto_svc = produto_svc
        self._canvas_fig = None
        self._construir()

    # =================================================================
    # Construção
    # =================================================================

    def _construir(self) -> None:
        """Constrói a interface do módulo IA."""
        # ---- Painel de controlo superior ----
        frame_ctrl = ctk.CTkFrame(
            self, fg_color=COLORS["card_bg"], corner_radius=12
        )
        frame_ctrl.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            frame_ctrl,
            text="🤖  IA — Previsão de Demanda por Regressão Linear",
            font=FONTS["subtitle"],
        ).pack(side="left", padx=20, pady=16)

        # Selector de produto
        frame_seleccao = ctk.CTkFrame(frame_ctrl, fg_color="transparent")
        frame_seleccao.pack(side="right", padx=16, pady=12)

        ctk.CTkLabel(
            frame_seleccao, text="Produto:", font=FONTS["small"],
            text_color=COLORS["text_secondary"]
        ).pack(side="left", padx=(0, 6))

        produtos = self._produto_svc.obter_todos()
        self._lista_produtos = produtos
        nomes = [p.nome for p in produtos]

        self._combo_produto = ctk.CTkComboBox(
            frame_seleccao,
            values=nomes if nomes else ["Sem produtos"],
            width=220, height=40,
            font=FONTS["body"],
            corner_radius=8,
        )
        if nomes:
            self._combo_produto.set(nomes[0])
        self._combo_produto.pack(side="left", padx=6)

        self._btn_treinar = ctk.CTkButton(
            frame_seleccao,
            text="▶  Treinar Modelo",
            height=40, width=150,
            font=FONTS["body"],
            fg_color="#9b59b6",
            hover_color="#6c3483",
            corner_radius=10,
            command=self._iniciar_treino,
        )
        self._btn_treinar.pack(side="left", padx=6)

        # ---- Layout principal: gráfico | painel de métricas ----
        frame_main = ctk.CTkFrame(self, fg_color="transparent")
        frame_main.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # Gráfico (esquerda)
        self._frame_grafico = ctk.CTkFrame(
            frame_main, fg_color=COLORS["card_bg"], corner_radius=12
        )
        self._frame_grafico.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Painel direito
        frame_dir = ctk.CTkFrame(frame_main, fg_color="transparent", width=300)
        frame_dir.pack(side="right", fill="y")
        frame_dir.pack_propagate(False)

        self._frame_metricas = ctk.CTkFrame(
            frame_dir, fg_color=COLORS["card_bg"], corner_radius=12
        )
        self._frame_metricas.pack(fill="x", pady=(0, 10))
        self._construir_painel_metricas()

        # Relatório
        self._frame_relatorio = ctk.CTkFrame(
            frame_dir, fg_color=COLORS["card_bg"], corner_radius=12
        )
        self._frame_relatorio.pack(fill="both", expand=True)
        self._construir_painel_relatorio()

        # Estado inicial
        self._mostrar_grafico_vazio()

    def _construir_painel_metricas(self) -> None:
        """Constrói o painel de métricas do modelo."""
        ctk.CTkLabel(
            self._frame_metricas,
            text="📊  Métricas do Modelo",
            font=FONTS["body"],
            text_color=COLORS["text_primary"],
        ).pack(padx=16, pady=(14, 8), anchor="w")

        self._labels_metricas = {}
        metricas_info = [
            ("r2",        "R² (Precisão)",   "#9b59b6"),
            ("mae",       "MAE (Erro Médio)", COLORS["warning"]),
            ("rmse",      "RMSE",             COLORS["danger"]),
            ("coef",      "Tendência/Mês",    COLORS["success"]),
            ("n_amostras","Amostras",          COLORS["primary"]),
        ]
        for chave, titulo, cor in metricas_info:
            f = ctk.CTkFrame(self._frame_metricas, fg_color=COLORS["secondary"], corner_radius=8)
            f.pack(fill="x", padx=12, pady=3)
            ctk.CTkLabel(f, text=titulo, font=FONTS["small"],
                         text_color=COLORS["text_secondary"]).pack(side="left", padx=10, pady=8)
            lbl = ctk.CTkLabel(f, text="—", font=("Segoe UI", 12, "bold"), text_color=cor)
            lbl.pack(side="right", padx=10)
            self._labels_metricas[chave] = lbl

        ctk.CTkLabel(
            self._frame_metricas, text="",
            font=FONTS["small"]
        ).pack(pady=(0, 6))

    def _construir_painel_relatorio(self) -> None:
        """Constrói o painel do relatório textual."""
        ctk.CTkLabel(
            self._frame_relatorio,
            text="📋  Previsões",
            font=FONTS["body"],
        ).pack(padx=16, pady=(14, 6), anchor="w")

        self._text_relatorio = ctk.CTkTextbox(
            self._frame_relatorio,
            font=FONTS["mono"],
            fg_color=COLORS["secondary"],
            corner_radius=8,
            state="disabled",
        )
        self._text_relatorio.pack(
            fill="both", expand=True, padx=12, pady=(0, 12)
        )

    # =================================================================
    # Gráfico Matplotlib
    # =================================================================

    def _mostrar_grafico_vazio(self) -> None:
        """Exibe uma mensagem quando não há dados."""
        for w in self._frame_grafico.winfo_children():
            w.destroy()
        ctk.CTkLabel(
            self._frame_grafico,
            text=(
                "🤖  Nenhum modelo treinado.\n\n"
                "Seleccione um produto e clique em\n"
                "▶  Treinar Modelo"
            ),
            font=FONTS["subtitle"],
            text_color=COLORS["text_secondary"],
            justify="center",
        ).pack(expand=True)

    def _desenhar_grafico(self, dados: dict) -> None:
        """Desenha o gráfico de previsão com Matplotlib."""
        for w in self._frame_grafico.winfo_children():
            w.destroy()

        if not dados:
            self._mostrar_grafico_vazio()
            return

        labels_hist   = dados.get("labels_historico", [])
        vals_hist     = dados.get("valores_historico", [])
        labels_prev   = dados.get("labels_previsao", [])
        vals_prev     = dados.get("valores_previsao", [])
        linha_tend    = dados.get("linha_tendencia", [])

        nome_produto  = self._combo_produto.get()
        n_pontos      = dados.get("n_pontos", len(labels_hist))
        modo          = dados.get("modo", "linear")

        # Aviso sobre quantidade de dados
        if n_pontos == 1:
            aviso = " (1 ponto — previsão constante)"
        elif n_pontos == 2:
            aviso = " (2 pontos — tendência preliminar)"
        else:
            aviso = f" ({n_pontos} meses)"

        fig, ax = plt.subplots(figsize=(7, 4))
        fig.patch.set_facecolor("#2b2b2b")
        ax.set_facecolor("#2b2b2b")
        ax.tick_params(colors="white", labelsize=8)
        ax.spines[:].set_color("#444")

        # Histórico — barras azuis
        ax.bar(
            range(len(labels_hist)), vals_hist,
            color=COLORS["primary"], alpha=0.8, label="Histórico", width=0.5
        )

        # Linha de tendência
        if linha_tend:
            ax.plot(
                range(len(linha_tend)), linha_tend,
                color=COLORS["warning"], linewidth=2, linestyle="--",
                label="Tendência"
            )

        # Previsão — barras roxas
        offset = len(labels_hist)
        ax.bar(
            range(offset, offset + len(vals_prev)), vals_prev,
            color="#9b59b6", alpha=0.9, label="Previsão", width=0.5
        )

        # Linha vertical separadora
        if labels_hist and vals_prev:
            ax.axvline(x=offset - 0.5, color="#aaa", linestyle=":", linewidth=1.2)
            ax.text(
                offset - 0.4, max(vals_hist + vals_prev + [1]) * 0.95,
                "▶ Futuro", color="#aaa", fontsize=8
            )

        # Rótulos eixo X
        all_labels = labels_hist + labels_prev
        ax.set_xticks(range(len(all_labels)))
        ax.set_xticklabels(all_labels, rotation=45, ha="right", fontsize=8)

        ax.set_title(
            f"Previsão de Demanda — {nome_produto}{aviso}",
            color="white", fontsize=11, pad=10
        )
        ax.set_ylabel("Unidades Vendidas", color="#aaa", fontsize=9)
        ax.legend(
            facecolor="#2b2b2b", edgecolor="#444",
            labelcolor="white", fontsize=8
        )

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self._frame_grafico)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)
        self._canvas_fig = canvas
        plt.close(fig)

    # =================================================================
    # Treino e Actualização
    # =================================================================

    def _iniciar_treino(self) -> None:
        """Inicia o treino do modelo numa thread separada (não bloqueia a GUI)."""
        nome_produto = self._combo_produto.get()
        if not nome_produto or nome_produto == "Sem produtos":
            return

        produto = next(
            (p for p in self._lista_produtos if p.nome == nome_produto), None
        )
        if not produto:
            return

        # Feedback visual
        self._btn_treinar.configure(
            state="disabled", text="⏳  A treinar..."
        )
        for w in self._frame_grafico.winfo_children():
            w.destroy()
        ctk.CTkLabel(
            self._frame_grafico,
            text="⏳  A processar dados e treinar o modelo...\nAguarde.",
            font=FONTS["subtitle"],
            text_color=COLORS["text_secondary"],
        ).pack(expand=True)
        self.update()

        # Thread para não bloquear a GUI
        def _treinar():
            try:
                historico = self._venda_svc.obter_historico_mensal(str(produto.id))

                if len(historico) < 1:
                    self.after(0, self._sem_dados_suficientes)
                    return

                sucesso = self._ia_svc.treinar(historico)

                if sucesso:
                    dados_grafico = self._ia_svc.obter_dados_grafico(IA_FORECAST_MONTHS)
                    metricas = self._ia_svc.obter_metricas()
                    relatorio = self._ia_svc.gerar_relatorio_ia(produto.nome)
                    self.after(
                        0,
                        lambda: self._actualizar_interface(
                            dados_grafico, metricas, relatorio
                        ),
                    )
                else:
                    self.after(0, self._sem_dados_suficientes)

            except Exception as e:
                logger.error(f"Erro no treino IA: {e}")
                self.after(0, lambda: self._erro_treino(str(e)))

        threading.Thread(target=_treinar, daemon=True).start()

    def _actualizar_interface(
        self, dados_grafico: dict, metricas: dict, relatorio: str
    ) -> None:
        """Actualiza todos os painéis após o treino."""
        # Gráfico
        self._desenhar_grafico(dados_grafico)

        # Métricas
        mapa = {
            "r2":        f"{metricas.get('r2', 0):.4f}",
            "mae":       f"{metricas.get('mae', 0):.2f} un.",
            "rmse":      f"{metricas.get('rmse', 0):.2f} un.",
            "coef":      f"{metricas.get('coef', 0):+.2f} un./mês",
            "n_amostras":f"{int(metricas.get('n_amostras', 0))} meses",
        }
        for chave, valor in mapa.items():
            if chave in self._labels_metricas:
                self._labels_metricas[chave].configure(text=valor)

        # Relatório textual
        self._text_relatorio.configure(state="normal")
        self._text_relatorio.delete("1.0", "end")
        self._text_relatorio.insert("1.0", relatorio)
        self._text_relatorio.configure(state="disabled")

        # Reabilita botão
        self._btn_treinar.configure(state="normal", text="🔁  Re-treinar")

    def _sem_dados_suficientes(self) -> None:
        """Informa que não há nenhum dado de vendas."""
        for w in self._frame_grafico.winfo_children():
            w.destroy()
        ctk.CTkLabel(
            self._frame_grafico,
            text=(
                "⚠️  Nenhuma venda registada para este produto.\n\n"
                "Registe pelo menos 1 venda e clique em\n"
                "▶  Treinar Modelo"
            ),
            font=FONTS["subtitle"],
            text_color=COLORS["warning"],
            justify="center",
        ).pack(expand=True)
        self._btn_treinar.configure(state="normal", text="▶  Treinar Modelo")

    def _erro_treino(self, erro: str) -> None:
        """Exibe mensagem de erro no treino."""
        for w in self._frame_grafico.winfo_children():
            w.destroy()
        ctk.CTkLabel(
            self._frame_grafico,
            text=f"❌  Erro ao treinar o modelo:\n{erro}",
            font=FONTS["body"],
            text_color=COLORS["danger"],
        ).pack(expand=True)
        self._btn_treinar.configure(state="normal", text="▶  Treinar Modelo")
