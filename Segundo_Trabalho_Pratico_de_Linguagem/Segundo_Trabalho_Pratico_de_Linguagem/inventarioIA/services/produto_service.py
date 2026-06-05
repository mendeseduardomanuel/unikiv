"""
=============================================================================
Ficheiro: services/produto_service.py
Descrição: Serviço de negócio para gestão de produtos/inventário.
           Implementa todas as operações CRUD e lógica de negócio.

POO:
  - Implementa IProdutoRepository (interface abstracta).
  - Decoradores: @log_execution, @validate_positive.
=============================================================================
"""

import logging
from typing import Optional, List, Dict, Any

from interfaces.repository_interface import IProdutoRepository
from models.produto import Produto
from exceptions.stock_exception import (
    ProductNotFoundException,
    DuplicateProductException,
    InvalidProductDataException,
    InvalidStockValueException,
    LowStockWarningException,
)
from config.settings import STOCK_LOW_THRESHOLD
from utils.decorators import log_execution, validate_positive, cache_result

logger = logging.getLogger(__name__)


class ProdutoService(IProdutoRepository):
    """
    Serviço que implementa todas as operações de gestão de produtos.

    POO:
      - Herança: implementa IProdutoRepository.
      - Polimorfismo: os métodos abstractos são concretizados aqui.
      - Decoradores: enriquecem os métodos com logging, validação e cache.

    Padrão de Projecto: Service Layer
    Centraliza a lógica de negócio, separando-a da GUI e da camada de dados.
    """

    def __init__(self) -> None:
        logger.info("ProdutoService inicializado.")

    # =================================================================
    # CRUD - Criar
    # =================================================================

    @log_execution
    def criar(self, dados: Dict[str, Any]) -> Produto:
        """
        Cria um novo produto no inventário.

        Parâmetros:
            dados: Dicionário com os campos do produto.
                   Chaves: nome, categoria, preco, stock, stock_minimo, descricao.

        Returns:
            Produto: Produto criado.

        Raises:
            DuplicateProductException  : Se já existir produto com esse nome.
            InvalidProductDataException: Se os dados forem inválidos.
        """
        nome = dados.get("nome", "").strip()
        if not nome:
            raise InvalidProductDataException("nome", "O nome é obrigatório.")

        # Verifica duplicado
        existente = self.obter_por_nome(nome)
        if existente:
            raise DuplicateProductException(nome)

        try:
            produto = Produto(
                nome=nome,
                categoria=dados.get("categoria", "Geral"),
                preco=float(dados.get("preco", 0.0)),
                stock=int(dados.get("stock", 0)),
                stock_minimo=int(dados.get("stock_minimo", STOCK_LOW_THRESHOLD)),
                descricao=dados.get("descricao", ""),
                ativo=True,
            )
            produto.save()
            logger.info(f"Produto criado: '{nome}' (stock={produto.stock})")

            # Emite aviso se stock inicial for baixo
            if produto.tem_stock_baixo:
                logger.warning(
                    f"Produto '{nome}' criado com stock baixo: {produto.stock}"
                )

            return produto

        except Exception as e:
            logger.error(f"Erro ao criar produto '{nome}': {e}")
            raise InvalidProductDataException("geral", str(e))

    # =================================================================
    # CRUD - Ler
    # =================================================================

    @log_execution
    def obter_por_id(self, entity_id: str) -> Optional[Produto]:
        """
        Obtém um produto pelo seu ID MongoDB.

        Parâmetros:
            entity_id: String do ObjectId MongoDB.

        Returns:
            Produto ou None.
        """
        try:
            return Produto.objects(id=entity_id).first()
        except Exception as e:
            logger.error(f"Erro ao obter produto por ID '{entity_id}': {e}")
            return None

    @log_execution
    def obter_todos(self) -> List[Produto]:
        """
        Obtém todos os produtos activos ordenados por nome.

        Returns:
            Lista de Produto.
        """
        try:
            return list(Produto.objects(ativo=True).order_by("nome"))
        except Exception as e:
            logger.error(f"Erro ao obter todos os produtos: {e}")
            return []

    @log_execution
    def obter_por_nome(self, nome: str) -> Optional[Produto]:
        """
        Obtém um produto pelo nome exacto (case-insensitive).

        Parâmetros:
            nome: Nome do produto.

        Returns:
            Produto ou None.
        """
        try:
            return Produto.objects(nome__iexact=nome.strip()).first()
        except Exception as e:
            logger.error(f"Erro ao obter produto por nome '{nome}': {e}")
            return None

    @log_execution
    def obter_por_categoria(self, categoria: str) -> List[Produto]:
        """
        Obtém todos os produtos de uma categoria.

        Parâmetros:
            categoria: Nome da categoria.

        Returns:
            Lista de Produto.
        """
        try:
            return list(
                Produto.objects(categoria__iexact=categoria, ativo=True).order_by(
                    "nome"
                )
            )
        except Exception as e:
            logger.error(f"Erro ao obter produtos da categoria '{categoria}': {e}")
            return []

    @log_execution
    def obter_com_stock_baixo(
        self, threshold: int = STOCK_LOW_THRESHOLD
    ) -> List[Produto]:
        """
        Obtém produtos com stock abaixo do limiar.

        Parâmetros:
            threshold: Quantidade mínima aceitável.

        Returns:
            Lista de Produto com stock baixo.
        """
        try:
            return list(
                Produto.objects(stock__lte=threshold, ativo=True).order_by("stock")
            )
        except Exception as e:
            logger.error(f"Erro ao obter produtos com stock baixo: {e}")
            return []

    @log_execution
    def pesquisar(self, filtros: Dict[str, Any]) -> List[Produto]:
        """
        Pesquisa produtos com base em filtros flexíveis.

        Parâmetros:
            filtros: Dicionário com critérios.
                     Suporta: nome (parcial), categoria, preco_min, preco_max,
                              stock_min, stock_max, ativo.

        Returns:
            Lista de Produto que correspondem.
        """
        try:
            query = Produto.objects()

            if "nome" in filtros and filtros["nome"]:
                query = query.filter(nome__icontains=filtros["nome"])

            if "categoria" in filtros and filtros["categoria"]:
                query = query.filter(categoria__iexact=filtros["categoria"])

            if "preco_min" in filtros:
                query = query.filter(preco__gte=float(filtros["preco_min"]))

            if "preco_max" in filtros:
                query = query.filter(preco__lte=float(filtros["preco_max"]))

            if "stock_min" in filtros:
                query = query.filter(stock__gte=int(filtros["stock_min"]))

            if "stock_max" in filtros:
                query = query.filter(stock__lte=int(filtros["stock_max"]))

            # Por padrão, só produtos activos
            ativo = filtros.get("ativo", True)
            query = query.filter(ativo=ativo)

            return list(query.order_by("nome"))

        except Exception as e:
            logger.error(f"Erro ao pesquisar produtos: {e}")
            return []

    # =================================================================
    # CRUD - Actualizar
    # =================================================================

    @log_execution
    def actualizar(
        self, entity_id: str, dados: Dict[str, Any]
    ) -> Optional[Produto]:
        """
        Actualiza os campos de um produto existente.

        Parâmetros:
            entity_id: ID do produto.
            dados    : Campos a actualizar.

        Returns:
            Produto actualizado ou None.

        Raises:
            ProductNotFoundException: Se o produto não existir.
        """
        produto = self.obter_por_id(entity_id)
        if not produto:
            raise ProductNotFoundException(product_id=entity_id)

        campos_actualizaveis = [
            "nome", "categoria", "preco", "stock",
            "stock_minimo", "descricao", "ativo",
        ]

        for campo in campos_actualizaveis:
            if campo in dados and dados[campo] is not None:
                valor = dados[campo]
                # Conversões de tipo
                if campo == "preco":
                    valor = float(valor)
                elif campo in ("stock", "stock_minimo"):
                    valor = int(valor)
                setattr(produto, campo, valor)

        produto.save()
        logger.info(f"Produto '{produto.nome}' actualizado.")
        return produto

    @log_execution
    def actualizar_stock(
        self, produto_id: str, nova_quantidade: int
    ) -> bool:
        """
        Actualiza apenas o stock de um produto.

        Parâmetros:
            produto_id    : ID do produto.
            nova_quantidade: Novo valor absoluto de stock.

        Returns:
            bool: True se actualizado.

        Raises:
            ProductNotFoundException  : Se o produto não existir.
            InvalidStockValueException: Se a quantidade for negativa.
        """
        if nova_quantidade < 0:
            raise InvalidStockValueException(nova_quantidade)

        produto = self.obter_por_id(produto_id)
        if not produto:
            raise ProductNotFoundException(product_id=produto_id)

        produto.stock = nova_quantidade
        produto.save()

        if produto.tem_stock_baixo:
            logger.warning(
                f"Stock baixo após actualização: '{produto.nome}' = {nova_quantidade}"
            )

        logger.info(f"Stock do produto '{produto.nome}' → {nova_quantidade}")
        return True

    # =================================================================
    # CRUD - Eliminar
    # =================================================================

    @log_execution
    def eliminar(self, entity_id: str) -> bool:
        """
        Elimina logicamente um produto (marca como inactivo).
        Não elimina fisicamente para preservar o histórico de vendas.

        Parâmetros:
            entity_id: ID do produto.

        Returns:
            bool: True se eliminado.

        Raises:
            ProductNotFoundException: Se o produto não existir.
        """
        produto = self.obter_por_id(entity_id)
        if not produto:
            raise ProductNotFoundException(product_id=entity_id)

        produto.ativo = False
        produto.save()
        logger.info(f"Produto '{produto.nome}' desactivado (eliminação lógica).")
        return True

    def eliminar_fisicamente(self, entity_id: str) -> bool:
        """
        Elimina fisicamente um produto da base de dados.
        USE COM CUIDADO - elimina também o histórico.

        Parâmetros:
            entity_id: ID do produto.

        Returns:
            bool: True se eliminado.
        """
        produto = self.obter_por_id(entity_id)
        if not produto:
            raise ProductNotFoundException(product_id=entity_id)

        nome = produto.nome
        produto.delete()
        logger.warning(f"Produto '{nome}' eliminado FISICAMENTE.")
        return True

    # =================================================================
    # Estatísticas para Dashboard
    # =================================================================

    @cache_result(ttl_seconds=30)
    def obter_estatisticas(self) -> Dict[str, Any]:
        """
        Calcula estatísticas globais do inventário para o Dashboard.
        Resultado em cache por 30 segundos.

        Returns:
            dict com:
              total_produtos, produtos_stock_baixo, valor_total_inventario,
              categorias, produtos_sem_stock.
        """
        try:
            todos = self.obter_todos()
            stock_baixo = [p for p in todos if p.tem_stock_baixo]
            sem_stock = [p for p in todos if p.stock == 0]
            valor_total = sum(p.valor_total_stock for p in todos)
            categorias = list({p.categoria for p in todos})

            return {
                "total_produtos": len(todos),
                "produtos_stock_baixo": len(stock_baixo),
                "produtos_sem_stock": len(sem_stock),
                "valor_total_inventario": round(valor_total, 2),
                "categorias": sorted(categorias),
                "total_categorias": len(categorias),
            }
        except Exception as e:
            logger.error(f"Erro ao calcular estatísticas: {e}")
            return {
                "total_produtos": 0,
                "produtos_stock_baixo": 0,
                "produtos_sem_stock": 0,
                "valor_total_inventario": 0.0,
                "categorias": [],
                "total_categorias": 0,
            }

    def obter_categorias(self) -> List[str]:
        """
        Devolve a lista de categorias únicas dos produtos activos.

        Returns:
            Lista de strings (categorias).
        """
        try:
            todos = Produto.objects(ativo=True).only("categoria")
            return sorted(list({p.categoria for p in todos}))
        except Exception:
            return []
