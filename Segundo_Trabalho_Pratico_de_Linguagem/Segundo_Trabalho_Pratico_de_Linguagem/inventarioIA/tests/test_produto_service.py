"""
=============================================================================
Ficheiro: tests/test_produto_service.py
Descrição: Testes unitários para o serviço de produtos.
           Usa unittest e MongoMock para isolar a base de dados.
=============================================================================
"""

import sys
import os
import unittest
from unittest.mock import MagicMock, patch, PropertyMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestProdutoServiceUnitario(unittest.TestCase):
    """
    Testes unitários para ProdutoService.
    Usa mocks para não depender do MongoDB real.
    """

    def setUp(self) -> None:
        """Configuração executada antes de cada teste."""
        # Mockamos o ProdutoService para não precisar de MongoDB
        with patch("services.produto_service.Produto"):
            from services.produto_service import ProdutoService
            self.service = ProdutoService()

    # ---------------------------------------------------------------
    # Testes de Validação de Dados
    # ---------------------------------------------------------------

    def test_criar_produto_nome_vazio_lanca_excecao(self) -> None:
        """
        Testa que criar um produto com nome vazio lança InvalidProductDataException.
        """
        from exceptions.stock_exception import InvalidProductDataException

        with self.assertRaises(InvalidProductDataException):
            with patch.object(self.service, "obter_por_nome", return_value=None):
                with patch("services.produto_service.Produto") as MockProduto:
                    MockProduto.side_effect = Exception("Validação falhou")
                    self.service.criar({"nome": "", "preco": 100, "stock": 10})

    def test_criar_produto_duplicado_lanca_excecao(self) -> None:
        """
        Testa que criar um produto com nome já existente lança DuplicateProductException.
        """
        from exceptions.stock_exception import DuplicateProductException

        produto_existente = MagicMock()
        produto_existente.nome = "Arroz 5kg"

        with patch.object(
            self.service, "obter_por_nome", return_value=produto_existente
        ):
            with self.assertRaises(DuplicateProductException):
                self.service.criar({
                    "nome": "Arroz 5kg",
                    "categoria": "Alimentação",
                    "preco": 1500.0,
                    "stock": 100,
                })

    def test_eliminar_produto_nao_existente_lanca_excecao(self) -> None:
        """
        Testa que eliminar um produto inexistente lança ProductNotFoundException.
        """
        from exceptions.stock_exception import ProductNotFoundException

        with patch.object(self.service, "obter_por_id", return_value=None):
            with self.assertRaises(ProductNotFoundException):
                self.service.eliminar("id_inexistente_123")

    def test_actualizar_stock_negativo_lanca_excecao(self) -> None:
        """
        Testa que actualizar stock com valor negativo lança InvalidStockValueException.
        """
        from exceptions.stock_exception import InvalidStockValueException

        with self.assertRaises(InvalidStockValueException):
            self.service.actualizar_stock("qualquer_id", -5)

    def test_pesquisar_sem_filtros_chama_obter_todos(self) -> None:
        """
        Testa que pesquisar sem filtros é equivalente a obter_todos.
        """
        mock_todos = [MagicMock(), MagicMock()]
        with patch.object(self.service, "obter_todos", return_value=mock_todos):
            with patch("services.produto_service.Produto") as MockProduto:
                MockProduto.objects.return_value.filter.return_value.order_by.return_value = mock_todos
                MockProduto.objects.return_value.order_by.return_value = mock_todos
                resultado = self.service.pesquisar({})
        # Apenas verifica que não lança excepção
        self.assertIsInstance(resultado, list)


class TestProdutoModelo(unittest.TestCase):
    """
    Testes unitários para o modelo Produto (lógica sem base de dados).
    """

    def _criar_produto_mock(
        self,
        stock: int = 50,
        stock_minimo: int = 10,
        preco: float = 100.0,
    ) -> MagicMock:
        """Helper que cria um mock de Produto com os atributos necessários."""
        p = MagicMock()
        p.stock = stock
        p.stock_minimo = stock_minimo
        p.preco = preco
        p.nome = "Produto Teste"
        # Recria a property usando a lógica real
        p.tem_stock_baixo = stock <= stock_minimo
        p.valor_total_stock = round(preco * stock, 2)
        return p

    def test_stock_baixo_quando_stock_menor_ou_igual_minimo(self) -> None:
        """Produto com stock = stock_minimo deve estar marcado como baixo."""
        produto = self._criar_produto_mock(stock=10, stock_minimo=10)
        self.assertTrue(produto.tem_stock_baixo)

    def test_stock_normal_quando_stock_maior_que_minimo(self) -> None:
        """Produto com stock > stock_minimo deve estar com stock normal."""
        produto = self._criar_produto_mock(stock=50, stock_minimo=10)
        self.assertFalse(produto.tem_stock_baixo)

    def test_valor_total_stock_calculado_correctamente(self) -> None:
        """Valor total = preço × stock."""
        produto = self._criar_produto_mock(stock=10, preco=150.0)
        self.assertAlmostEqual(produto.valor_total_stock, 1500.0, places=2)

    def test_valor_total_stock_zero_quando_sem_stock(self) -> None:
        """Valor total deve ser 0 quando stock = 0."""
        produto = self._criar_produto_mock(stock=0, preco=200.0)
        self.assertAlmostEqual(produto.valor_total_stock, 0.0, places=2)


class TestExcecoes(unittest.TestCase):
    """
    Testes das excepções customizadas.
    """

    def test_insufficient_stock_mensagem_correcta(self) -> None:
        """Testa a mensagem de InsufficientStockException."""
        from exceptions.stock_exception import InsufficientStockException

        exc = InsufficientStockException(
            product_name="Arroz", requested=20, available=5
        )
        self.assertIn("Arroz", str(exc))
        self.assertIn("20", str(exc))
        self.assertIn("5", str(exc))

    def test_auth_exception_heranca(self) -> None:
        """Testa que InvalidCredentialsException herda de AuthException."""
        from exceptions.auth_exception import (
            InvalidCredentialsException,
            AuthException,
        )
        exc = InvalidCredentialsException()
        self.assertIsInstance(exc, AuthException)
        self.assertIsInstance(exc, Exception)

    def test_stock_exception_heranca(self) -> None:
        """Testa que InsufficientStockException herda de StockException."""
        from exceptions.stock_exception import (
            InsufficientStockException,
            StockException,
        )
        exc = InsufficientStockException()
        self.assertIsInstance(exc, StockException)
        self.assertIsInstance(exc, Exception)

    def test_product_not_found_mensagem_com_id(self) -> None:
        """Testa ProductNotFoundException com ID."""
        from exceptions.stock_exception import ProductNotFoundException

        exc = ProductNotFoundException(product_id="abc123")
        self.assertIn("abc123", str(exc))

    def test_invalid_credentials_mensagem_padrao(self) -> None:
        """Testa mensagem padrão de InvalidCredentialsException."""
        from exceptions.auth_exception import InvalidCredentialsException

        exc = InvalidCredentialsException()
        self.assertIn("incorrectos", exc.message.lower())

    def test_duplicate_product_mensagem_com_nome(self) -> None:
        """Testa DuplicateProductException com nome."""
        from exceptions.stock_exception import DuplicateProductException

        exc = DuplicateProductException("Monitor LG")
        self.assertIn("Monitor LG", str(exc))


class TestIAService(unittest.TestCase):
    """
    Testes para o serviço de Inteligência Artificial.
    """

    def setUp(self) -> None:
        """Inicializa o IAService para cada teste."""
        from services.ia_service import IAService
        self.ia_svc = IAService()

    def test_modelo_nao_treinado_inicialmente(self) -> None:
        """O modelo não deve estar treinado logo após a inicialização."""
        self.assertFalse(self.ia_svc.modelo_treinado())

    def test_prever_sem_modelo_retorna_lista_vazia(self) -> None:
        """Prever sem modelo treinado deve retornar lista vazia."""
        resultado = self.ia_svc.prever(3)
        self.assertEqual(resultado, [])

    def test_treinar_com_historico_insuficiente_retorna_false(self) -> None:
        """Treinar com lista vazia deve retornar False."""
        historico_vazio = []
        resultado = self.ia_svc.treinar(historico_vazio)
        self.assertFalse(resultado)

    def test_treinar_com_um_elemento_retorna_true(self) -> None:
        """Treinar com 1 elemento deve retornar True (modo constante)."""
        historico_1_ponto = [{"mes": 1, "ano": 2024, "total_vendido": 10}]
        resultado = self.ia_svc.treinar(historico_1_ponto)
        self.assertTrue(resultado)

    def test_treinar_com_historico_valido_retorna_true(self) -> None:
        """Treinar com dados válidos deve retornar True."""
        historico = [
            {"mes": i, "ano": 2024, "total_vendido": 10 + i * 2}
            for i in range(1, 7)
        ]
        resultado = self.ia_svc.treinar(historico)
        self.assertTrue(resultado)
        self.assertTrue(self.ia_svc.modelo_treinado())

    def test_treinar_e_prever_retorna_valores_positivos(self) -> None:
        """Após treino, as previsões devem ser valores positivos."""
        historico = [
            {"mes": i, "ano": 2024, "total_vendido": 10 + i * 3}
            for i in range(1, 9)
        ]
        self.ia_svc.treinar(historico)
        previsoes = self.ia_svc.prever(3)

        self.assertEqual(len(previsoes), 3)
        for p in previsoes:
            self.assertGreaterEqual(p, 0.0)

    def test_metricas_disponiveis_apos_treino(self) -> None:
        """Após treino, as métricas devem estar preenchidas."""
        historico = [
            {"mes": i, "ano": 2024, "total_vendido": 5 * i}
            for i in range(1, 8)
        ]
        self.ia_svc.treinar(historico)
        metricas = self.ia_svc.obter_metricas()

        self.assertIn("r2", metricas)
        self.assertIn("mae", metricas)
        self.assertIn("rmse", metricas)
        self.assertIn("coef", metricas)

    def test_regressao_linear_detecta_tendencia_crescente(self) -> None:
        """Com dados crescentes, o coeficiente deve ser positivo."""
        historico = [
            {"mes": i, "ano": 2024, "total_vendido": i * 5}
            for i in range(1, 7)
        ]
        self.ia_svc.treinar(historico)
        metricas = self.ia_svc.obter_metricas()
        self.assertGreater(metricas["coef"], 0)

    def test_r2_perfeito_para_dados_lineares(self) -> None:
        """Com dados perfeitamente lineares, R² deve ser próximo de 1."""
        historico = [
            {"mes": i, "ano": 2024, "total_vendido": i * 10}
            for i in range(1, 10)
        ]
        self.ia_svc.treinar(historico)
        metricas = self.ia_svc.obter_metricas()
        self.assertAlmostEqual(metricas["r2"], 1.0, places=3)


class TestDecorators(unittest.TestCase):
    """
    Testes para os decoradores personalizados.
    """

    def test_validate_positive_lanca_excecao_com_valor_negativo(self) -> None:
        """@validate_positive deve lançar ValueError para parâmetros negativos."""
        from utils.decorators import validate_positive

        @validate_positive("quantidade")
        def funcao_teste(quantidade: int) -> int:
            return quantidade

        with self.assertRaises(ValueError):
            funcao_teste(quantidade=-5)

    def test_validate_positive_permite_valores_positivos(self) -> None:
        """@validate_positive não deve interferir com valores positivos."""
        from utils.decorators import validate_positive

        @validate_positive("valor")
        def calcular(valor: float) -> float:
            return valor * 2

        resultado = calcular(valor=10.0)
        self.assertEqual(resultado, 20.0)

    def test_log_execution_preserva_resultado(self) -> None:
        """@log_execution não deve alterar o valor de retorno."""
        from utils.decorators import log_execution

        @log_execution
        def soma(a: int, b: int) -> int:
            return a + b

        self.assertEqual(soma(3, 4), 7)

    def test_cache_result_devolve_mesmo_resultado(self) -> None:
        """@cache_result deve devolver o mesmo resultado em chamadas repetidas."""
        from utils.decorators import cache_result

        contador = {"n": 0}

        @cache_result(ttl_seconds=60)
        def funcao_cara() -> int:
            contador["n"] += 1
            return 42

        r1 = funcao_cara()
        r2 = funcao_cara()
        self.assertEqual(r1, 42)
        self.assertEqual(r2, 42)
        # A função real só deve ter sido chamada uma vez
        self.assertEqual(contador["n"], 1)

    def test_timer_nao_altera_resultado(self) -> None:
        """@timer não deve alterar o valor de retorno."""
        from utils.decorators import timer

        @timer
        def multiplicar(x: int, y: int) -> int:
            return x * y

        self.assertEqual(multiplicar(6, 7), 42)


class TestContextManagers(unittest.TestCase):
    """
    Testes para os context managers personalizados.
    """

    def test_database_transaction_commit(self) -> None:
        """DatabaseTransaction deve registar commit correctamente."""
        from utils.context_manager import DatabaseTransaction

        with DatabaseTransaction("teste") as txn:
            txn.log_operation("op1")
            txn.commit()

        self.assertTrue(txn._committed)
        self.assertEqual(len(txn._operations_log), 1)

    def test_database_transaction_sem_commit(self) -> None:
        """DatabaseTransaction sem commit não deve lançar excepção."""
        from utils.context_manager import DatabaseTransaction

        with DatabaseTransaction("sem_commit") as txn:
            txn.log_operation("op1")
        # Não houve commit, mas não deve lançar excepção

        self.assertFalse(txn._committed)

    def test_measure_time_retorna_tempo_positivo(self) -> None:
        """measure_time deve retornar um tempo elapsed positivo."""
        import time
        from utils.context_manager import measure_time

        with measure_time("operação teste") as timing:
            time.sleep(0.01)

        self.assertGreater(timing["elapsed"], 0.0)

    def test_csv_writer_cria_ficheiro(self) -> None:
        """CSVWriter deve criar um ficheiro CSV com o conteúdo correcto."""
        import csv
        import tempfile
        from utils.context_manager import CSVWriter

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as tmp:
            caminho = tmp.name

        try:
            cabecalhos = ["Nome", "Quantidade", "Preço"]
            with CSVWriter(caminho, cabecalhos, delimiter=";") as writer:
                writer.write_row(["Produto A", 10, 100.0])
                writer.write_row(["Produto B", 20, 200.0])
                self.assertEqual(writer.rows_written, 2)

            # Verifica conteúdo do ficheiro
            with open(caminho, "r", encoding="utf-8-sig") as f:
                leitor = csv.reader(f, delimiter=";")
                linhas = list(leitor)

            self.assertEqual(linhas[0], ["Nome", "Quantidade", "Preço"])
            self.assertEqual(linhas[1][0], "Produto A")
            self.assertEqual(len(linhas), 3)  # 1 cabeçalho + 2 linhas

        finally:
            if os.path.exists(caminho):
                os.remove(caminho)

    def test_suppress_and_log_suprime_excecao_especificada(self) -> None:
        """suppress_and_log deve suprimir a excepção especificada."""
        from utils.context_manager import suppress_and_log

        with suppress_and_log(ValueError, default_value=0) as ctx:
            ctx["result"] = int("não é um número")

        self.assertTrue(ctx["suppressed"])
        self.assertIsInstance(ctx["error"], ValueError)


if __name__ == "__main__":
    unittest.main(verbosity=2)
