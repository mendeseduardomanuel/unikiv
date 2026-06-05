"""
=============================================================================
Ficheiro: exceptions/auth_exception.py
Descrição: Excepções customizadas relacionadas com autenticação e sessão.
           Demonstra a criação de hierarquias de excepções personalizadas.
=============================================================================
"""


class AuthException(Exception):
    """
    Classe base para todas as excepções de autenticação.

    POO: Herança - serve como classe pai para excepções mais específicas.
    Todas as excepções de autenticação herdam desta classe, permitindo
    capturar qualquer erro de auth com um único bloco except.

    Exemplo:
        try:
            auth_service.login(username, password)
        except AuthException as e:
            mostrar_erro(str(e))
    """

    def __init__(self, message: str = "Erro de autenticação.") -> None:
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"[AuthException] {self.message}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message='{self.message}')"


class InvalidCredentialsException(AuthException):
    """
    Levantada quando o nome de utilizador ou palavra-passe estão incorrectos.

    POO: Herança - especializa AuthException para credenciais inválidas.
    """

    def __init__(
        self,
        message: str = "Nome de utilizador ou palavra-passe incorrectos.",
    ) -> None:
        super().__init__(message)

    def __str__(self) -> str:
        return f"[InvalidCredentialsException] {self.message}"


class UserNotFoundException(AuthException):
    """
    Levantada quando o utilizador não existe na base de dados.

    POO: Herança - especializa AuthException para utilizador não encontrado.
    """

    def __init__(self, username: str = "") -> None:
        message = (
            f"Utilizador '{username}' não encontrado."
            if username
            else "Utilizador não encontrado."
        )
        super().__init__(message)
        self.username = username

    def __str__(self) -> str:
        return f"[UserNotFoundException] {self.message}"


class UserAlreadyExistsException(AuthException):
    """
    Levantada ao tentar registar um utilizador com nome já existente.

    POO: Herança - especializa AuthException para duplicação de utilizador.
    """

    def __init__(self, username: str = "") -> None:
        message = (
            f"O utilizador '{username}' já existe no sistema."
            if username
            else "O utilizador já existe no sistema."
        )
        super().__init__(message)
        self.username = username

    def __str__(self) -> str:
        return f"[UserAlreadyExistsException] {self.message}"


class SessionExpiredException(AuthException):
    """
    Levantada quando a sessão do utilizador expirou.

    POO: Herança - especializa AuthException para sessão expirada.
    """

    def __init__(
        self, message: str = "A sessão expirou. Por favor, faça login novamente."
    ) -> None:
        super().__init__(message)

    def __str__(self) -> str:
        return f"[SessionExpiredException] {self.message}"


class MaxLoginAttemptsException(AuthException):
    """
    Levantada quando o número máximo de tentativas de login é atingido.

    POO: Herança - especializa AuthException para bloqueio por tentativas.
    """

    def __init__(self, max_attempts: int = 5) -> None:
        message = (
            f"Número máximo de tentativas de login atingido ({max_attempts}). "
            "Conta temporariamente bloqueada."
        )
        super().__init__(message)
        self.max_attempts = max_attempts

    def __str__(self) -> str:
        return f"[MaxLoginAttemptsException] {self.message}"


class InsufficientPermissionsException(AuthException):
    """
    Levantada quando o utilizador não tem permissão para realizar uma acção.

    POO: Herança - especializa AuthException para controlo de acesso.
    """

    def __init__(self, action: str = "", required_role: str = "admin") -> None:
        message = (
            f"Sem permissão para '{action}'. Necessário papel: '{required_role}'."
            if action
            else f"Permissões insuficientes. Necessário papel: '{required_role}'."
        )
        super().__init__(message)
        self.action = action
        self.required_role = required_role

    def __str__(self) -> str:
        return f"[InsufficientPermissionsException] {self.message}"
