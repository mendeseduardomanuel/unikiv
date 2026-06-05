"""
=============================================================================
Ficheiro: models/usuario.py
Descrição: Modelo de dados do Utilizador usando MongoEngine (ODM para MongoDB).
           Inclui lógica de hash de palavra-passe e verificação de credenciais.

POO: Encapsulamento - dados sensíveis (password_hash) são protegidos
     e só acessíveis através de métodos específicos.
=============================================================================
"""

import hashlib
import os
import logging
from datetime import datetime
from mongoengine import (
    Document,
    StringField,
    BooleanField,
    DateTimeField,
    IntField,
)

logger = logging.getLogger(__name__)


class Usuario(Document):
    """
    Modelo MongoEngine para a colecção 'usuarios' no MongoDB.

    MongoEngine é um ODM (Object-Document Mapper) que mapeia classes Python
    para documentos MongoDB, de forma semelhante a como SQLAlchemy mapeia
    para tabelas SQL.

    POO:
      - Encapsulamento: dados da password são protegidos via métodos.
      - Herança: herda de mongoengine.Document que fornece toda a
        infraestrutura de persistência.

    Campos:
        username      : Nome de utilizador único.
        password_hash : Hash SHA-256 + salt da palavra-passe (nunca texto claro).
        salt          : Salt criptográfico único por utilizador.
        nome_completo : Nome completo do utilizador.
        role          : Papel: "admin" (todos os acessos) | "operador" (limitado).
        ativo         : Se o utilizador está activo no sistema.
        tentativas    : Número de tentativas de login falhadas consecutivas.
        ultimo_login  : Data/hora do último login bem-sucedido.
        criado_em     : Data/hora de criação do registo.
    """

    # -----------------------------------------------------------------
    # Campos do documento MongoDB
    # -----------------------------------------------------------------
    username = StringField(
        required=True,
        unique=True,
        max_length=50,
        min_length=3,
    )
    password_hash = StringField(required=True)
    salt = StringField(required=True)
    nome_completo = StringField(max_length=100, default="")
    role = StringField(
        required=True,
        choices=("admin", "operador"),
        default="operador",
    )
    ativo = BooleanField(default=True)
    tentativas_login = IntField(default=0)
    ultimo_login = DateTimeField(default=None)
    criado_em = DateTimeField(default=datetime.utcnow)

    # -----------------------------------------------------------------
    # Configuração da colecção MongoDB
    # -----------------------------------------------------------------
    meta = {
        "collection": "usuarios",
        "ordering": ["-criado_em"],
        "indexes": ["username"],
    }

    # =================================================================
    # Métodos de Negócio (Encapsulamento)
    # =================================================================

    @classmethod
    def _gerar_salt(cls) -> str:
        """
        Gera um salt criptográfico aleatório de 32 bytes.

        Returns:
            str: Salt em formato hexadecimal.
        """
        return os.urandom(32).hex()

    @classmethod
    def _hash_password(cls, password: str, salt: str) -> str:
        """
        Gera o hash SHA-256 da palavra-passe com o salt.

        Parâmetros:
            password: Palavra-passe em texto claro.
            salt: Salt criptográfico.

        Returns:
            str: Hash hexadecimal de 64 caracteres.
        """
        salted = (password + salt).encode("utf-8")
        return hashlib.sha256(salted).hexdigest()

    @classmethod
    def criar_utilizador(
        cls,
        username: str,
        password: str,
        nome_completo: str = "",
        role: str = "operador",
    ) -> "Usuario":
        """
        Cria e guarda um novo utilizador com a palavra-passe encriptada.

        Parâmetros:
            username     : Nome de utilizador único.
            password     : Palavra-passe em texto claro (nunca guardada).
            nome_completo: Nome completo (opcional).
            role         : Papel do utilizador.

        Returns:
            Usuario: Instância guardada no MongoDB.

        Raises:
            mongoengine.NotUniqueError: Se o username já existir.
        """
        salt = cls._gerar_salt()
        password_hash = cls._hash_password(password, salt)

        utilizador = cls(
            username=username,
            password_hash=password_hash,
            salt=salt,
            nome_completo=nome_completo,
            role=role,
            ativo=True,
            tentativas_login=0,
            criado_em=datetime.utcnow(),
        )
        utilizador.save()
        logger.info(f"Utilizador '{username}' criado com role='{role}'.")
        return utilizador

    def verificar_password(self, password: str) -> bool:
        """
        Verifica se a palavra-passe fornecida corresponde ao hash armazenado.

        POO: Encapsulamento - a lógica de verificação está encapsulada
        no modelo, protegendo os detalhes da implementação.

        Parâmetros:
            password: Palavra-passe em texto claro a verificar.

        Returns:
            bool: True se a palavra-passe está correcta.
        """
        hash_verificar = self._hash_password(password, self.salt)
        return hash_verificar == self.password_hash

    def alterar_password(self, nova_password: str) -> None:
        """
        Altera a palavra-passe do utilizador (gera novo salt).

        Parâmetros:
            nova_password: Nova palavra-passe em texto claro.
        """
        novo_salt = self._gerar_salt()
        novo_hash = self._hash_password(nova_password, novo_salt)
        self.salt = novo_salt
        self.password_hash = novo_hash
        self.save()
        logger.info(f"Palavra-passe do utilizador '{self.username}' alterada.")

    def registrar_login_sucesso(self) -> None:
        """Actualiza os dados de sessão após login bem-sucedido."""
        self.tentativas_login = 0
        self.ultimo_login = datetime.utcnow()
        self.save()

    def registrar_tentativa_falhada(self) -> None:
        """Incrementa o contador de tentativas falhadas."""
        self.tentativas_login += 1
        self.save()

    def is_bloqueado(self, max_tentativas: int = 5) -> bool:
        """
        Verifica se a conta está bloqueada por excesso de tentativas.

        Parâmetros:
            max_tentativas: Número máximo de tentativas permitidas.

        Returns:
            bool: True se a conta está bloqueada.
        """
        return self.tentativas_login >= max_tentativas

    def is_admin(self) -> bool:
        """Verifica se o utilizador tem papel de administrador."""
        return self.role == "admin"

    def desbloquear(self) -> None:
        """Desbloqueia a conta resetando o contador de tentativas."""
        self.tentativas_login = 0
        self.save()
        logger.info(f"Conta '{self.username}' desbloqueada.")

    # =================================================================
    # Representações String (dunder methods)
    # =================================================================

    def __str__(self) -> str:
        return (
            f"Usuario(username='{self.username}', "
            f"role='{self.role}', "
            f"ativo={self.ativo})"
        )

    def __repr__(self) -> str:
        return (
            f"Usuario(id={self.id}, username='{self.username}', "
            f"role='{self.role}')"
        )

    def to_dict(self) -> dict:
        """
        Serializa o utilizador para dicionário (sem dados sensíveis).

        Returns:
            dict: Dados do utilizador sem password_hash nem salt.
        """
        return {
            "id": str(self.id),
            "username": self.username,
            "nome_completo": self.nome_completo,
            "role": self.role,
            "ativo": self.ativo,
            "ultimo_login": (
                self.ultimo_login.strftime("%d/%m/%Y %H:%M")
                if self.ultimo_login
                else "Nunca"
            ),
            "criado_em": self.criado_em.strftime("%d/%m/%Y"),
        }
