"""
=============================================================================
Ficheiro: services/ia_service.py
Descrição: Serviço de Inteligência Artificial para previsão de demanda.
           Funciona com QUALQUER quantidade de dados históricos:
             - 1 ponto  → previsão constante (sem tendência)
             - 2 pontos → regressão linear directa
             - 3+       → regressão linear com métricas completas

POO:
  - Implementa IIAService (interface abstracta).
  - Decoradores: @log_execution, @timer.
  - Encapsulamento: modelo e dados internos protegidos.
=============================================================================
"""

import os
import pickle
import logging
import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from interfaces.repository_interface import IIAService
from config.settings import IA_FORECAST_MONTHS, MODEL_SAVE_PATH
from utils.decorators import log_execution, timer

logger = logging.getLogger(__name__)

# Mínimo absoluto de pontos para treinar (1 é suficiente)
MIN_PONTOS = 1


class IAService(IIAService):
    """
    Serviço de IA com Regressão Linear adaptativa.
    Funciona com 1 ou mais meses de histórico de vendas.

    Estratégias por quantidade de dados:
      1 ponto  → valor constante (sem inclinação)
      2 pontos → regressão linear simples (2 pontos definem uma recta)
      3+       → regressão linear com métricas completas (R², MAE, RMSE)
    """

    def __init__(self) -> None:
        self._modelo: Optional[LinearRegression] = None
        self._dados_treino: Optional[Tuple[np.ndarray, np.ndarray]] = None
        self._metricas: Dict[str, float] = {}
        self._historico_original: List[Dict] = []
        self._ultimo_indice: int = 0
        self._modo: str = "nenhum"   # "constante" | "linear_2pts" | "linear"

        logger.info("IAService inicializado.")

    # =================================================================
    # Interface IIAService
    # =================================================================

    @log_execution
    @timer
    def treinar(self, historico: List[Dict]) -> bool:
        """
        Treina o modelo com o histórico fornecido.
        Aceita desde 1 único mês de dados.

        Parâmetros:
            historico: Lista de dicts com 'total_vendido'
                       (e opcionalmente 'mes', 'ano').

        Returns:
            bool: True se treino bem-sucedido.
        """
        if not historico:
            logger.warning("Histórico vazio — impossível treinar.")
            return False

        try:
            self._historico_original = historico
            quantidades = [max(0.0, float(h["total_vendido"])) for h in historico]
            n = len(quantidades)
            self._ultimo_indice = n

            # ── Caso especial: 1 único ponto ──────────────────────
            if n == 1:
                self._modo = "constante"
                logger.info("Modo CONSTANTE (1 ponto). Previsão = valor actual.")
                self._modelo = None   # Não usa sklearn
                self._dados_treino = (
                    np.array([[1]]),
                    np.array(quantidades),
                )
                self._metricas = {
                    "r2": 1.0,
                    "mae": 0.0,
                    "rmse": 0.0,
                    "coef": 0.0,
                    "intercept": quantidades[0],
                    "n_amostras": 1,
                }
                self._guardar_modelo()
                return True

            # ── 2 ou mais pontos: Regressão Linear ────────────────
            X = np.array(range(1, n + 1)).reshape(-1, 1)
            y = np.array(quantidades)

            self._modelo = LinearRegression()
            self._modelo.fit(X, y)
            self._dados_treino = (X, y)

            if n == 2:
                self._modo = "linear_2pts"
                # Com 2 pontos r2_score não funciona (divisão por zero)
                y_pred = self._modelo.predict(X)
                mae  = float(mean_absolute_error(y, y_pred))
                rmse = float(np.sqrt(mean_squared_error(y, y_pred)))
                self._metricas = {
                    "r2": 1.0,       # 2 pontos → ajuste perfeito por definição
                    "mae": round(mae, 4),
                    "rmse": round(rmse, 4),
                    "coef": round(float(self._modelo.coef_[0]), 4),
                    "intercept": round(float(self._modelo.intercept_), 4),
                    "n_amostras": 2,
                }
            else:
                self._modo = "linear"
                self._calcular_metricas(X, y)

            self._guardar_modelo()
            logger.info(
                f"Modelo treinado ({self._modo}) com {n} ponto(s). "
                f"R²={self._metricas.get('r2', '—')}"
            )
            return True

        except Exception as e:
            logger.error(f"Erro ao treinar modelo: {e}")
            return False

    def prever(self, n_periodos: int = IA_FORECAST_MONTHS) -> List[float]:
        """
        Gera previsões para os próximos N períodos.
        Funciona com qualquer modo (constante ou linear).

        Returns:
            Lista de floats com as previsões (sempre >= 0).
        """
        if not self.modelo_treinado():
            logger.warning("Modelo não treinado.")
            return []

        try:
            # Modo constante (1 ponto): repete o valor do único ponto
            if self._modo == "constante":
                valor = float(self._historico_original[0]["total_vendido"])
                return [max(0.0, round(valor, 1))] * n_periodos

            # Modo linear (2+ pontos)
            indices_futuros = np.array(
                range(self._ultimo_indice + 1,
                      self._ultimo_indice + n_periodos + 1)
            ).reshape(-1, 1)

            previsoes = self._modelo.predict(indices_futuros)
            return [max(0.0, round(float(p), 1)) for p in previsoes]

        except Exception as e:
            logger.error(f"Erro ao prever: {e}")
            return []

    def obter_metricas(self) -> Dict[str, float]:
        return self._metricas.copy()

    def modelo_treinado(self) -> bool:
        """True se o modelo foi treinado (modo constante ou linear)."""
        return (
            self._dados_treino is not None
            and len(self._historico_original) >= MIN_PONTOS
        )

    # =================================================================
    # Auxiliares privados
    # =================================================================

    def _calcular_metricas(self, X: np.ndarray, y: np.ndarray) -> None:
        """Calcula R², MAE, RMSE para 3+ pontos."""
        if self._modelo is None:
            return
        y_pred = self._modelo.predict(X)
        r2   = r2_score(y, y_pred)
        mae  = mean_absolute_error(y, y_pred)
        rmse = float(np.sqrt(mean_squared_error(y, y_pred)))
        self._metricas = {
            "r2":        round(r2, 4),
            "mae":       round(mae, 4),
            "rmse":      round(rmse, 4),
            "coef":      round(float(self._modelo.coef_[0]), 4),
            "intercept": round(float(self._modelo.intercept_), 4),
            "n_amostras": len(y),
        }
        logger.info(f"Métricas → R²={r2:.4f} | MAE={mae:.4f} | RMSE={rmse:.4f}")

    def _guardar_modelo(self) -> None:
        """Persiste o estado do modelo em disco (pickle)."""
        try:
            os.makedirs(
                os.path.dirname(MODEL_SAVE_PATH)
                if os.path.dirname(MODEL_SAVE_PATH) else ".",
                exist_ok=True,
            )
            dados = {
                "modelo":           self._modelo,
                "ultimo_indice":    self._ultimo_indice,
                "metricas":         self._metricas,
                "historico":        self._historico_original,
                "modo":             self._modo,
                "treinado_em":      datetime.utcnow().isoformat(),
            }
            with open(MODEL_SAVE_PATH, "wb") as f:
                pickle.dump(dados, f)
            logger.info(f"Modelo guardado: {MODEL_SAVE_PATH}")
        except Exception as e:
            logger.warning(f"Não foi possível guardar o modelo: {e}")

    def carregar_modelo(self) -> bool:
        """Carrega modelo previamente guardado em disco."""
        try:
            if not os.path.exists(MODEL_SAVE_PATH):
                return False
            with open(MODEL_SAVE_PATH, "rb") as f:
                dados = pickle.load(f)
            self._modelo             = dados.get("modelo")
            self._ultimo_indice      = dados.get("ultimo_indice", 0)
            self._metricas           = dados.get("metricas", {})
            self._historico_original = dados.get("historico", [])
            self._modo               = dados.get("modo", "linear")
            logger.info(
                f"Modelo carregado ({self._modo}). "
                f"Treinado em: {dados.get('treinado_em', '—')}"
            )
            return True
        except Exception as e:
            logger.warning(f"Não foi possível carregar modelo: {e}")
            return False

    # =================================================================
    # Dados para o gráfico
    # =================================================================

    def obter_dados_grafico(self, n_previsoes: int = IA_FORECAST_MONTHS) -> Dict:
        """Prepara dados formatados para o gráfico da GUI."""
        if not self.modelo_treinado():
            return {}

        historico = self._historico_original
        n = len(historico)

        labels_hist = [
            f"{h.get('mes', i+1):02d}/{h.get('ano', datetime.now().year)}"
            for i, h in enumerate(historico)
        ]
        valores_hist = [float(h["total_vendido"]) for h in historico]

        # Linha de tendência sobre o histórico
        if self._modo == "constante":
            linha_tendencia = valores_hist[:]
        else:
            X_hist = np.array(range(1, n + 1)).reshape(-1, 1)
            linha_tendencia = [
                max(0.0, round(float(v), 1))
                for v in self._modelo.predict(X_hist)
            ]

        previsoes = self.prever(n_previsoes)

        # Etiquetas dos meses futuros
        ultimo = historico[-1] if historico else {}
        ano_atual = ultimo.get("ano", datetime.now().year)
        mes_atual = ultimo.get("mes", datetime.now().month)
        labels_prev = []
        for i in range(1, n_previsoes + 1):
            mes_fut = (mes_atual - 1 + i) % 12 + 1
            ano_fut = ano_atual + (mes_atual - 1 + i) // 12
            labels_prev.append(f"{mes_fut:02d}/{ano_fut}")

        return {
            "labels_historico":  labels_hist,
            "valores_historico": valores_hist,
            "labels_previsao":   labels_prev,
            "valores_previsao":  previsoes,
            "linha_tendencia":   linha_tendencia,
            "metricas":          self._metricas,
            "modo":              self._modo,
            "n_pontos":          n,
        }

    # =================================================================
    # Relatório textual
    # =================================================================

    def gerar_relatorio_ia(self, produto_nome: str = "") -> str:
        """Gera relatório textual do modelo e previsões."""
        if not self.modelo_treinado():
            return "Modelo não treinado. Execute o treino primeiro."

        m = self._metricas
        previsoes = self.prever(IA_FORECAST_MONTHS)
        titulo = f"Produto: {produto_nome}" if produto_nome else "Análise Global"
        n = m.get("n_amostras", 0)

        # Aviso sobre quantidade de dados
        if n == 1:
            aviso_dados = "  ⚠  Apenas 1 mês de dados — previsão constante."
        elif n == 2:
            aviso_dados = "  ⚠  Apenas 2 meses de dados — tendência preliminar."
        else:
            aviso_dados = f"  ✓  {n} meses de dados — tendência confiável."

        linhas = [
            "=" * 55,
            "  RELATÓRIO DE PREVISÃO DE DEMANDA — IA",
            f"  {titulo}",
            "=" * 55,
            "",
            aviso_dados,
            "",
            "  MÉTRICAS DO MODELO",
            f"  ├─ Modo:          {self._modo.replace('_', ' ').upper()}",
            f"  ├─ R²:            {m.get('r2', 0):.4f}",
            f"  ├─ MAE:           {m.get('mae', 0):.2f} unidades",
            f"  ├─ RMSE:          {m.get('rmse', 0):.2f} unidades",
            f"  ├─ Tendência/mês: {m.get('coef', 0):+.2f} unidades",
            f"  └─ Amostras:      {n} mês(es)",
            "",
            f"  PREVISÃO — PRÓXIMOS {IA_FORECAST_MONTHS} MÊS(ES):",
        ]

        for i, prev in enumerate(previsoes, 1):
            linhas.append(f"  ├─ Período +{i}:  {prev:.0f} unidades")

        tendencia = m.get("coef", 0)
        if self._modo == "constante":
            dir_tendencia = "→ Sem dados suficientes para calcular tendência"
        elif tendencia > 0.5:
            dir_tendencia = f"↑ Crescimento ~{tendencia:.1f} un./mês"
        elif tendencia < -0.5:
            dir_tendencia = f"↓ Decréscimo ~{abs(tendencia):.1f} un./mês"
        else:
            dir_tendencia = "→ Estável"

        linhas += [
            "",
            f"  TENDÊNCIA: {dir_tendencia}",
            "",
            f"  Gerado: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            "=" * 55,
        ]

        return "\n".join(linhas)

    def __repr__(self) -> str:
        return (
            f"IAService(modo='{self._modo}', "
            f"treinado={self.modelo_treinado()}, "
            f"r2={self._metricas.get('r2', 'N/A')})"
        )
