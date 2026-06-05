"""
=============================================================================
Ficheiro: services/auth_service.py
Descrição: Serviço de autenticação e gestão de sessão.
           Implementa lógica de login, logout e controlo de acesso.

POO:
  - Implementa IAuthRepository (contrato de interface).
  - Encapsulamento: estado da sessão protegido.
  - Decoradores: @log_execution, @retry.
=============================================================================
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from interfaces.repository_interface import IAuthRepository
from models.usuario import Usuario
from exceptions.auth_exception import (
    InvalidCredentialsException,
    UserNotFoundException,
    UserAlreadyExistsException,
    SessionExpiredException,
    MaxLoginAttemptsException,
)
from config.settings import MAX_LOGIN_ATTEMPTS, SESSION_TIMEOUT_MINUTES
from utils.decorators import log_execution, retry

logger = logging.getLogger(__name__)


class AuthService(IAuthRepository):
    """
    Serviço de autenticação que implementa a interface IAuthRepository.

    POO:
      - Herança: herda de IAuthRepository (interface abstracta).
      - Polimorfismo: implementa o contrato definido na interface.
      - Encapsulamento: _current_user e _session_start são privados.

    Responsabilidades:
      - Validar credenciais de login.
      - Gerir o estado da sessão activa.
      - Criar novos utilizadores.
      - Controlar tentativas de login.
    """

    def __init__(self) -> None:
        """Inicializa o serviço sem sessão activa."""
        self._current_user: Optional[Usuario] = None
        self._session_start: Optional[datetime] = None

    # =================================================================
    # Implementação da Interface IAuthRepository
    # =================================================================

    @log_execution
    def obter_por_username(self, username: str) -> Optional[Usuario]:
        """
        Obtém um utilizador pelo username.

        Parâmetros:
            username: Nome de utilizador.

        Returns:
            Usuario ou None se não encontrado.
        """
        try:
            return Usuario.objects(username=username).first()
        except Exception as e:
            logger.error(f"Erro ao obter utilizador '{username}': {e}")
            return None

    @log_execution
    def criar_utilizador(
        self,
        username: str,
        password: str,
        role: str = "operador",
        nome_completo: str = "",
    ) -> Usuario:
        """
        Cria um novo utilizador no sistema.

        Parâmetros:
            username     : Nome de utilizador único.
            password     : Palavra-passe em texto claro.
            role         : Papel ("admin" | "operador").
            nome_completo: Nome completo.

        Returns:
            Usuario: Utilizador criado.

        Raises:
            UserAlreadyExistsException: Se o username já existir.
        """
        # Verifica se já existe
        existente = self.obter_por_username(username)
        if existente:
            raise UserAlreadyExistsException(username)

        utilizador = Usuario.criar_utilizador(
            username=username,
            password=password,
            nome_completo=nome_completo,
            role=role,
        )
        logger.info(f"Utilizador '{username}' criado com sucesso.")
        return utilizador

    @log_execution
    def verificar_credenciais(
        self, username: str, password: str
    ) -> Optional[Usuario]:
        """
        Verifica as credenciais e realiza o login.

        Parâmetros:
            username: Nome de utilizador.
            password: Palavra-passe em texto claro.

        Returns:
            Usuario se credenciais válidas.

        Raises:
            UserNotFoundException        : Se o utilizador não existir.
            MaxLoginAttemptsException    : Se a conta estiver bloqueada.
            InvalidCredentialsException  : Se a password estiver errada.
        """
        utilizador = self.obter_por_username(username)

        if not utilizador:
            raise UserNotFoundException(username)

        if not utilizador.ativo:
            raise InvalidCredentialsException(
                "Conta desactivada. Contacte o administrador."
            )

        if utilizador.is_bloqueado(MAX_LOGIN_ATTEMPTS):
            raise MaxLoginAttemptsException(MAX_LOGIN_ATTEMPTS)

        if not utilizador.verificar_password(password):
            utilizador.registrar_tentativa_falhada()
            tentativas_restantes = MAX_LOGIN_ATTEMPTS - utilizador.tentativas_login
            raise InvalidCredentialsException(
                f"Palavra-passe incorrecta. "
                f"Tentativas restantes: {tentativas_restantes}."
            )

        # Login bem-sucedido
        utilizador.registrar_login_sucesso()
        self._current_user = utilizador
        self._session_start = datetime.utcnow()

        logger.info(f"Login bem-sucedido: '{username}' ({utilizador.role})")
        return utilizador

    # =================================================================
    # Gestão de Sessão
    # =================================================================

    def logout(self) -> None:
        """Termina a sessão activa."""
        if self._current_user:
            logger.info(f"Logout: '{self._current_user.username}'")
        self._current_user = None
        self._session_start = None

    @property
    def current_user(self) -> Optional[Usuario]:
        """
        Devolve o utilizador actualmente autenticado.

        Returns:
            Usuario ou None se não houver sessão.
        """
        if self._current_user is None:
            return None

        # Verifica expiração da sessão
        if (
            SESSION_TIMEOUT_MINUTES > 0
            and self._session_start is not None
        ):
            expiry = self._session_start + timedelta(
                minutes=SESSION_TIMEOUT_MINUTES
            )
            if datetime.utcnow() > expiry:
                logger.warning("Sessão expirada.")
                self._current_user = None
                self._session_start = None
                raise SessionExpiredException()

        return self._current_user

    @property
    def is_authenticated(self) -> bool:
        """Verifica se existe uma sessão activa válida."""
        try:
            return self.current_user is not None
        except SessionExpiredException:
            return False

    @property
    def is_admin(self) -> bool:
        """Verifica se o utilizador actual é administrador."""
        user = self.current_user
        return user is not None and user.is_admin()

    def get_session_info(self) -> dict:
        """
        Devolve informações da sessão actual.

        Returns:
            dict: Informações da sessão.
        """
        user = self.current_user
        if user is None:
            return {"authenticated": False}

        duracao = (
            datetime.utcnow() - self._session_start
            if self._session_start
            else timedelta(0)
        )
        return {
            "authenticated": True,
            "username": user.username,
            "nome_completo": user.nome_completo,
            "role": user.role,
            "session_start": self._session_start.strftime("%H:%M:%S")
            if self._session_start
            else "",
            "session_duration_min": int(duracao.total_seconds() / 60),
        }

    # =================================================================
    # Inicialização do Sistema
    # =================================================================

    @staticmethod
    @log_execution
    def garantir_admin_padrao() -> None:
        """
        Garante que existe pelo menos um utilizador administrador.
        Se não existir nenhum, cria o admin padrão.
        Chamado no arranque da aplicação.
        """
        admin_existente = Usuario.objects(role="admin").first()

        if not admin_existente:
            logger.info(
                "Nenhum administrador encontrado. A criar administrador padrão."
            )
            Usuario.criar_utilizador(
                username="admin",
                password="admin123",
                nome_completo="Administrador do Sistema",
                role="admin",
            )
            logger.info(
                "Administrador padrão criado: username='admin', password='admin123'. "
                "ALTERE A PASSWORD APÓS O PRIMEIRO LOGIN!"
            )

    def __repr__(self) -> str:
        user = self._current_user
        return (
            f"AuthService(user='{user.username if user else None}', "
            f"authenticated={self.is_authenticated})"
        )
