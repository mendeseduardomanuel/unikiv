"""
=============================================================================
Ficheiro: models/produto.py
Descrição: Modelo de dados do Produto usando MongoEngine.
           Implementa validação de dados, propriedades calculadas e
           lógica de negócio relacionada com o produto.
=============================================================================
"""

import logging
from datetime import datetime
from mongoengine import (
    Document,
    StringField,
    FloatField,
    IntField,
    DateTimeField,
    BooleanField,
)
from exceptions.stock_exception import (
    InvalidStockValueException,
    InvalidProductDataException,
)

logger = logging.getLogger(__name__)


class Produto(Document):
    """
    Modelo MongoEngine para a colecção 'produtos' no MongoDB.

    POO:
      - Encapsulamento: validação de dados no setter/método.
      - Herança: herda de Document (MongoEngine).

    Campos:
        nome        : Nome do produto (único no inventário).
        categoria   : Categoria do produto (ex: "Alimentação", "Electrónica").
        preco       : Preço unitário do produto (em AOA ou moeda configurada).
        stock       : Quantidade disponível em stock.
        stock_minimo: Nível mínimo de stock (para alertas).
        descricao   : Descrição detalhada do produto.
        ativo       : Se o produto está activo no catálogo.
        criado_em   : Data de criação do registo.
        atualizado_em: Data da última actualização.
    """

    # -----------------------------------------------------------------
    # Campos do documento MongoDB
    # -----------------------------------------------------------------
    nome = StringField(
        required=True,
        unique=True,
        max_length=100,
        min_length=2,
    )
    categoria = StringField(
        required=True,
        max_length=50,
        default="Geral",
    )
    preco = FloatField(required=True, min_value=0.0)
    stock = IntField(required=True, min_value=0, default=0)
    stock_minimo = IntField(default=10, min_value=0)
    descricao = StringField(max_length=500, default="")
    ativo = BooleanField(default=True)
    criado_em = DateTimeField(default=datetime.utcnow)
    atualizado_em = DateTimeField(default=datetime.utcnow)

    # -----------------------------------------------------------------
    # Configuração da colecção MongoDB
    # -----------------------------------------------------------------
    meta = {
        "collection": "produtos",
        "ordering": ["nome"],
        "indexes": [
            "nome",
            "categoria",
            "stock",
        ],
    }

    # =================================================================
    # Validação personalizada (chamada pelo MongoEngine no save())
    # =================================================================

    def clean(self) -> None:
        """
        Método de validação executado pelo MongoEngine antes de guardar.
        Lança ValidationError se os dados forem inválidos.

        POO: Polimorfismo - sobrescreve o método clean() da classe pai Document.
        """
        if self.preco is not None and self.preco < 0:
            raise InvalidProductDataException("preco", "O preço não pode ser negativo.")

        if self.stock is not None and self.stock < 0:
            raise InvalidStockValueException(self.stock)

        if self.nome:
            self.nome = self.nome.strip()
            if len(self.nome) < 2:
                raise InvalidProductDataException(
                    "nome", "O nome deve ter pelo menos 2 caracteres."
                )

        # Actualiza o timestamp de modificação
        self.atualizado_em = datetime.utcnow()

    # =================================================================
    # Propriedades Calculadas (Encapsulamento)
    # =================================================================

    @property
    def tem_stock_baixo(self) -> bool:
        """
        Verifica se o stock está abaixo do mínimo configurado.

        Returns:
            bool: True se stock <= stock_minimo.
        """
        return self.stock <= self.stock_minimo

    @property
    def valor_total_stock(self) -> float:
        """
        Calcula o valor total do stock (preço × quantidade).

        Returns:
            float: Valor monetário total do stock deste produto.
        """
        return round(self.preco * self.stock, 2)

    @property
    def estado_stock(self) -> str:
        """
        Devolve uma descrição textual do estado do stock.

        Returns:
            str: "Crítico" | "Baixo" | "Normal" | "Elevado"
        """
        if self.stock == 0:
            return "Sem Stock"
        elif self.stock <= self.stock_minimo // 2:
            return "Crítico"
        elif self.stock <= self.stock_minimo:
            return "Baixo"
        elif self.stock <= self.stock_minimo * 3:
            return "Normal"
        else:
            return "Elevado"

    # =================================================================
    # Métodos de Negócio
    # =================================================================

    def decrementar_stock(self, quantidade: int) -> None:
        """
        Reduz o stock em 'quantidade' unidades após uma venda.

        Parâmetros:
            quantidade: Número de unidades vendidas.

        Raises:
            InsufficientStockException: Se o stock for insuficiente.
            InvalidStockValueException: Se a quantidade for negativa.
        """
        from exceptions.stock_exception import InsufficientStockException

        if quantidade <= 0:
            raise InvalidStockValueException(quantidade)

        if self.stock < quantidade:
            from exceptions.stock_exception import InsufficientStockException
            raise InsufficientStockException(
                product_name=self.nome,
                requested=quantidade,
                available=self.stock,
            )

        self.stock -= quantidade
        self.atualizado_em = datetime.utcnow()
        self.save()
        logger.info(
            f"Stock de '{self.nome}' decrementado em {quantidade}. "
            f"Novo stock: {self.stock}."
        )

    def incrementar_stock(self, quantidade: int) -> None:
        """
        Aumenta o stock em 'quantidade' unidades (reposição).

        Parâmetros:
            quantidade: Número de unidades a adicionar.

        Raises:
            InvalidStockValueException: Se a quantidade for negativa.
        """
        if quantidade <= 0:
            raise InvalidStockValueException(quantidade)

        self.stock += quantidade
        self.atualizado_em = datetime.utcnow()
        self.save()
        logger.info(
            f"Stock de '{self.nome}' incrementado em {quantidade}. "
            f"Novo stock: {self.stock}."
        )

    # =================================================================
    # Representações String
    # =================================================================

    def __str__(self) -> str:
        return (
            f"Produto(nome='{self.nome}', "
            f"stock={self.stock}, "
            f"preco={self.preco:.2f})"
        )

    def __repr__(self) -> str:
        return (
            f"Produto(id={self.id}, nome='{self.nome}', "
            f"categoria='{self.categoria}', "
            f"stock={self.stock})"
        )

    def __eq__(self, other: object) -> bool:
        """Dois produtos são iguais se tiverem o mesmo ID no MongoDB."""
        if not isinstance(other, Produto):
            return NotImplemented
        return str(self.id) == str(other.id)

    def to_dict(self) -> dict:
        """
        Serializa o produto para dicionário (para GUI e exportação CSV).

        Returns:
            dict: Todos os campos do produto.
        """
        return {
            "id": str(self.id),
            "nome": self.nome,
            "categoria": self.categoria,
            "preco": self.preco,
            "stock": self.stock,
            "stock_minimo": self.stock_minimo,
            "descricao": self.descricao,
            "ativo": self.ativo,
            "estado_stock": self.estado_stock,
            "valor_total_stock": self.valor_total_stock,
            "criado_em": self.criado_em.strftime("%d/%m/%Y"),
            "atualizado_em": self.atualizado_em.strftime("%d/%m/%Y %H:%M"),
        }
