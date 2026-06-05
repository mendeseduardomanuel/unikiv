"""
=============================================================================
Ficheiro: utils/context_manager.py
Descrição: Context Managers personalizados para gestão de transacções,
           ficheiros CSV e operações temporárias.
           
POO: Context Managers implementam os métodos __enter__ e __exit__,
     garantindo que recursos são correctamente iniciados e libertados,
     mesmo que ocorram excepções.
=============================================================================
"""

import csv
import logging
import os
import time
from typing import Optional, Any, Generator
from contextlib import contextmanager

logger = logging.getLogger(__name__)


# =============================================================================
# Context Manager 1: DatabaseTransaction
# Gere transacções MongoDB de forma segura.
# =============================================================================
class DatabaseTransaction:
    """
    Context Manager para operações de base de dados que devem ser atómicas.
    
    Garante que, em caso de erro, as alterações sejam revertidas (rollback),
    mantendo a integridade dos dados.
    
    Nota: MongoDB suporta transacções ACID a partir da versão 4.0 em modo
    ReplicaSet. Para desenvolvimento local em modo standalone, usamos
    um mecanismo de controlo lógico.

    Exemplo de uso:
        with DatabaseTransaction("Registar venda") as txn:
            produto_service.decrementar_stock(produto_id, quantidade)
            venda_service.registrar(venda)
            txn.commit()
    """

    def __init__(self, operation_name: str = "transacção") -> None:
        """
        Inicializa o contexto de transacção.
        
        Parâmetros:
            operation_name: Nome descritivo da operação (para logging).
        """
        self.operation_name = operation_name
        self._start_time: float = 0.0
        self._committed: bool = False
        self._operations_log: list = []

    def __enter__(self) -> "DatabaseTransaction":
        """
        Iniciada ao entrar no bloco 'with'.
        Inicia o temporizador e regista o início da transacção.
        """
        self._start_time = time.perf_counter()
        self._committed = False
        self._operations_log = []
        logger.debug(f"[TRANSACÇÃO] Iniciada: '{self.operation_name}'")
        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],
    ) -> bool:
        """
        Executada ao sair do bloco 'with' (normalmente ou por excepção).
        
        Parâmetros:
            exc_type: Tipo da excepção (None se não houve erro).
            exc_val: Valor da excepção.
            exc_tb: Traceback da excepção.
            
        Returns:
            bool: False para não suprimir excepções.
        """
        elapsed = time.perf_counter() - self._start_time

        if exc_type is not None:
            # Ocorreu uma excepção → rollback lógico
            logger.error(
                f"[TRANSACÇÃO] FALHOU '{self.operation_name}' após {elapsed:.4f}s. "
                f"Erro: {exc_val}. "
                f"Operações registadas: {self._operations_log}"
            )
        elif self._committed:
            logger.info(
                f"[TRANSACÇÃO] Concluída com sucesso '{self.operation_name}' "
                f"em {elapsed:.4f}s. "
                f"Operações: {len(self._operations_log)}"
            )
        else:
            logger.warning(
                f"[TRANSACÇÃO] '{self.operation_name}' encerrada sem commit explícito."
            )

        # Retorna False para não suprimir a excepção
        return False

    def commit(self) -> None:
        """Marca a transacção como confirmada com sucesso."""
        self._committed = True
        logger.debug(
            f"[TRANSACÇÃO] Commit em '{self.operation_name}'. "
            f"Operações: {self._operations_log}"
        )

    def log_operation(self, description: str) -> None:
        """
        Regista uma operação realizada dentro da transacção.
        Útil para auditoria e rollback manual.
        
        Parâmetros:
            description: Descrição textual da operação.
        """
        self._operations_log.append(description)
        logger.debug(f"[TRANSACÇÃO] Op registada: {description}")


# =============================================================================
# Context Manager 2: CSVWriter
# Gere a escrita de ficheiros CSV de forma segura.
# =============================================================================
class CSVWriter:
    """
    Context Manager para escrita de ficheiros CSV.
    Garante que o ficheiro é correctamente aberto, escrito e fechado,
    mesmo que ocorram erros durante a escrita.

    Exemplo de uso:
        with CSVWriter("relatorio_produtos.csv", ["Nome", "Stock", "Preço"]) as writer:
            for produto in produtos:
                writer.write_row([produto.nome, produto.stock, produto.preco])
    """

    def __init__(
        self,
        filepath: str,
        headers: list,
        delimiter: str = ";",
        encoding: str = "utf-8-sig",
    ) -> None:
        """
        Parâmetros:
            filepath: Caminho completo do ficheiro CSV.
            headers: Lista com os cabeçalhos das colunas.
            delimiter: Delimitador de campos (padrão: ";").
            encoding: Codificação do ficheiro (padrão: "utf-8-sig" para Excel PT).
        """
        self.filepath = filepath
        self.headers = headers
        self.delimiter = delimiter
        self.encoding = encoding
        self._file = None
        self._writer = None
        self._rows_written: int = 0

    def __enter__(self) -> "CSVWriter":
        """Abre o ficheiro e escreve os cabeçalhos."""
        # Garante que o directório existe
        os.makedirs(os.path.dirname(self.filepath) if os.path.dirname(self.filepath) else ".", exist_ok=True)
        
        self._file = open(
            self.filepath, mode="w", newline="", encoding=self.encoding
        )
        self._writer = csv.writer(self._file, delimiter=self.delimiter)
        self._writer.writerow(self.headers)
        self._rows_written = 0
        logger.debug(f"[CSV] Ficheiro aberto: '{self.filepath}'")
        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],
    ) -> bool:
        """Fecha o ficheiro, mesmo que tenha ocorrido um erro."""
        if self._file:
            self._file.close()
            if exc_type is None:
                logger.info(
                    f"[CSV] Ficheiro '{self.filepath}' guardado com "
                    f"{self._rows_written} linhas."
                )
            else:
                logger.error(
                    f"[CSV] Erro ao escrever '{self.filepath}': {exc_val}"
                )
        return False

    def write_row(self, row: list) -> None:
        """
        Escreve uma linha no ficheiro CSV.
        
        Parâmetros:
            row: Lista de valores para a linha.
            
        Raises:
            RuntimeError: Se o writer não foi inicializado (fora do bloco 'with').
        """
        if self._writer is None:
            raise RuntimeError(
                "CSVWriter não inicializado. Use dentro de um bloco 'with'."
            )
        self._writer.writerow(row)
        self._rows_written += 1

    def write_rows(self, rows: list) -> None:
        """
        Escreve múltiplas linhas de uma só vez.
        
        Parâmetros:
            rows: Lista de listas de valores.
        """
        for row in rows:
            self.write_row(row)

    @property
    def rows_written(self) -> int:
        """Devolve o número de linhas escritas até ao momento."""
        return self._rows_written


# =============================================================================
# Context Manager 3: MeasureTime (usando @contextmanager do contextlib)
# Mede o tempo de execução de um bloco de código.
# =============================================================================
@contextmanager
def measure_time(operation: str = "operação") -> Generator[dict, None, None]:
    """
    Context Manager baseado em generator para medir tempo de execução.
    
    Usa o decorador @contextmanager do módulo contextlib, que é uma forma
    mais concisa de criar context managers sem precisar de uma classe.

    Parâmetros:
        operation: Nome descritivo da operação (para logging e resultado).

    Yields:
        dict: Dicionário com chave 'elapsed' preenchida após o bloco.

    Exemplo de uso:
        with measure_time("treinar modelo IA") as timing:
            modelo.fit(X_train, y_train)
        print(f"IA treinada em {timing['elapsed']:.2f}s")
    """
    timing = {"elapsed": 0.0, "operation": operation}
    start = time.perf_counter()
    logger.debug(f"[TIMER] Iniciando medição: '{operation}'")

    try:
        yield timing
    finally:
        timing["elapsed"] = time.perf_counter() - start
        logger.info(
            f"[TIMER] '{operation}' completada em {timing['elapsed']:.4f}s"
        )


# =============================================================================
# Context Manager 4: SuppressAndLog
# Suprime excepções específicas e regista-as no log.
# =============================================================================
@contextmanager
def suppress_and_log(
    *exception_types: type,
    default_value: Any = None,
    log_level: str = "warning",
) -> Generator[dict, None, None]:
    """
    Context Manager que suprime excepções específicas e as regista.
    Útil para operações não-críticas onde falhas devem ser silenciosas.

    Parâmetros:
        *exception_types: Tipos de excepção a suprimir.
        default_value: Valor a usar se houver excepção (armazenado em result).
        log_level: Nível de log ("debug", "info", "warning", "error").

    Yields:
        dict: Com chaves 'result' e 'error'.

    Exemplo de uso:
        with suppress_and_log(ValueError, ZeroDivisionError) as ctx:
            ctx['result'] = calcular_media(dados)
        print(ctx['result'] or "Não foi possível calcular")
    """
    ctx: dict = {"result": default_value, "error": None, "suppressed": False}

    try:
        yield ctx
    except exception_types as exc:  # type: ignore
        ctx["error"] = exc
        ctx["suppressed"] = True
        log_fn = getattr(logger, log_level, logger.warning)
        log_fn(f"[SUPPRESS] Excepção suprimida: {type(exc).__name__}: {exc}")
    except Exception:
        # Excepções não especificadas são re-lançadas
        raise
