"""
=============================================================================
Ficheiro: database/connection.py
Descrição: Gestão da ligação ao MongoDB via MongoEngine.
           Implementa o padrão Singleton para garantir uma única instância
           de ligação durante todo o ciclo de vida da aplicação.
=============================================================================
"""

import logging
from mongoengine import connect, disconnect
from mongoengine.connection import get_db
from config.settings import MONGO_URI, MONGO_DATABASE

# Configuração do logger para este módulo
logger = logging.getLogger(__name__)


class DatabaseConnection:
    """
    Classe Singleton responsável por gerir a ligação ao MongoDB.

    Padrão de Projeto: Singleton
    Garante que apenas uma instância de ligação existe em toda a aplicação,
    evitando múltiplas ligações desnecessárias ao servidor de base de dados.

    Exemplo de uso:
        db = DatabaseConnection.get_instance()
        db.connect()
    """

    # Atributo de classe que armazena a única instância (Singleton)
    _instance = None

    # Flag que indica se já existe uma ligação activa
    _connected: bool = False

    def __new__(cls) -> "DatabaseConnection":
        """
        Sobrescreve __new__ para implementar o padrão Singleton.
        Se já existir uma instância, devolve a existente; caso contrário, cria uma nova.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            logger.debug("Nova instância DatabaseConnection criada.")
        return cls._instance

    @classmethod
    def get_instance(cls) -> "DatabaseConnection":
        """
        Método de classe que devolve a instância Singleton.

        Returns:
            DatabaseConnection: A única instância desta classe.
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def connect(self) -> bool:
        """
        Estabelece a ligação ao MongoDB utilizando o URI definido nas settings.

        Returns:
            bool: True se a ligação foi estabelecida com sucesso, False caso contrário.

        Raises:
            ConnectionError: Se não for possível conectar ao servidor MongoDB.
        """
        if self._connected:
            logger.info("Ligação ao MongoDB já existe. A reutilizar.")
            return True

        try:
            connect(
                db=MONGO_DATABASE,
                host=MONGO_URI,
                uuidRepresentation="standard",  # Compatibilidade com PyMongo 4+
            )
            self._connected = True
            logger.info(
                f"Ligação ao MongoDB estabelecida com sucesso: {MONGO_DATABASE}"
            )
            return True

        except Exception as error:
            logger.error(f"Erro ao conectar ao MongoDB: {error}")
            self._connected = False
            raise ConnectionError(
                f"Não foi possível conectar ao MongoDB.\n"
                f"Verifique se o servidor está em execução em {MONGO_URI}.\n"
                f"Detalhe: {error}"
            )

    def disconnect(self) -> None:
        """
        Encerra a ligação ao MongoDB de forma segura.
        """
        if self._connected:
            try:
                disconnect()
                self._connected = False
                logger.info("Ligação ao MongoDB encerrada com sucesso.")
            except Exception as error:
                logger.warning(f"Erro ao desconectar do MongoDB: {error}")

    def is_connected(self) -> bool:
        """
        Verifica se existe uma ligação activa ao MongoDB.

        Returns:
            bool: True se ligado, False caso contrário.
        """
        return self._connected

    def get_database(self):
        """
        Devolve o objecto de base de dados PyMongo (para operações raw).

        Returns:
            Database: Objecto de base de dados PyMongo.

        Raises:
            RuntimeError: Se não houver ligação activa.
        """
        if not self._connected:
            raise RuntimeError(
                "Nenhuma ligação activa ao MongoDB. Chame connect() primeiro."
            )
        return get_db()

    def __repr__(self) -> str:
        status = "conectado" if self._connected else "desconectado"
        return f"DatabaseConnection(uri='{MONGO_URI}', status='{status}')"
