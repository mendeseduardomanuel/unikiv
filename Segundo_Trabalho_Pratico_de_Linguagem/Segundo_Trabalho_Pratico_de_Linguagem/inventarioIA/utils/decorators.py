"""
=============================================================================
Ficheiro: utils/decorators.py
Descrição: Decoradores personalizados para logging, validação, temporização
           e controlo de acesso.
           
POO: Decoradores são funções de ordem superior que envolvem outras funções,
     adicionando comportamento sem modificar o código original.
=============================================================================
"""

import time
import logging
import functools
from typing import Callable, Any, Optional

logger = logging.getLogger(__name__)


# =============================================================================
# Decorador 1: log_execution
# Regista automaticamente a entrada, saída e duração de qualquer função.
# =============================================================================
def log_execution(func: Callable) -> Callable:
    """
    Decorador que regista automaticamente a execução de uma função.
    Regista: nome da função, argumentos, resultado e tempo de execução.

    Exemplo de uso:
        @log_execution
        def calcular_stock(produto_id: str) -> int:
            ...
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.perf_counter()
        func_name = func.__qualname__

        logger.debug(
            f"[LOG] Iniciando '{func_name}' | "
            f"args={args[1:] if args else ()} | kwargs={kwargs}"
        )

        try:
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start_time
            logger.debug(
                f"[LOG] '{func_name}' concluída com sucesso em {elapsed:.4f}s"
            )
            return result

        except Exception as exc:
            elapsed = time.perf_counter() - start_time
            logger.error(
                f"[LOG] '{func_name}' falhou após {elapsed:.4f}s | Erro: {exc}"
            )
            raise  # Re-lança a excepção original

    return wrapper


# =============================================================================
# Decorador 2: validate_positive
# Valida que todos os argumentos numéricos são positivos.
# =============================================================================
def validate_positive(*param_names: str) -> Callable:
    """
    Decorador de fábrica que valida que parâmetros especificados são positivos.

    Parâmetros:
        *param_names: Nomes dos parâmetros a validar.

    Exemplo de uso:
        @validate_positive("quantidade", "preco")
        def registrar_venda(self, produto_id: str, quantidade: int, preco: float):
            ...
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Combina argumentos posicionais com os seus nomes
            import inspect
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            params = bound.arguments

            for param_name in param_names:
                if param_name in params:
                    value = params[param_name]
                    if isinstance(value, (int, float)) and value <= 0:
                        raise ValueError(
                            f"O parâmetro '{param_name}' deve ser positivo. "
                            f"Recebido: {value}"
                        )
            return func(*args, **kwargs)

        return wrapper

    return decorator


# =============================================================================
# Decorador 3: retry
# Tenta executar a função N vezes antes de lançar a excepção final.
# =============================================================================
def retry(
    max_attempts: int = 3,
    delay_seconds: float = 1.0,
    exceptions: tuple = (Exception,),
) -> Callable:
    """
    Decorador de fábrica que retenta a execução de uma função em caso de falha.

    Parâmetros:
        max_attempts: Número máximo de tentativas (padrão: 3).
        delay_seconds: Espera (em segundos) entre tentativas (padrão: 1.0).
        exceptions: Tupla de excepções que activam o retry (padrão: Exception).

    Exemplo de uso:
        @retry(max_attempts=3, delay_seconds=0.5, exceptions=(ConnectionError,))
        def conectar_base_dados():
            ...
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception: Optional[Exception] = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    last_exception = exc
                    logger.warning(
                        f"[RETRY] '{func.__qualname__}' falhou na tentativa "
                        f"{attempt}/{max_attempts}: {exc}"
                    )
                    if attempt < max_attempts:
                        time.sleep(delay_seconds)

            logger.error(
                f"[RETRY] '{func.__qualname__}' falhou após {max_attempts} tentativas."
            )
            raise last_exception  # type: ignore

        return wrapper

    return decorator


# =============================================================================
# Decorador 4: timer
# Mede e regista o tempo de execução de uma função.
# =============================================================================
def timer(func: Callable) -> Callable:
    """
    Decorador que mede o tempo de execução de uma função e o imprime no log.

    Exemplo de uso:
        @timer
        def treinar_modelo_ia():
            ...
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        logger.info(
            f"[TIMER] '{func.__qualname__}' executada em {elapsed:.4f} segundos."
        )
        return result

    return wrapper


# =============================================================================
# Decorador 5: require_auth
# Verifica se existe uma sessão activa antes de executar a função.
# =============================================================================
def require_auth(func: Callable) -> Callable:
    """
    Decorador que protege funções que requerem autenticação activa.
    Lança InsufficientPermissionsException se não houver sessão.

    Nota: Espera que o primeiro argumento (self) tenha um atributo
    'current_user' ou 'session' não-nulo.

    Exemplo de uso:
        @require_auth
        def eliminar_produto(self, produto_id: str):
            ...
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        from exceptions.auth_exception import InsufficientPermissionsException

        # args[0] é normalmente 'self' numa instância de classe
        instance = args[0] if args else None

        if instance is not None:
            # Verifica se o serviço/instância tem sessão activa
            session = getattr(instance, "current_user", None) or getattr(
                instance, "session", None
            )
            if session is None:
                raise InsufficientPermissionsException(
                    action=func.__qualname__,
                    required_role="utilizador autenticado",
                )

        return func(*args, **kwargs)

    return wrapper


# =============================================================================
# Decorador 6: cache_result
# Cache simples em memória (TTL em segundos).
# =============================================================================
def cache_result(ttl_seconds: float = 60.0) -> Callable:
    """
    Decorador de fábrica que implementa um cache simples em memória com TTL.

    Parâmetros:
        ttl_seconds: Tempo de vida do cache em segundos (padrão: 60).

    Exemplo de uso:
        @cache_result(ttl_seconds=30)
        def obter_total_produtos():
            ...
    """

    def decorator(func: Callable) -> Callable:
        _cache: dict = {}

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Chave de cache baseada nos argumentos
            key = str(args) + str(sorted(kwargs.items()))
            now = time.time()

            if key in _cache:
                result, timestamp = _cache[key]
                if now - timestamp < ttl_seconds:
                    logger.debug(f"[CACHE] Hit para '{func.__qualname__}'")
                    return result

            result = func(*args, **kwargs)
            _cache[key] = (result, now)
            logger.debug(f"[CACHE] Miss para '{func.__qualname__}'. Cache actualizado.")
            return result

        # Método para limpar o cache manualmente
        wrapper.clear_cache = lambda: _cache.clear()  # type: ignore
        return wrapper

    return decorator
