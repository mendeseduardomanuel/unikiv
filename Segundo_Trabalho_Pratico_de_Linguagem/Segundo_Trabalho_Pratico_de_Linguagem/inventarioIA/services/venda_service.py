"""
=============================================================================
Ficheiro: services/venda_service.py
Descrição: Serviço de negócio para gestão de vendas.
           Coordena o registo de vendas e actualização automática de stock.

POO:
  - Implementa IVendaRepository.
  - Context Manager: DatabaseTransaction para atomicidade.
  - Decoradores: @log_execution, @validate_positive.
=============================================================================
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from interfaces.repository_interface import IVendaRepository
from models.venda import Venda
from models.produto import Produto
from services.produto_service import ProdutoService
from exceptions.stock_exception import (
    ProductNotFoundException,
    InsufficientStockException,
)
from utils.decorators import log_execution, validate_positive
from utils.context_manager import DatabaseTransaction

logger = logging.getLogger(__name__)


class VendaService(IVendaRepository):
    """
    Serviço de vendas que implementa IVendaRepository.

    POO:
      - Herança: implementa IVendaRepository.
      - Composição: usa ProdutoService (não herda).
      - Context Manager: transacções atómicas.

    Responsabilidades:
      - Registar vendas.
      - Decrementar stock automaticamente.
      - Consultar histórico e estatísticas.
    """

    def __init__(self, produto_service: ProdutoService) -> None:
        """
        Parâmetros:
            produto_service: Injecção de dependência do serviço de produtos.
        """
        self._produto_service = produto_service
        logger.info("VendaService inicializado.")

    # =================================================================
    # Operação Principal: Registar Venda
    # =================================================================

    @log_execution
    @validate_positive("quantidade")
    def registrar_venda(
        self,
        produto_id: str,
        quantidade: int,
        vendido_por: str = "sistema",
        observacoes: str = "",
    ) -> Venda:
        """
        Regista uma venda e actualiza o stock do produto automaticamente.
        Utiliza um Context Manager para garantir atomicidade.

        Parâmetros:
            produto_id  : ID do produto a vender.
            quantidade  : Número de unidades.
            vendido_por : Username do operador.
            observacoes : Notas opcionais.

        Returns:
            Venda: Registo da venda criado.

        Raises:
            ProductNotFoundException   : Se o produto não existir.
            InsufficientStockException : Se o stock for insuficiente.
        """
        # Obtém o produto
        produto = self._produto_service.obter_por_id(produto_id)
        if not produto:
            raise ProductNotFoundException(product_id=produto_id)

        # Verifica stock antes de iniciar a transacção
        if produto.stock < quantidade:
            raise InsufficientStockException(
                product_name=produto.nome,
                requested=quantidade,
                available=produto.stock,
            )

        # Usa Context Manager para garantir que ambas as operações
        # (decrementar stock + registar venda) são atómicas
        with DatabaseTransaction(
            f"Registar venda: {quantidade}x {produto.nome}"
        ) as txn:
            # 1. Decrementa o stock
            produto.decrementar_stock(quantidade)
            txn.log_operation(
                f"Stock de '{produto.nome}': -{quantidade} → {produto.stock}"
            )

            # 2. Cria o registo de venda
            venda = Venda.criar_venda(
                produto=produto,
                quantidade=quantidade,
                vendido_por=vendido_por,
                observacoes=observacoes,
            )
            txn.log_operation(f"Venda ID: {venda.id}")

            txn.commit()

        logger.info(
            f"Venda concluída: {quantidade}x '{produto.nome}' "
            f"| Total: {venda.total:.2f} | Por: {vendido_por}"
        )
        return venda

    # =================================================================
    # Implementação da Interface IVendaRepository
    # =================================================================

    @log_execution
    def criar(self, dados: Dict[str, Any]) -> Venda:
        """Cria uma venda a partir de um dicionário (wrapper de registar_venda)."""
        return self.registrar_venda(
            produto_id=dados["produto_id"],
            quantidade=int(dados["quantidade"]),
            vendido_por=dados.get("vendido_por", "sistema"),
            observacoes=dados.get("observacoes", ""),
        )

    @log_execution
    def obter_por_id(self, entity_id: str) -> Optional[Venda]:
        """Obtém uma venda pelo ID."""
        try:
            return Venda.objects(id=entity_id).first()
        except Exception as e:
            logger.error(f"Erro ao obter venda '{entity_id}': {e}")
            return None

    @log_execution
    def obter_todos(self) -> List[Venda]:
        """Obtém todas as vendas ordenadas pela mais recente."""
        try:
            return list(Venda.objects().order_by("-data_venda"))
        except Exception as e:
            logger.error(f"Erro ao obter todas as vendas: {e}")
            return []

    @log_execution
    def actualizar(
        self, entity_id: str, dados: Dict[str, Any]
    ) -> Optional[Venda]:
        """
        Actualiza as observações de uma venda (único campo editável).
        O histórico financeiro é imutável.
        """
        venda = self.obter_por_id(entity_id)
        if not venda:
            return None
        if "observacoes" in dados:
            venda.observacoes = dados["observacoes"]
            venda.save()
        return venda

    @log_execution
    def eliminar(self, entity_id: str) -> bool:
        """Elimina um registo de venda (uso restrito - apenas admin)."""
        venda = self.obter_por_id(entity_id)
        if not venda:
            return False
        venda.delete()
        logger.warning(f"Venda {entity_id} eliminada.")
        return True

    @log_execution
    def pesquisar(self, filtros: Dict[str, Any]) -> List[Venda]:
        """Pesquisa vendas com filtros (produto, data, utilizador)."""
        try:
            query = Venda.objects()

            if "produto_id" in filtros and filtros["produto_id"]:
                query = query.filter(produto=filtros["produto_id"])

            if "vendido_por" in filtros and filtros["vendido_por"]:
                query = query.filter(vendido_por__icontains=filtros["vendido_por"])

            if "data_inicio" in filtros and filtros["data_inicio"]:
                query = query.filter(data_venda__gte=filtros["data_inicio"])

            if "data_fim" in filtros and filtros["data_fim"]:
                query = query.filter(data_venda__lte=filtros["data_fim"])

            return list(query.order_by("-data_venda"))

        except Exception as e:
            logger.error(f"Erro ao pesquisar vendas: {e}")
            return []

    @log_execution
    def obter_por_produto(self, produto_id: str) -> List[Venda]:
        """Obtém todas as vendas de um produto específico."""
        try:
            produto = Produto.objects(id=produto_id).first()
            if not produto:
                return []
            return list(Venda.objects(produto=produto).order_by("-data_venda"))
        except Exception as e:
            logger.error(f"Erro ao obter vendas do produto '{produto_id}': {e}")
            return []

    @log_execution
    def obter_por_periodo(
        self, data_inicio: datetime, data_fim: datetime
    ) -> List[Venda]:
        """Obtém vendas num intervalo de datas."""
        try:
            return list(
                Venda.objects(
                    data_venda__gte=data_inicio,
                    data_venda__lte=data_fim,
                ).order_by("-data_venda")
            )
        except Exception as e:
            logger.error(f"Erro ao obter vendas por período: {e}")
            return []

    @log_execution
    def obter_historico_mensal(self, produto_id: str) -> List[Dict]:
        """
        Obtém o histórico de vendas mensais de um produto para alimentar a IA.
        Agrega as vendas por mês/ano.

        Parâmetros:
            produto_id: ID do produto.

        Returns:
            Lista de dicts com 'mes', 'ano', 'total_vendido', 'receita'.
            Ordenada por data crescente.
        """
        vendas = self.obter_por_produto(produto_id)
        if not vendas:
            return []

        # Agrega por mês e ano
        historico: Dict[tuple, Dict] = {}

        for venda in vendas:
            chave = (venda.data_venda.year, venda.data_venda.month)
            if chave not in historico:
                historico[chave] = {
                    "ano": venda.data_venda.year,
                    "mes": venda.data_venda.month,
                    "total_vendido": 0,
                    "receita": 0.0,
                    "num_transacoes": 0,
                }
            historico[chave]["total_vendido"] += venda.quantidade
            historico[chave]["receita"] += venda.total
            historico[chave]["num_transacoes"] += 1

        # Ordena por data crescente
        resultado = sorted(historico.values(), key=lambda x: (x["ano"], x["mes"]))
        return resultado

    # =================================================================
    # Estatísticas para Dashboard e Relatórios
    # =================================================================

    def obter_estatisticas_gerais(self) -> Dict[str, Any]:
        """
        Calcula estatísticas globais de vendas para o Dashboard.

        Returns:
            dict com: total_vendas, receita_total, media_diaria,
                      produto_mais_vendido, vendas_hoje, vendas_mes.
        """
        try:
            agora = datetime.utcnow()
            inicio_hoje = agora.replace(hour=0, minute=0, second=0, microsecond=0)
            inicio_mes = agora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

            todas = list(Venda.objects())
            vendas_hoje = list(Venda.objects(data_venda__gte=inicio_hoje))
            vendas_mes = list(Venda.objects(data_venda__gte=inicio_mes))

            receita_total = sum(v.total for v in todas)
            receita_mes = sum(v.total for v in vendas_mes)

            return {
                "total_vendas": len(todas),
                "receita_total": round(receita_total, 2),
                "receita_mes": round(receita_mes, 2),
                "vendas_hoje": len(vendas_hoje),
                "vendas_mes": len(vendas_mes),
                "media_por_venda": round(
                    receita_total / len(todas), 2
                ) if todas else 0.0,
            }

        except Exception as e:
            logger.error(f"Erro ao obter estatísticas de vendas: {e}")
            return {
                "total_vendas": 0,
                "receita_total": 0.0,
                "receita_mes": 0.0,
                "vendas_hoje": 0,
                "vendas_mes": 0,
                "media_por_venda": 0.0,
            }

    def obter_vendas_por_mes_todos_produtos(self) -> List[Dict]:
        """
        Agrega o total de vendas mensais de todos os produtos.
        Usado para o gráfico de linha do Dashboard.

        Returns:
            Lista de dicts com 'periodo' (MM/YYYY) e 'total'.
        """
        try:
            todas = list(Venda.objects().order_by("data_venda"))
            agregado: Dict[str, float] = {}

            for venda in todas:
                periodo = venda.data_venda.strftime("%m/%Y")
                agregado[periodo] = agregado.get(periodo, 0) + venda.total

            return [
                {"periodo": k, "total": round(v, 2)}
                for k, v in agregado.items()
            ]
        except Exception as e:
            logger.error(f"Erro ao agregar vendas mensais: {e}")
            return []
