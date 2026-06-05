"""
=============================================================================
Ficheiro: exceptions/stock_exception.py
Descrição: Excepções customizadas relacionadas com stock e inventário.
=============================================================================
"""


class StockException(Exception):
    """
    Classe base para todas as excepções de stock/inventário.

    POO: Herança - serve como classe pai para excepções de stock mais específicas.
    """

    def __init__(self, message: str = "Erro de stock.") -> None:
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"[StockException] {self.message}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message='{self.message}')"


class InsufficientStockException(StockException):
    """
    Levantada quando se tenta vender mais unidades do que as disponíveis em stock.

    POO: Herança - especializa StockException para stock insuficiente.

    Exemplo:
        raise InsufficientStockException(
            product_name="Arroz 5kg",
            requested=50,
            available=10
        )
    """

    def __init__(
        self,
        product_name: str = "",
        requested: int = 0,
        available: int = 0,
    ) -> None:
        if product_name:
            message = (
                f"Stock insuficiente para '{product_name}'. "
                f"Solicitado: {requested} | Disponível: {available}."
            )
        else:
            message = (
                f"Stock insuficiente. "
                f"Solicitado: {requested} | Disponível: {available}."
            )
        super().__init__(message)
        self.product_name = product_name
        self.requested = requested
        self.available = available

    def __str__(self) -> str:
        return f"[InsufficientStockException] {self.message}"


class LowStockWarningException(StockException):
    """
    Levantada como aviso quando o stock atinge o nível mínimo configurado.

    POO: Herança - especializa StockException para avisos de stock baixo.
    Nota: Este é um aviso (warning), não necessariamente um erro crítico.
    """

    def __init__(
        self,
        product_name: str = "",
        current_stock: int = 0,
        threshold: int = 10,
    ) -> None:
        message = (
            f"AVISO: Stock baixo para '{product_name}'. "
            f"Stock actual: {current_stock} (mínimo: {threshold})."
        )
        super().__init__(message)
        self.product_name = product_name
        self.current_stock = current_stock
        self.threshold = threshold

    def __str__(self) -> str:
        return f"[LowStockWarningException] {self.message}"


class ProductNotFoundException(StockException):
    """
    Levantada quando um produto não é encontrado na base de dados.

    POO: Herança - especializa StockException para produto não encontrado.
    """

    def __init__(self, product_id: str = "", product_name: str = "") -> None:
        if product_id:
            message = f"Produto com ID '{product_id}' não encontrado."
        elif product_name:
            message = f"Produto '{product_name}' não encontrado."
        else:
            message = "Produto não encontrado."
        super().__init__(message)
        self.product_id = product_id
        self.product_name = product_name

    def __str__(self) -> str:
        return f"[ProductNotFoundException] {self.message}"


class InvalidStockValueException(StockException):
    """
    Levantada quando um valor de stock inválido é fornecido (ex: negativo).

    POO: Herança - especializa StockException para valores inválidos.
    """

    def __init__(self, value: object = None) -> None:
        message = (
            f"Valor de stock inválido: '{value}'. "
            "O stock deve ser um número inteiro não-negativo."
        )
        super().__init__(message)
        self.value = value

    def __str__(self) -> str:
        return f"[InvalidStockValueException] {self.message}"


class InvalidProductDataException(StockException):
    """
    Levantada quando os dados de um produto são inválidos ou incompletos.

    POO: Herança - especializa StockException para dados de produto inválidos.
    """

    def __init__(self, field: str = "", reason: str = "") -> None:
        if field and reason:
            message = f"Dados inválidos no campo '{field}': {reason}."
        elif field:
            message = f"Campo inválido: '{field}'."
        else:
            message = "Dados do produto inválidos ou incompletos."
        super().__init__(message)
        self.field = field
        self.reason = reason

    def __str__(self) -> str:
        return f"[InvalidProductDataException] {self.message}"


class DuplicateProductException(StockException):
    """
    Levantada ao tentar adicionar um produto com nome já existente.

    POO: Herança - especializa StockException para produtos duplicados.
    """

    def __init__(self, product_name: str = "") -> None:
        message = (
            f"Produto '{product_name}' já existe no inventário."
            if product_name
            else "Produto duplicado no inventário."
        )
        super().__init__(message)
        self.product_name = product_name

    def __str__(self) -> str:
        return f"[DuplicateProductException] {self.message}"
