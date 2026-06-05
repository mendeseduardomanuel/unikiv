"""
=============================================================================
Ficheiro: interfaces/repository_interface.py
Descrição: Interfaces (contratos) abstractos que definem o comportamento
           esperado de todos os repositórios de dados.
           
POO: Classes Abstractas e Interfaces
     - ABC (Abstract Base Class) define contratos que as subclasses DEVEM implementar.
     - @abstractmethod obriga as subclasses a implementar o método.
     - Polimorfismo: serviços trabalham com a interface, não com implementações concretas.
=============================================================================
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Any, Dict


# =============================================================================
# Interface Base: IRepository
# Define as operações CRUD genéricas para qualquer entidade.
# =============================================================================
class IRepository(ABC):
    """
    Interface base para todos os repositórios de dados.
    
    POO: Classe Abstracta (ABC)
    Define um contrato CRUD genérico. Qualquer classe que herde desta
    interface DEVE implementar todos os métodos abstractos.
    
    Padrão de Projecto: Repository Pattern
    Isola a lógica de acesso a dados da lógica de negócio, permitindo
    trocar o SGBD sem alterar os serviços.
    """

    @abstractmethod
    def criar(self, dados: Dict[str, Any]) -> Any:
        """
        Cria uma nova entidade na base de dados.
        
        Parâmetros:
            dados: Dicionário com os dados da entidade.
            
        Returns:
            A entidade criada.
        """
        ...

    @abstractmethod
    def obter_por_id(self, entity_id: str) -> Optional[Any]:
        """
        Obtém uma entidade pelo seu identificador único.
        
        Parâmetros:
            entity_id: Identificador único (MongoDB ObjectId como string).
            
        Returns:
            A entidade encontrada ou None.
        """
        ...

    @abstractmethod
    def obter_todos(self) -> List[Any]:
        """
        Obtém todas as entidades da colecção.
        
        Returns:
            Lista de todas as entidades.
        """
        ...

    @abstractmethod
    def actualizar(self, entity_id: str, dados: Dict[str, Any]) -> Optional[Any]:
        """
        Actualiza uma entidade existente.
        
        Parâmetros:
            entity_id: Identificador único da entidade.
            dados: Dicionário com os campos a actualizar.
            
        Returns:
            A entidade actualizada ou None se não encontrada.
        """
        ...

    @abstractmethod
    def eliminar(self, entity_id: str) -> bool:
        """
        Elimina uma entidade da base de dados.
        
        Parâmetros:
            entity_id: Identificador único da entidade.
            
        Returns:
            True se eliminada com sucesso, False caso contrário.
        """
        ...

    @abstractmethod
    def pesquisar(self, filtros: Dict[str, Any]) -> List[Any]:
        """
        Pesquisa entidades com base em filtros.
        
        Parâmetros:
            filtros: Dicionário com critérios de pesquisa.
            
        Returns:
            Lista de entidades que correspondem aos filtros.
        """
        ...

    def contar(self, filtros: Optional[Dict[str, Any]] = None) -> int:
        """
        Conta o número de entidades (com filtros opcionais).
        Método não-abstracto com implementação padrão via pesquisar().
        
        Parâmetros:
            filtros: Filtros opcionais.
            
        Returns:
            Número de entidades encontradas.
        """
        resultados = self.pesquisar(filtros or {})
        return len(resultados)


# =============================================================================
# Interface: IProdutoRepository
# Contrato específico para operações de Produto.
# =============================================================================
class IProdutoRepository(IRepository):
    """
    Interface específica para o repositório de produtos.
    Herda as operações CRUD de IRepository e adiciona métodos específicos.
    
    POO: Herança de Interface - IProdutoRepository especializa IRepository.
    """

    @abstractmethod
    def obter_por_nome(self, nome: str) -> Optional[Any]:
        """
        Obtém um produto pelo nome.
        
        Parâmetros:
            nome: Nome exacto do produto.
        """
        ...

    @abstractmethod
    def obter_por_categoria(self, categoria: str) -> List[Any]:
        """
        Obtém todos os produtos de uma categoria.
        
        Parâmetros:
            categoria: Nome da categoria.
        """
        ...

    @abstractmethod
    def obter_com_stock_baixo(self, threshold: int) -> List[Any]:
        """
        Obtém produtos com stock abaixo do limiar definido.
        
        Parâmetros:
            threshold: Quantidade mínima de stock.
        """
        ...

    @abstractmethod
    def actualizar_stock(self, produto_id: str, nova_quantidade: int) -> bool:
        """
        Actualiza apenas o stock de um produto.
        
        Parâmetros:
            produto_id: ID do produto.
            nova_quantidade: Novo valor de stock.
        """
        ...


# =============================================================================
# Interface: IVendaRepository
# Contrato específico para operações de Venda.
# =============================================================================
class IVendaRepository(IRepository):
    """
    Interface específica para o repositório de vendas.
    
    POO: Herança de Interface - IVendaRepository especializa IRepository.
    """

    @abstractmethod
    def obter_por_produto(self, produto_id: str) -> List[Any]:
        """
        Obtém todas as vendas de um produto específico.
        
        Parâmetros:
            produto_id: ID do produto.
        """
        ...

    @abstractmethod
    def obter_por_periodo(self, data_inicio: Any, data_fim: Any) -> List[Any]:
        """
        Obtém vendas num intervalo de datas.
        
        Parâmetros:
            data_inicio: Data de início do período.
            data_fim: Data de fim do período.
        """
        ...

    @abstractmethod
    def obter_historico_mensal(self, produto_id: str) -> List[Dict]:
        """
        Obtém o histórico de vendas mensais de um produto (para a IA).
        
        Parâmetros:
            produto_id: ID do produto.
            
        Returns:
            Lista de dicionários com 'mes', 'ano', 'total_vendido'.
        """
        ...


# =============================================================================
# Interface: IAuthRepository
# Contrato específico para operações de Autenticação.
# =============================================================================
class IAuthRepository(ABC):
    """
    Interface para o repositório de autenticação/utilizadores.
    
    POO: Classe Abstracta independente (não herda IRepository porque
    as operações de auth têm semântica diferente do CRUD padrão).
    """

    @abstractmethod
    def obter_por_username(self, username: str) -> Optional[Any]:
        """
        Obtém um utilizador pelo nome de utilizador.
        
        Parâmetros:
            username: Nome de utilizador (único).
        """
        ...

    @abstractmethod
    def criar_utilizador(self, username: str, password_hash: str, role: str) -> Any:
        """
        Cria um novo utilizador na base de dados.
        
        Parâmetros:
            username: Nome de utilizador.
            password_hash: Hash da palavra-passe.
            role: Papel do utilizador ("admin" | "operador").
        """
        ...

    @abstractmethod
    def verificar_credenciais(self, username: str, password: str) -> Optional[Any]:
        """
        Verifica as credenciais de um utilizador.
        
        Parâmetros:
            username: Nome de utilizador.
            password: Palavra-passe em texto claro.
            
        Returns:
            O utilizador se as credenciais forem válidas, None caso contrário.
        """
        ...


# =============================================================================
# Interface: IIAService
# Contrato para o serviço de Inteligência Artificial.
# =============================================================================
class IIAService(ABC):
    """
    Interface para o serviço de Inteligência Artificial.
    Define o contrato que qualquer implementação de IA deve seguir.
    
    POO: Abstracção - oculta os detalhes do modelo (regressão linear,
    redes neuronais, etc.) atrás de uma interface uniforme.
    """

    @abstractmethod
    def treinar(self, historico: List[Dict]) -> bool:
        """
        Treina o modelo de IA com o histórico de vendas.
        
        Parâmetros:
            historico: Lista de registos com 'mes' e 'quantidade'.
            
        Returns:
            True se o treino foi bem-sucedido.
        """
        ...

    @abstractmethod
    def prever(self, n_periodos: int) -> List[float]:
        """
        Gera previsões para os próximos N períodos.
        
        Parâmetros:
            n_periodos: Número de períodos futuros a prever.
            
        Returns:
            Lista de valores previstos.
        """
        ...

    @abstractmethod
    def obter_metricas(self) -> Dict[str, float]:
        """
        Devolve as métricas de avaliação do modelo treinado.
        
        Returns:
            Dicionário com métricas como 'r2', 'mae', 'rmse'.
        """
        ...

    @abstractmethod
    def modelo_treinado(self) -> bool:
        """
        Indica se o modelo foi treinado e está pronto para previsões.
        
        Returns:
            bool: True se pronto para uso.
        """
        ...
