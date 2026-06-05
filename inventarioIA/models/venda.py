"""
=============================================================================
Ficheiro: models/venda.py
Descrição: Modelo de dados da Venda usando MongoEngine.
           Referencia o modelo Produto via ReferenceField (relação 1-N).
=============================================================================
"""

import logging
from datetime import datetime
from mongoengine import (
    Document,
    ReferenceField,
    IntField,
    FloatField,
    StringField,
    DateTimeField,
    CASCADE,
)

logger = logging.getLogger(__name__)


class Venda(Document):
    """
    Modelo MongoEngine para a colecção 'vendas' no MongoDB.

    POO:
      - Herança: herda de mongoengine.Document.
      - Encapsulamento: propriedades calculadas (total, etc.).

    Relação com Produto:
      - ReferenceField cria uma referência ao documento Produto.
      - CASCADE define que se o Produto for eliminado, as vendas
        associadas também são eliminadas (integridade referencial).

    Campos:
        produto       : Referência ao produto vendido.
        quantidade    : Número de unidades vendidas.
        preco_unitario: Preço no momento da venda (histórico).
        total         : Total da venda (calculado: quantidade × preco_unitario).
        observacoes   : Notas opcionais sobre a venda.
        vendido_por   : Username do utilizador que registou a venda.
        data_venda    : Data e hora da venda.
    """

    # -----------------------------------------------------------------
    # Campos do documento MongoDB
    # -----------------------------------------------------------------
    produto = ReferenceField(
        "Produto",
        required=True,
        reverse_delete_rule=CASCADE,  # Elimina vendas se produto for eliminado
    )
    quantidade = IntField(required=True, min_value=1)
    preco_unitario = FloatField(required=True, min_value=0.0)
    total = FloatField(required=True, min_value=0.0)
    observacoes = StringField(max_length=300, default="")
    vendido_por = StringField(max_length=50, default="sistema")
    data_venda = DateTimeField(default=datetime.utcnow)

    # -----------------------------------------------------------------
    # Configuração da colecção MongoDB
    # -----------------------------------------------------------------
    meta = {
        "collection": "vendas",
        "ordering": ["-data_venda"],  # Mais recentes primeiro
        "indexes": [
            "produto",
            "data_venda",
            "vendido_por",
        ],
    }

    # =================================================================
    # Método factory para criação consistente
    # =================================================================

    @classmethod
    def criar_venda(
        cls,
        produto,
        quantidade: int,
        vendido_por: str = "sistema",
        observacoes: str = "",
    ) -> "Venda":
        """
        Cria e guarda uma nova venda.
        Calcula automaticamente o total com base no preço actual do produto.

        Parâmetros:
            produto    : Instância de Produto.
            quantidade : Número de unidades vendidas.
            vendido_por: Username do utilizador.
            observacoes: Notas opcionais.

        Returns:
            Venda: Instância guardada no MongoDB.
        """
        total = round(produto.preco * quantidade, 2)

        venda = cls(
            produto=produto,
            quantidade=quantidade,
            preco_unitario=produto.preco,
            total=total,
            vendido_por=vendido_por,
            observacoes=observacoes,
            data_venda=datetime.utcnow(),
        )
        venda.save()
        logger.info(
            f"Venda registada: {quantidade}x '{produto.nome}' "
            f"| Total: {total:.2f} | Por: {vendido_por}"
        )
        return venda

    # =================================================================
    # Propriedades Calculadas
    # =================================================================

    @property
    def data_formatada(self) -> str:
        """Devolve a data da venda formatada para exibição."""
        return self.data_venda.strftime("%d/%m/%Y %H:%M")

    @property
    def nome_produto(self) -> str:
        """Devolve o nome do produto de forma segura."""
        try:
            return self.produto.nome if self.produto else "Produto removido"
        except Exception:
            return "Produto removido"

    # =================================================================
    # Representações String
    # =================================================================

    def __str__(self) -> str:
        return (
            f"Venda({self.data_formatada}: "
            f"{self.quantidade}x '{self.nome_produto}' "
            f"= {self.total:.2f})"
        )

    def __repr__(self) -> str:
        return (
            f"Venda(id={self.id}, "
            f"produto='{self.nome_produto}', "
            f"quantidade={self.quantidade}, "
            f"total={self.total})"
        )

    def to_dict(self) -> dict:
        """
        Serializa a venda para dicionário (para GUI e exportação CSV).

        Returns:
            dict: Todos os campos da venda.
        """
        return {
            "id": str(self.id),
            "produto_id": str(self.produto.id) if self.produto else "",
            "produto_nome": self.nome_produto,
            "quantidade": self.quantidade,
            "preco_unitario": self.preco_unitario,
            "total": self.total,
            "observacoes": self.observacoes,
            "vendido_por": self.vendido_por,
            "data_venda": self.data_formatada,
        }
