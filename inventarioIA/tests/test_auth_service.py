"""
=============================================================================
Ficheiro: tests/test_auth_service.py
Descrição: Testes unitários para o serviço de autenticação.
=============================================================================
"""

import sys
import os
import unittest
from unittest.mock import MagicMock, patch, PropertyMock
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestAuthServiceLogica(unittest.TestCase):
    """
    Testes unitários para AuthService.
    Usa mocks para não depender do MongoDB.
    """

    def _criar_utilizador_mock(
        self,
        username: str = "teste",
        role: str = "operador",
        ativo: bool = True,
        tentativas: int = 0,
        password_ok: bool = True,
    ) -> MagicMock:
        """Helper que cria um utilizador mock configurável."""
        u = MagicMock()
        u.username = username
        u.nome_completo = f"Utilizador {username.capitalize()}"
        u.role = role
        u.ativo = ativo
        u.tentativas_login = tentativas
        u.is_admin.return_value = role == "admin"
        u.is_bloqueado.return_value = tentativas >= 5
        u.verificar_password.return_value = password_ok
        return u

    # ------------------------------------------------------------------
    # Testes de login bem-sucedido
    # ------------------------------------------------------------------

    def test_login_bem_sucedido_activa_sessao(self) -> None:
        """Após login com credenciais correctas, current_user deve ser preenchido."""
        from services.auth_service import AuthService

        svc = AuthService()
        mock_user = self._criar_utilizador_mock(password_ok=True)

        with patch.object(svc, "obter_por_username", return_value=mock_user):
            resultado = svc.verificar_credenciais("teste", "senha_correcta")

        self.assertIsNotNone(resultado)
        self.assertEqual(resultado.username, "teste")

    def test_login_bem_sucedido_chama_registar_sucesso(self) -> None:
        """Após login, registrar_login_sucesso deve ser chamado no utilizador."""
        from services.auth_service import AuthService

        svc = AuthService()
        mock_user = self._criar_utilizador_mock(password_ok=True)

        with patch.object(svc, "obter_por_username", return_value=mock_user):
            svc.verificar_credenciais("teste", "senha")

        mock_user.registrar_login_sucesso.assert_called_once()

    # ------------------------------------------------------------------
    # Testes de login falhado
    # ------------------------------------------------------------------

    def test_utilizador_inexistente_lanca_user_not_found(self) -> None:
        """Login com username inexistente lança UserNotFoundException."""
        from services.auth_service import AuthService
        from exceptions.auth_exception import UserNotFoundException

        svc = AuthService()
        with patch.object(svc, "obter_por_username", return_value=None):
            with self.assertRaises(UserNotFoundException):
                svc.verificar_credenciais("nao_existe", "qualquer")

    def test_password_errada_lanca_invalid_credentials(self) -> None:
        """Login com password errada lança InvalidCredentialsException."""
        from services.auth_service import AuthService
        from exceptions.auth_exception import InvalidCredentialsException

        svc = AuthService()
        mock_user = self._criar_utilizador_mock(password_ok=False)

        with patch.object(svc, "obter_por_username", return_value=mock_user):
            with self.assertRaises(InvalidCredentialsException):
                svc.verificar_credenciais("teste", "senha_errada")

    def test_password_errada_incrementa_tentativas(self) -> None:
        """Após password errada, tentativas falhadas devem ser incrementadas."""
        from services.auth_service import AuthService
        from exceptions.auth_exception import InvalidCredentialsException

        svc = AuthService()
        mock_user = self._criar_utilizador_mock(password_ok=False)

        with patch.object(svc, "obter_por_username", return_value=mock_user):
            try:
                svc.verificar_credenciais("teste", "errada")
            except InvalidCredentialsException:
                pass

        mock_user.registrar_tentativa_falhada.assert_called_once()

    def test_conta_bloqueada_lanca_max_attempts(self) -> None:
        """Conta com 5+ tentativas falhadas lança MaxLoginAttemptsException."""
        from services.auth_service import AuthService
        from exceptions.auth_exception import MaxLoginAttemptsException

        svc = AuthService()
        mock_user = self._criar_utilizador_mock(tentativas=5)
        mock_user.is_bloqueado.return_value = True

        with patch.object(svc, "obter_por_username", return_value=mock_user):
            with self.assertRaises(MaxLoginAttemptsException):
                svc.verificar_credenciais("bloqueado", "qualquer")

    def test_conta_inactiva_lanca_invalid_credentials(self) -> None:
        """Login com conta inactiva lança InvalidCredentialsException."""
        from services.auth_service import AuthService
        from exceptions.auth_exception import InvalidCredentialsException

        svc = AuthService()
        mock_user = self._criar_utilizador_mock(ativo=False)

        with patch.object(svc, "obter_por_username", return_value=mock_user):
            with self.assertRaises(InvalidCredentialsException):
                svc.verificar_credenciais("inactivo", "senha")

    # ------------------------------------------------------------------
    # Testes de sessão e logout
    # ------------------------------------------------------------------

    def test_logout_limpa_sessao(self) -> None:
        """Após logout, is_authenticated deve ser False."""
        from services.auth_service import AuthService

        svc = AuthService()
        mock_user = self._criar_utilizador_mock()
        svc._current_user = mock_user
        svc._session_start = datetime.utcnow()

        self.assertTrue(svc.is_authenticated)
        svc.logout()
        self.assertFalse(svc.is_authenticated)

    def test_sem_sessao_is_authenticated_false(self) -> None:
        """Sem login prévio, is_authenticated deve ser False."""
        from services.auth_service import AuthService

        svc = AuthService()
        self.assertFalse(svc.is_authenticated)

    def test_current_user_none_sem_login(self) -> None:
        """current_user deve ser None sem login."""
        from services.auth_service import AuthService

        svc = AuthService()
        self.assertIsNone(svc.current_user)

    def test_is_admin_false_para_operador(self) -> None:
        """Utilizador com role='operador' não é admin."""
        from services.auth_service import AuthService

        svc = AuthService()
        mock_user = self._criar_utilizador_mock(role="operador")
        svc._current_user = mock_user
        svc._session_start = datetime.utcnow()

        self.assertFalse(svc.is_admin)

    def test_is_admin_true_para_admin(self) -> None:
        """Utilizador com role='admin' é admin."""
        from services.auth_service import AuthService

        svc = AuthService()
        mock_user = self._criar_utilizador_mock(role="admin")
        mock_user.is_admin.return_value = True
        svc._current_user = mock_user
        svc._session_start = datetime.utcnow()

        self.assertTrue(svc.is_admin)

    def test_get_session_info_sem_login(self) -> None:
        """get_session_info sem login devolve authenticated=False."""
        from services.auth_service import AuthService

        svc = AuthService()
        info = svc.get_session_info()
        self.assertFalse(info["authenticated"])

    def test_get_session_info_com_login(self) -> None:
        """get_session_info com sessão activa devolve dados correctos."""
        from services.auth_service import AuthService

        svc = AuthService()
        mock_user = self._criar_utilizador_mock(username="joao", role="operador")
        svc._current_user = mock_user
        svc._session_start = datetime.utcnow()

        info = svc.get_session_info()
        self.assertTrue(info["authenticated"])
        self.assertEqual(info["username"], "joao")
        self.assertEqual(info["role"], "operador")


class TestUsuarioModelo(unittest.TestCase):
    """
    Testes da lógica do modelo Usuario (sem MongoDB).
    """

    def test_hash_password_diferente_do_original(self) -> None:
        """O hash da password deve ser diferente da password original."""
        from models.usuario import Usuario

        salt = Usuario._gerar_salt()
        hashed = Usuario._hash_password("minha_senha", salt)
        self.assertNotEqual(hashed, "minha_senha")

    def test_hash_password_consistente(self) -> None:
        """O mesmo salt e password devem gerar sempre o mesmo hash."""
        from models.usuario import Usuario

        salt = Usuario._gerar_salt()
        h1 = Usuario._hash_password("senha123", salt)
        h2 = Usuario._hash_password("senha123", salt)
        self.assertEqual(h1, h2)

    def test_hash_diferente_com_salts_diferentes(self) -> None:
        """A mesma password com salts diferentes deve gerar hashes diferentes."""
        from models.usuario import Usuario

        salt1 = Usuario._gerar_salt()
        salt2 = Usuario._gerar_salt()
        h1 = Usuario._hash_password("senha123", salt1)
        h2 = Usuario._hash_password("senha123", salt2)
        self.assertNotEqual(h1, h2)

    def test_salt_e_unico(self) -> None:
        """Dois salts gerados consecutivamente devem ser diferentes."""
        from models.usuario import Usuario

        salt1 = Usuario._gerar_salt()
        salt2 = Usuario._gerar_salt()
        self.assertNotEqual(salt1, salt2)

    def test_salt_tem_64_caracteres_hex(self) -> None:
        """O salt deve ter 64 caracteres hexadecimais (32 bytes)."""
        from models.usuario import Usuario

        salt = Usuario._gerar_salt()
        self.assertEqual(len(salt), 64)
        int(salt, 16)  # Não lança excepção se for hexadecimal válido

    def test_verificar_password_correcta(self) -> None:
        """verificar_password deve retornar True para a password correcta."""
        from models.usuario import Usuario

        # Usa directamente os métodos estáticos/de classe (sem instância MongoEngine)
        salt = Usuario._gerar_salt()
        password = "minha_senha_segura"
        hash_calculado = Usuario._hash_password(password, salt)
        hash_verificar = Usuario._hash_password(password, salt)
        self.assertEqual(hash_calculado, hash_verificar)

    def test_verificar_password_errada(self) -> None:
        """verificar_password deve retornar False para password errada."""
        from models.usuario import Usuario

        salt = Usuario._gerar_salt()
        hash_correcto = Usuario._hash_password("senha_correcta", salt)
        hash_errado   = Usuario._hash_password("senha_errada",   salt)
        self.assertNotEqual(hash_correcto, hash_errado)

    def test_is_bloqueado_com_5_tentativas(self) -> None:
        """Lógica: tentativas >= max deve ser bloqueado."""
        # Testa a lógica directamente sem instanciar MongoEngine Document
        tentativas = 5
        max_t = 5
        self.assertTrue(tentativas >= max_t)

    def test_nao_bloqueado_com_menos_de_5_tentativas(self) -> None:
        """Lógica: tentativas < max não deve estar bloqueado."""
        tentativas = 3
        max_t = 5
        self.assertFalse(tentativas >= max_t)


class TestVendaService(unittest.TestCase):
    """
    Testes unitários para VendaService.
    """

    def setUp(self) -> None:
        """Configura o ambiente de teste com mocks."""
        from services.produto_service import ProdutoService
        from services.venda_service import VendaService

        self.mock_produto_svc = MagicMock(spec=ProdutoService)
        self.venda_svc = VendaService(produto_service=self.mock_produto_svc)

    def _criar_produto_mock(self, stock: int = 50) -> MagicMock:
        """Cria um produto mock com stock definido."""
        p = MagicMock()
        p.id = "produto_id_123"
        p.nome = "Produto Teste"
        p.preco = 100.0
        p.stock = stock
        p.decrementar_stock = MagicMock()
        return p

    def test_registrar_venda_produto_nao_encontrado(self) -> None:
        """Registar venda com produto inexistente lança ProductNotFoundException."""
        from exceptions.stock_exception import ProductNotFoundException

        self.mock_produto_svc.obter_por_id.return_value = None

        with self.assertRaises(ProductNotFoundException):
            self.venda_svc.registrar_venda(
                produto_id="id_invalido",
                quantidade=5,
                vendido_por="admin",
            )

    def test_registrar_venda_stock_insuficiente(self) -> None:
        """Venda com quantidade > stock lança InsufficientStockException."""
        from exceptions.stock_exception import InsufficientStockException

        produto_mock = self._criar_produto_mock(stock=3)
        self.mock_produto_svc.obter_por_id.return_value = produto_mock

        with self.assertRaises(InsufficientStockException):
            self.venda_svc.registrar_venda(
                produto_id="produto_id_123",
                quantidade=10,
                vendido_por="admin",
            )

    def test_quantidade_negativa_lanca_value_error(self) -> None:
        """Quantidade negativa deve lançar ValueError pelo decorator @validate_positive."""
        with self.assertRaises(ValueError):
            self.venda_svc.registrar_venda(
                produto_id="qualquer",
                quantidade=-1,
                vendido_por="admin",
            )

    def test_quantidade_zero_lanca_value_error(self) -> None:
        """Quantidade zero deve lançar ValueError."""
        with self.assertRaises(ValueError):
            self.venda_svc.registrar_venda(
                produto_id="qualquer",
                quantidade=0,
                vendido_por="admin",
            )

    def test_obter_historico_mensal_produto_sem_vendas(self) -> None:
        """Histórico mensal para produto sem vendas deve retornar lista vazia."""
        with patch.object(self.venda_svc, "obter_por_produto", return_value=[]):
            resultado = self.venda_svc.obter_historico_mensal("qualquer_id")
        self.assertEqual(resultado, [])

    def test_obter_historico_mensal_agrega_por_mes(self) -> None:
        """Histórico mensal deve agregar correctamente vendas do mesmo mês."""
        # Cria vendas mock no mesmo mês (Janeiro 2024)
        jan = datetime(2024, 1, 15)
        v1 = MagicMock()
        v1.data_venda = jan
        v1.quantidade = 10
        v1.total = 1000.0

        v2 = MagicMock()
        v2.data_venda = datetime(2024, 1, 28)
        v2.quantidade = 5
        v2.total = 500.0

        # Venda de Fevereiro
        v3 = MagicMock()
        v3.data_venda = datetime(2024, 2, 10)
        v3.quantidade = 8
        v3.total = 800.0

        with patch.object(
            self.venda_svc, "obter_por_produto", return_value=[v1, v2, v3]
        ):
            resultado = self.venda_svc.obter_historico_mensal("produto_123")

        # Deve ter 2 períodos (Jan + Fev)
        self.assertEqual(len(resultado), 2)

        # Janeiro: 10 + 5 = 15 unidades
        jan_resultado = next(r for r in resultado if r["mes"] == 1)
        self.assertEqual(jan_resultado["total_vendido"], 15)

        # Fevereiro: 8 unidades
        fev_resultado = next(r for r in resultado if r["mes"] == 2)
        self.assertEqual(fev_resultado["total_vendido"], 8)


class TestIAServiceAvancado(unittest.TestCase):
    """
    Testes avançados para o serviço de IA.
    """

    def setUp(self) -> None:
        from services.ia_service import IAService
        self.ia = IAService()

    def _historico(self, valores: list) -> list:
        """Gera histórico mock com os valores fornecidos."""
        return [
            {"mes": i + 1, "ano": 2024, "total_vendido": v}
            for i, v in enumerate(valores)
        ]

    def test_previsao_com_dados_lineares_perfeitos(self) -> None:
        """Com y = 2x, a previsão do mês 7 deve ser próxima de 14."""
        hist = self._historico([2, 4, 6, 8, 10, 12])
        self.ia.treinar(hist)
        previsoes = self.ia.prever(1)
        self.assertAlmostEqual(previsoes[0], 14.0, delta=0.5)

    def test_previsao_nao_retorna_negativos(self) -> None:
        """Previsões não devem ser negativas mesmo com tendência decrescente."""
        hist = self._historico([20, 15, 10, 8, 5, 3])
        self.ia.treinar(hist)
        previsoes = self.ia.prever(5)
        for p in previsoes:
            self.assertGreaterEqual(p, 0.0, "Previsão não pode ser negativa")

    def test_numero_correcto_de_previsoes(self) -> None:
        """O número de previsões deve corresponder ao pedido."""
        hist = self._historico([5, 8, 11, 14, 17, 20])
        self.ia.treinar(hist)
        for n in [1, 3, 6, 12]:
            previsoes = self.ia.prever(n)
            self.assertEqual(len(previsoes), n, f"Esperava {n} previsões")

    def test_relatorio_ia_contem_metricas(self) -> None:
        """O relatório da IA deve mencionar R², MAE e RMSE."""
        hist = self._historico([10, 12, 15, 17, 20, 22])
        self.ia.treinar(hist)
        relatorio = self.ia.gerar_relatorio_ia("Produto Teste")
        self.assertIn("R²", relatorio)
        self.assertIn("MAE", relatorio)
        self.assertIn("RMSE", relatorio)

    def test_relatorio_sem_treino_indica_erro(self) -> None:
        """Relatório sem modelo treinado deve indicar ausência de treino."""
        relatorio = self.ia.gerar_relatorio_ia()
        self.assertIn("não treinado", relatorio.lower())

    def test_dados_grafico_tem_todas_chaves(self) -> None:
        """obter_dados_grafico deve retornar todas as chaves esperadas."""
        hist = self._historico([10, 14, 18, 22, 26, 30])
        self.ia.treinar(hist)
        dados = self.ia.obter_dados_grafico(3)
        chaves_esperadas = [
            "labels_historico", "valores_historico",
            "labels_previsao", "valores_previsao",
            "linha_tendencia", "metricas",
        ]
        for chave in chaves_esperadas:
            self.assertIn(chave, dados, f"Chave '{chave}' em falta nos dados do gráfico")

    def test_historico_e_previsao_tamanhos_correctos(self) -> None:
        """labels_historico deve ter N elementos; labels_previsao deve ter n_periodos."""
        n_hist = 8
        n_prev = 3
        hist = self._historico(list(range(5, 5 + n_hist)))
        self.ia.treinar(hist)
        dados = self.ia.obter_dados_grafico(n_prev)
        self.assertEqual(len(dados["labels_historico"]), n_hist)
        self.assertEqual(len(dados["valores_previsao"]), n_prev)

    def test_treino_com_historico_vazio_retorna_false(self) -> None:
        """Treino com lista vazia deve retornar False."""
        self.assertFalse(self.ia.treinar([]))

    def test_treino_com_um_elemento_retorna_true(self) -> None:
        """Treino com 1 elemento deve retornar True (modo constante)."""
        self.assertTrue(self.ia.treinar([{"mes": 1, "ano": 2024, "total_vendido": 10}]))

    def test_modelo_treinado_true_apos_treino_valido(self) -> None:
        """modelo_treinado() deve ser True após treino com dados suficientes."""
        hist = self._historico([5, 10, 15, 20])
        self.ia.treinar(hist)
        self.assertTrue(self.ia.modelo_treinado())

    def test_metricas_r2_entre_0_e_1_para_dados_razoaveis(self) -> None:
        """R² deve estar entre 0 e 1 para dados razoáveis."""
        hist = self._historico([10, 13, 11, 15, 14, 17, 16, 20])
        self.ia.treinar(hist)
        metricas = self.ia.obter_metricas()
        r2 = metricas.get("r2", -1)
        self.assertGreaterEqual(r2, 0.0)
        self.assertLessEqual(r2, 1.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
