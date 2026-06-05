# 📦 InventárioIA
## Sistema Inteligente de Gestão de Inventário com Previsão de Demanda

> **Instituto Politécnico - UNIKIVI** | Departamento de Engenharia Informática  
> Linguagem de Programação VI (Python) | Trabalho Prático — Avaliação Contínua  
> Docente: Moyo Kanivengidio | Ano Lectivo: 2026

---

## 📋 Índice

1. [Descrição do Projecto](#1-descrição-do-projecto)
2. [Objectivos](#2-objectivos)
3. [Funcionalidades](#3-funcionalidades)
4. [Tecnologias Utilizadas](#4-tecnologias-utilizadas)
5. [Arquitectura do Sistema](#5-arquitectura-do-sistema)
6. [Estrutura de Pastas](#6-estrutura-de-pastas)
7. [Pré-requisitos](#7-pré-requisitos)
8. [Instalação do MongoDB](#8-instalação-do-mongodb)
9. [Configuração do MongoDB](#9-configuração-do-mongodb)
10. [Instalação das Dependências Python](#10-instalação-das-dependências-python)
11. [Como Executar](#11-como-executar)
12. [Manual do Utilizador](#12-manual-do-utilizador)
13. [Fluxo do Sistema](#13-fluxo-do-sistema)
14. [Diagrama UML (Textual)](#14-diagrama-uml-textual)
15. [Diagrama da Base de Dados](#15-diagrama-da-base-de-dados)
16. [Conceitos de POO Aplicados](#16-conceitos-de-poo-aplicados)
17. [Explicação da Inteligência Artificial](#17-explicação-da-inteligência-artificial)
18. [Explicação do MongoEngine](#18-explicação-do-mongoengine)
19. [Screenshots Esperados](#19-screenshots-esperados)
20. [Testes Unitários](#20-testes-unitários)
21. [Padrões de Projecto Utilizados](#21-padrões-de-projecto-utilizados)
22. [Melhorias Futuras](#22-melhorias-futuras)
23. [Solução de Erros Comuns](#23-solução-de-erros-comuns)
24. [Dependências Detalhadas](#24-dependências-detalhadas)
25. [Referências Bibliográficas](#25-referências-bibliográficas)

---

## 1. Descrição do Projecto

O **InventárioIA** é uma aplicação desktop completa desenvolvida em Python que integra:

- **Gestão de Inventário**: controlo total de produtos, categorias e stock.
- **Registo de Vendas**: histórico de transacções com actualização automática de stock.
- **Inteligência Artificial**: previsão de demanda futura por Regressão Linear (scikit-learn).
- **Interface Gráfica Moderna**: dashboard responsivo com gráficos (CustomTkinter + Matplotlib).
- **Base de Dados MongoDB**: persistência fiável via ODM MongoEngine.

O sistema permite que gestores de inventário tomem decisões baseadas em dados históricos de vendas, antecipando a procura futura e evitando rupturas de stock.

---

## 2. Objectivos

### 2.1 Objectivo Geral
Desenvolver uma aplicação desktop completa em Python para gestão inteligente de inventário, demonstrando proficiência em POO avançada, GUI, base de dados NoSQL e IA.

### 2.2 Objectivos Específicos

| # | Objectivo | Tecnologia |
|---|-----------|------------|
| 1 | POO avançada (Herança, Polimorfismo, Encapsulamento, ABC) | Python 3.12 |
| 2 | Interface Gráfica moderna com dashboard | CustomTkinter |
| 3 | Persistência de dados com ODM | MongoEngine + MongoDB |
| 4 | Módulo de IA para previsão de demanda | scikit-learn |
| 5 | Gráficos interactivos | Matplotlib |
| 6 | Boas práticas (PEP 8, Design Patterns) | Python |

---

## 3. Funcionalidades

### 🔐 Autenticação
- Login com username e password (SHA-256 + salt)
- Controlo de tentativas falhadas (bloqueio automático)
- Gestão de sessão com expiração configurável
- Papéis de utilizador: `admin` e `operador`

### 🏠 Dashboard
- Cartões de KPI: total de produtos, stock baixo, receita total, previsão IA
- Gráfico de receita mensal (últimos 6 meses) com linha de tendência
- Lista de produtos com stock baixo em tempo real
- Relógio integrado com data/hora

### 📦 Gestão de Produtos (CRUD Completo)
- **Criar** produto com validação completa de dados
- **Listar** todos os produtos em tabela com cores por estado de stock
- **Pesquisar** por nome (texto parcial) e filtrar por categoria
- **Editar** todos os campos via diálogo modal
- **Eliminar** (lógico — mantém histórico de vendas)
- Indicadores visuais: Normal / Baixo / Crítico / Sem Stock

### 🛒 Módulo de Vendas
- Registo de venda com selector de produto e ajuste de quantidade
- Actualização automática e atómica do stock (Context Manager)
- Confirmação antes de registar
- Histórico completo de vendas em tabela
- Estatísticas: vendas hoje, este mês, receita total

### 🤖 Módulo de IA — Previsão de Demanda
- Selecção de produto para análise individual
- Treino do modelo Regressão Linear com histórico de vendas
- Gráfico combinado: histórico (barras) + tendência (linha) + previsão (barras roxas)
- Métricas: R², MAE, RMSE, coeficiente, tendência
- Relatório textual detalhado com interpretação
- Persistência do modelo treinado (pickle)

### 📊 Relatórios
- Gráfico de pizza: distribuição de produtos por categoria
- Gráfico de barras: top 5 produtos com mais stock
- Painel de estatísticas resumidas
- Exportação para CSV: produtos e vendas (com diálogo de ficheiro)

---

## 4. Tecnologias Utilizadas

| Camada | Tecnologia | Versão | Função |
|--------|------------|--------|--------|
| Linguagem | Python | 3.12+ | Base do projecto |
| GUI | CustomTkinter | 5.2.2 | Interface moderna |
| Gráficos | Matplotlib | 3.8.4 | Visualizações no dashboard |
| Base de Dados | MongoDB | 7.x | Armazenamento de dados |
| ODM | MongoEngine | 0.27.0 | Mapeamento OOP ↔ MongoDB |
| IA | scikit-learn | 1.4.2 | Regressão Linear |
| Numérico | NumPy | 1.26.4 | Vectores e cálculo |
| Imagens | Pillow | 10.3.0 | Suporte CustomTkinter |

---

## 5. Arquitectura do Sistema

O sistema segue a arquitectura em **camadas** com separação clara de responsabilidades:

```
┌────────────────────────────────────────────────────────────┐
│                     CAMADA DE APRESENTAÇÃO                  │
│          CustomTkinter + Matplotlib (gui/)                  │
├────────────────────────────────────────────────────────────┤
│                     CAMADA DE SERVIÇOS                      │
│     AuthService | ProdutoService | VendaService | IAService │
│                     (services/)                             │
├────────────────────────────────────────────────────────────┤
│                    CAMADA DE INTERFACES                     │
│    IRepository | IProdutoRepository | IVendaRepository      │
│                    (interfaces/)                            │
├────────────────────────────────────────────────────────────┤
│                      CAMADA DE MODELOS                      │
│            Usuario | Produto | Venda (models/)              │
├────────────────────────────────────────────────────────────┤
│                    CAMADA DE BASE DE DADOS                  │
│              MongoEngine ODM + MongoDB (database/)          │
└────────────────────────────────────────────────────────────┘
```

---

## 6. Estrutura de Pastas

```
inventarioIA/
│
├── main.py                     # Ponto de entrada da aplicação
│
├── config/
│   ├── __init__.py
│   └── settings.py             # Configurações globais (DB, GUI, IA, negócio)
│
├── database/
│   ├── __init__.py
│   └── connection.py           # Singleton de ligação ao MongoDB
│
├── models/
│   ├── __init__.py
│   ├── usuario.py              # Modelo MongoEngine: utilizador + autenticação
│   ├── produto.py              # Modelo MongoEngine: produto + lógica de stock
│   └── venda.py                # Modelo MongoEngine: venda + referência ao produto
│
├── interfaces/
│   ├── __init__.py
│   └── repository_interface.py # Classes Abstractas (ABC): contratos de repositório
│
├── services/
│   ├── __init__.py
│   ├── auth_service.py         # Lógica de autenticação e gestão de sessão
│   ├── produto_service.py      # CRUD de produtos + estatísticas
│   ├── venda_service.py        # Registo de vendas + histórico + agregações
│   └── ia_service.py           # Treino IA, previsão, métricas, relatório
│
├── gui/
│   ├── __init__.py
│   ├── login_window.py         # Ecrã de autenticação
│   ├── dashboard.py            # Janela principal + sidebar + navegação
│   ├── dashboard_widgets.py    # Cartões KPI + gráfico de vendas + stock baixo
│   ├── produto_view.py         # CRUD completo de produtos + formulário modal
│   ├── venda_view.py           # Registo de vendas + histórico
│   ├── ia_view.py              # Módulo IA: treino, gráfico, métricas
│   └── relatorio_view.py       # Relatórios + gráficos + exportação CSV
│
├── exceptions/
│   ├── __init__.py
│   ├── auth_exception.py       # Hierarquia de excepções de autenticação
│   └── stock_exception.py      # Hierarquia de excepções de stock/inventário
│
├── utils/
│   ├── __init__.py
│   ├── decorators.py           # Decoradores: log, retry, timer, validate, cache
│   └── context_manager.py      # Context managers: transacção, CSV, timer, suppress
│
├── reports/                    # Pasta para ficheiros exportados e modelo IA
│
├── logs/                       # Ficheiros de log (criados automaticamente)
│
├── tests/
│   ├── __init__.py
│   └── test_produto_service.py # Testes unitários (unittest)
│
├── requirements.txt            # Dependências Python
└── README.md                   # Esta documentação
```

### Descrição de cada pasta

| Pasta | Propósito |
|-------|-----------|
| `config/` | Centraliza todas as configurações da aplicação. Modificar aqui para alterar comportamento global. |
| `database/` | Única responsabilidade: gerir a ligação ao MongoDB (padrão Singleton). |
| `models/` | Representação das entidades de negócio como classes MongoEngine. |
| `interfaces/` | Define contratos (ABC) que os serviços devem respeitar. Permite substituir implementações sem alterar outros módulos. |
| `services/` | Contém toda a lógica de negócio. Cada serviço é independente e testável. |
| `gui/` | Módulos de interface gráfica. Cada ficheiro representa um ecrã/módulo da aplicação. |
| `exceptions/` | Hierarquias de excepções customizadas para tratamento de erros semântico. |
| `utils/` | Utilitários reutilizáveis: decoradores e context managers. |
| `tests/` | Testes unitários automatizados. |
| `reports/` | Destino de ficheiros CSV exportados e modelo IA serializado. |
| `logs/` | Ficheiros de log gerados automaticamente. |

---

## 7. Pré-requisitos

- **Python 3.12** ou superior
- **MongoDB 7.x** (Community Edition)
- **pip** (gestor de pacotes Python)
- Sistema operativo: Windows 10+, macOS 12+, ou Ubuntu 22.04+
- RAM mínima: 4 GB
- Espaço em disco: 500 MB

---

## 8. Instalação do MongoDB

### Windows

1. Aceda a: https://www.mongodb.com/try/download/community
2. Seleccione: `MongoDB 7.x` → `Windows` → `msi`
3. Execute o instalador e seleccione **Complete**
4. Marque a opção **Install MongoDB as a Service**
5. Opcionalmente instale o **MongoDB Compass** (interface gráfica)

```powershell
# Verificar se está instalado:
mongod --version
# Deve mostrar: db version v7.x.x
```

### Ubuntu / Debian

```bash
# Importar a chave GPG oficial
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
  sudo gpg --dearmor -o /usr/share/keyrings/mongodb-server-7.0.gpg

# Adicionar o repositório
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] \
  https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | \
  sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# Instalar
sudo apt-get update
sudo apt-get install -y mongodb-org

# Iniciar o serviço
sudo systemctl start mongod
sudo systemctl enable mongod  # Iniciar automaticamente no boot
```

### macOS

```bash
# Com Homebrew:
brew tap mongodb/brew
brew update
brew install mongodb-community@7.0

# Iniciar o serviço:
brew services start mongodb-community@7.0
```

---

## 9. Configuração do MongoDB

### 9.1 Iniciar o MongoDB manualmente (se não estiver como serviço)

```bash
# Windows (PowerShell como Administrador):
mkdir C:\data\db
mongod --dbpath C:\data\db

# Linux/macOS:
mkdir -p ~/data/db
mongod --dbpath ~/data/db
```

### 9.2 Verificar se o MongoDB está a correr

```bash
# Em qualquer SO, num terminal separado:
mongosh
# Deve aparecer o prompt: test>
# Para sair: quit()
```

### 9.3 A base de dados é criada automaticamente

Ao executar a aplicação pela primeira vez, o MongoDB cria automaticamente a base de dados `inventario_ia_db` com as seguintes colecções:

| Colecção | Descrição |
|----------|-----------|
| `usuarios` | Utilizadores do sistema |
| `produtos` | Catálogo de produtos |
| `vendas` | Histórico de transacções |

### 9.4 Configuração da ligação (opcional)

Para alterar o servidor MongoDB, edite o ficheiro `config/settings.py`:

```python
MONGO_HOST = "localhost"   # Endereço do servidor
MONGO_PORT = 27017         # Porta padrão MongoDB
MONGO_DATABASE = "inventario_ia_db"  # Nome da base de dados
```

---

## 10. Instalação das Dependências Python

```bash
# 1. Clone ou descomprima o projecto
cd inventarioIA

# 2. (Recomendado) Crie um ambiente virtual
python -m venv venv

# Activar no Windows:
venv\Scripts\activate

# Activar no Linux/macOS:
source venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Verificar instalação
python -c "import customtkinter; import mongoengine; import sklearn; print('OK')"
```

---

## 11. Como Executar

```bash
# Com o MongoDB em execução e o ambiente virtual activo:
python main.py
```

A aplicação irá:
1. Configurar o sistema de logging.
2. Conectar ao MongoDB.
3. Criar o utilizador administrador padrão (se não existir).
4. Abrir a janela de login.

---

## 12. Manual do Utilizador

### 12.1 Login

1. Abra a aplicação com `python main.py`.
2. No ecrã de login, introduza:
   - **Utilizador**: `admin`
   - **Palavra-passe**: `admin123`
3. Clique em **Entrar no Sistema** ou pressione `Enter`.

> ⚠️ **Altere a palavra-passe do admin após o primeiro login!**

### 12.2 Criar novo Produto

1. No menu lateral, clique em **📦 Produtos**.
2. Clique no botão **➕ Novo Produto**.
3. Preencha o formulário:
   - **Nome**: nome único do produto (obrigatório)
   - **Categoria**: seleccione da lista ou escreva uma nova
   - **Preço**: preço unitário em AOA
   - **Stock**: quantidade inicial disponível
   - **Stock Mínimo**: nível que activa o alerta de stock baixo (padrão: 10)
   - **Descrição**: opcional
4. Clique em **💾 Adicionar Produto**.

### 12.3 Registar uma Venda

1. No menu lateral, clique em **🛒 Vendas**.
2. No painel esquerdo:
   - Seleccione o produto no menu pendente.
   - Ajuste a quantidade com os botões **+** e **−** ou escreva directamente.
   - Adicione observações opcionais.
3. Clique em **✓ Registar Venda**.
4. Confirme o diálogo de confirmação.
5. O stock do produto é automaticamente decrementado.

### 12.4 Executar a Previsão com IA

1. No menu lateral, clique em **🤖 IA Previsão**.
2. Seleccione o produto no menu pendente.
   - *Nota: é necessário ter pelo menos 2 meses de histórico de vendas.*
3. Clique em **▶ Treinar Modelo**.
4. Aguarde o processamento (pode demorar alguns segundos).
5. O sistema exibe:
   - **Gráfico**: histórico real + linha de tendência + barras de previsão futura.
   - **Métricas**: R², MAE, RMSE, tendência mensal.
   - **Relatório**: texto detalhado com interpretação das métricas.

### 12.5 Gerar Relatórios e Exportar CSV

1. No menu lateral, clique em **📊 Relatórios**.
2. Visualize os gráficos e estatísticas.
3. Para exportar:
   - **📥 Exportar Produtos (CSV)**: exporta o inventário completo.
   - **📥 Exportar Vendas (CSV)**: exporta o histórico de vendas.
4. Escolha o caminho de destino no diálogo de ficheiro.
5. O ficheiro CSV pode ser aberto no Microsoft Excel ou LibreOffice Calc.

---

## 13. Fluxo do Sistema

```
┌──────────┐    login()     ┌─────────────┐
│  Login   │ ─────────────► │  Dashboard  │
└──────────┘                └──────┬──────┘
                                   │
            ┌──────────────────────┼──────────────────────┐
            │                      │                       │
            ▼                      ▼                       ▼
    ┌──────────────┐    ┌──────────────────┐    ┌──────────────────┐
    │  Produtos    │    │     Vendas        │    │   IA Previsão    │
    │  ─────────── │    │  ───────────────  │    │  ─────────────── │
    │  + Criar     │    │  + Registar       │    │  + Selec. Prod.  │
    │  + Listar    │    │  + Histórico      │    │  + Treinar       │
    │  + Editar    │    │  + Estatísticas   │    │  + Ver gráfico   │
    │  + Eliminar  │    │  + Stock auto ↓   │    │  + Métricas      │
    └──────────────┘    └──────────────────┘    └──────────────────┘
                                                         │
                                                ┌────────▼────────┐
                                                │   Relatórios     │
                                                │  ─────────────── │
                                                │  + Estatísticas  │
                                                │  + Gráficos      │
                                                │  + Export CSV    │
                                                └─────────────────┘
```

---

## 14. Diagrama UML (Textual)

```
┌──────────────────────────────────────────────────────────────┐
│                     <<abstract>>  IRepository                 │
│  + criar(dados): Any                                          │
│  + obter_por_id(id): Optional[Any]                           │
│  + obter_todos(): List[Any]                                   │
│  + actualizar(id, dados): Optional[Any]                      │
│  + eliminar(id): bool                                        │
│  + pesquisar(filtros): List[Any]                             │
└──────────────────────┬───────────────────────────────────────┘
                       │ herda
          ┌────────────┴──────────────┐
          │                           │
          ▼                           ▼
┌─────────────────────┐    ┌──────────────────────┐
│ <<abstract>>        │    │ <<abstract>>          │
│ IProdutoRepository  │    │ IVendaRepository      │
│ ──────────────────  │    │ ──────────────────    │
│ + obter_por_nome()  │    │ + obter_por_produto() │
│ + obter_categoria() │    │ + obter_por_periodo() │
│ + stock_baixo()     │    │ + historico_mensal()  │
│ + actualizar_stock()│    └────────────┬─────────┘
└─────────┬───────────┘                 │
          │ implementa                   │ implementa
          ▼                             ▼
┌─────────────────────┐    ┌──────────────────────┐
│   ProdutoService    │    │    VendaService       │
│ ──────────────────  │    │ ──────────────────    │
│ - produto_svc       │    │ - produto_svc: Prod.  │
│ + criar()           │    │ + registrar_venda()   │
│ + obter_todos()     │    │ + obter_historico()   │
│ + pesquisar()       │    │ + estatisticas()      │
│ + estatisticas()    │◄───│                       │
└─────────────────────┘    └──────────────────────┘

┌─────────────────────┐    ┌──────────────────────┐
│     AuthService     │    │      IAService        │
│ ──────────────────  │    │ ──────────────────    │
│ - _current_user     │    │ - _modelo             │
│ - _session_start    │    │ - _metricas           │
│ + verificar_cred()  │    │ + treinar()           │
│ + logout()          │    │ + prever()            │
│ + current_user      │    │ + obter_metricas()    │
└─────────────────────┘    └──────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                     MODELOS (MongoEngine)                     │
├─────────────────┬──────────────────┬────────────────────────┤
│    Usuario      │     Produto      │        Venda           │
│ ─────────────── │ ───────────────  │ ──────────────────     │
│ + username      │ + nome           │ + produto: Produto (R) │
│ + password_hash │ + categoria      │ + quantidade           │
│ + salt          │ + preco          │ + preco_unitario       │
│ + role          │ + stock          │ + total                │
│ + ativo         │ + stock_minimo   │ + vendido_por          │
│ ─────────────── │ + descricao      │ + data_venda           │
│ + verificar_pw()│ ───────────────  │ ──────────────────     │
│ + criar_util()  │ + decrementar()  │ + criar_venda()        │
│                 │ + stock_baixo    │ + to_dict()            │
└─────────────────┴──────────────────┴────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   HIERARQUIA DE EXCEPÇÕES                    │
├─────────────────────────┬───────────────────────────────────┤
│      AuthException      │       StockException              │
│ ──────────────────────  │ ─────────────────────────────     │
│  InvalidCredentials     │  InsufficientStockException       │
│  UserNotFoundException  │  LowStockWarningException         │
│  UserAlreadyExists      │  ProductNotFoundException         │
│  SessionExpired         │  InvalidStockValueException       │
│  MaxLoginAttempts       │  InvalidProductDataException      │
│  InsufficientPerms      │  DuplicateProductException        │
└─────────────────────────┴───────────────────────────────────┘
```

---

## 15. Diagrama da Base de Dados

```
MongoDB — Base de Dados: inventario_ia_db

┌─────────────────────────────────────┐
│           COLECÇÃO: usuarios         │
├─────────────────────────────────────┤
│ _id          : ObjectId (PK)        │
│ username     : String (UNIQUE)      │
│ password_hash: String               │
│ salt         : String               │
│ nome_completo: String               │
│ role         : String ["admin","op"]│
│ ativo        : Boolean              │
│ tentativas_login: Integer           │
│ ultimo_login : DateTime             │
│ criado_em    : DateTime             │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│           COLECÇÃO: produtos         │
├─────────────────────────────────────┤
│ _id          : ObjectId (PK)        │
│ nome         : String (UNIQUE)      │
│ categoria    : String               │
│ preco        : Float                │
│ stock        : Integer              │
│ stock_minimo : Integer              │
│ descricao    : String               │
│ ativo        : Boolean              │
│ criado_em    : DateTime             │
│ atualizado_em: DateTime             │
└──────────────────┬──────────────────┘
                   │ referenciado por
                   ▼
┌─────────────────────────────────────┐
│            COLECÇÃO: vendas          │
├─────────────────────────────────────┤
│ _id           : ObjectId (PK)       │
│ produto       : ObjectId (FK→prod.) │
│ quantidade    : Integer             │
│ preco_unitario: Float               │
│ total         : Float               │
│ observacoes   : String              │
│ vendido_por   : String              │
│ data_venda    : DateTime            │
└─────────────────────────────────────┘

Índices criados automaticamente:
  usuarios → username
  produtos → nome, categoria, stock
  vendas   → produto, data_venda, vendido_por
```

---

## 16. Conceitos de POO Aplicados

### 16.1 Herança
```python
# interfaces/repository_interface.py
class IRepository(ABC): ...          # Classe base abstracta
class IProdutoRepository(IRepository): ...  # Herda e especializa

# services/produto_service.py
class ProdutoService(IProdutoRepository): ...  # Implementa a interface

# exceptions/
class AuthException(Exception): ...              # Base
class InvalidCredentialsException(AuthException): ...  # Especialização
```

### 16.2 Polimorfismo
```python
# Todos os serviços implementam o mesmo contrato IRepository
# O código cliente pode chamar service.criar() em qualquer serviço
auth_svc.verificar_credenciais(u, p)   # AuthService
produto_svc.criar(dados)               # ProdutoService
venda_svc.registrar_venda(id, qtd)     # VendaService
```

### 16.3 Encapsulamento
```python
# models/usuario.py
class Usuario:
    # password_hash e salt são "privados" (nunca expostos directamente)
    password_hash = StringField(...)    # Guardado como hash
    
    def verificar_password(self, password: str) -> bool:
        # Lógica de verificação encapsulada no modelo
        ...
    
    def to_dict(self) -> dict:
        # Serialização SEM password_hash nem salt
        ...
```

### 16.4 Classes Abstractas
```python
# interfaces/repository_interface.py
from abc import ABC, abstractmethod

class IRepository(ABC):
    @abstractmethod
    def criar(self, dados): ...    # OBRIGATÓRIO nas subclasses
    
    @abstractmethod
    def obter_por_id(self, id): ...
    
    def contar(self, filtros=None) -> int:
        # Método concreto com implementação padrão
        return len(self.pesquisar(filtros or {}))
```

### 16.5 Decoradores Personalizados
```python
# utils/decorators.py

@log_execution     # Regista automaticamente entrada/saída
@validate_positive("quantidade")  # Valida parâmetros numéricos
@retry(max_attempts=3)   # Re-tenta em caso de falha
@timer             # Mede tempo de execução
@cache_result(ttl_seconds=30)  # Cache em memória com TTL
@require_auth      # Protege funções que requerem sessão activa
```

### 16.6 Context Managers Personalizados
```python
# utils/context_manager.py

with DatabaseTransaction("Registar venda") as txn:
    produto.decrementar_stock(quantidade)
    venda = Venda.criar_venda(...)
    txn.commit()   # Só confirma se tudo correu bem

with CSVWriter("produtos.csv", cabecalhos) as writer:
    for produto in produtos:
        writer.write_row([produto.nome, produto.stock])
    # Ficheiro fechado automaticamente, mesmo com erros

with measure_time("treino IA") as timing:
    modelo.fit(X, y)
print(f"Treino: {timing['elapsed']:.2f}s")
```

### 16.7 Excepções Customizadas
```python
# Hierarquias completas de excepções semânticas
raise InsufficientStockException(
    product_name="Arroz", requested=50, available=10
)
# → StockException → Exception

raise InvalidCredentialsException()
# → AuthException → Exception
```

---

## 17. Explicação da Inteligência Artificial

### 17.1 Algoritmo: Regressão Linear Simples

A Regressão Linear é um algoritmo supervisionado que encontra a relação linear entre:
- **X** (variável independente): índice temporal (1, 2, 3, ... N)
- **Y** (variável dependente): quantidade vendida nesse período

A equação é: `Y = β₀ + β₁ × X`

Onde:
- `β₀` = intercepto (valor inicial estimado)
- `β₁` = coeficiente angular (variação por período)

### 17.2 Processo Completo

```
DADOS DE ENTRADA (histórico):
  Jan(1): 12 | Fev(2): 15 | Mar(3): 18 | Abr(4): 20

TREINO (sklearn LinearRegression):
  X = [[1], [2], [3], [4]]
  y = [12, 15, 18, 20]
  modelo.fit(X, y)
  → coef_ ≈ 2.8   (cresce ~2.8 un/mês)
  → intercept_ ≈ 9.5

PREVISÃO:
  X_futuro = [[5], [6], [7]]
  previsoes = modelo.predict(X_futuro)
  → Maio(5) ≈ 23 | Jun(6) ≈ 26 | Jul(7) ≈ 29

MÉTRICAS:
  R² = 0.99   → excelente ajuste linear
  MAE = 0.6   → erro médio de 0.6 unidades
  RMSE = 0.7  → raiz do erro quadrático médio
```

### 17.3 Interpretação do R²

| R² | Qualidade | Acção |
|----|-----------|-------|
| ≥ 0.90 | Excelente | Alta confiança nas previsões |
| 0.70–0.89 | Bom | Previsões confiáveis |
| 0.50–0.69 | Moderado | Use com precaução |
| < 0.50 | Fraco | Adicione mais dados históricos |

### 17.4 Persistência do Modelo

O modelo treinado é guardado em `reports/modelo_ia.pkl` (pickle). Na próxima execução, é carregado automaticamente sem necessidade de re-treino.

---

## 18. Explicação do MongoEngine

O **MongoEngine** é um ODM (Object-Document Mapper) que permite trabalhar com o MongoDB usando classes Python, de forma semelhante ao SQLAlchemy com bases de dados SQL.

### 18.1 Definição de um Modelo

```python
from mongoengine import Document, StringField, IntField

class Produto(Document):
    nome     = StringField(required=True, unique=True)
    stock    = IntField(min_value=0, default=0)
    
    meta = {"collection": "produtos"}  # Nome da colecção MongoDB
```

### 18.2 Operações CRUD com MongoEngine

```python
# Criar
produto = Produto(nome="Arroz", stock=100)
produto.save()

# Ler
produto = Produto.objects(nome="Arroz").first()

# Actualizar
produto.stock = 80
produto.save()
# Ou: Produto.objects(id=id).update(set__stock=80)

# Eliminar
produto.delete()

# Pesquisar com filtros
baratos = Produto.objects(preco__lte=1000, ativo=True).order_by("nome")
```

### 18.3 ReferenceField (Relação entre documentos)

```python
class Venda(Document):
    produto = ReferenceField("Produto", reverse_delete_rule=CASCADE)
    # MongoDB armazena o ObjectId do produto
    # MongoEngine resolve automaticamente para o objecto Produto
    
# Acesso:
venda = Venda.objects.first()
print(venda.produto.nome)  # Resolve automaticamente a referência
```

---

## 19. Screenshots Esperados

```
┌──────────────────────────────────────────┐
│           ECRÃ DE LOGIN                  │
│  📦                                      │
│  InventárioIA                            │
│  Sistema Inteligente de Gestão...        │
│                                          │
│  Nome de Utilizador                      │
│  [________________]                      │
│                                          │
│  Palavra-passe                           │
│  [••••••••••••••] [👁]                   │
│                                          │
│  [   Entrar no Sistema   ]              │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│  DASHBOARD                                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────┐  ┌───────┐  │
│  │ 📦 12 prod  │  │ ⚠️ 3 baixos │  │ 💰 45k   │  │🤖 ~23 │  │
│  └─────────────┘  └─────────────┘  └──────────┘  └───────┘  │
│  ┌──────────────────────────────┐  ┌─────────────────────┐   │
│  │ 📈 Receita Mensal            │  │ ⚠️ Stock Baixo      │   │
│  │  [gráfico de barras]         │  │  Produto A — 2 un.  │   │
│  │                              │  │  Produto B — 5 un.  │   │
│  └──────────────────────────────┘  └─────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

---

## 20. Testes Unitários

```bash
# Executar todos os testes:
cd inventarioIA
python -m pytest tests/ -v

# Ou com unittest directamente:
python -m unittest tests.test_produto_service -v

# Com relatório de cobertura (requer: pip install coverage):
coverage run -m pytest tests/
coverage report -m
coverage html  # Gera relatório HTML em htmlcov/
```

Testes implementados:
- `TestProdutoServiceUnitario`: criação, duplicados, eliminação, pesquisa
- `TestProdutoModelo`: stock baixo, valor total, estados
- `TestExcecoes`: hierarquias, mensagens, herança
- `TestIAService`: treino, previsão, métricas, R², tendência
- `TestDecorators`: validate_positive, log_execution, cache_result, timer
- `TestContextManagers`: DatabaseTransaction, CSVWriter, measure_time, suppress_and_log

---

## 21. Padrões de Projecto Utilizados

| Padrão | Onde | Descrição |
|--------|------|-----------|
| **Singleton** | `DatabaseConnection` | Uma única instância de ligação ao MongoDB |
| **Repository** | `IProdutoRepository`, `IVendaRepository` | Abstracção do acesso a dados |
| **Service Layer** | `ProdutoService`, `VendaService` | Centraliza lógica de negócio |
| **Dependency Injection** | `main.py`, `VendaService` | Serviços injectados em vez de instanciados internamente |
| **Factory Method** | `Usuario.criar_utilizador()`, `Venda.criar_venda()` | Criação controlada de objectos |
| **Observer** (simplif.) | Callbacks da GUI | `on_login_success` na janela de login |
| **Decorator** | `utils/decorators.py` | Enriquecimento de funções sem modificação |
| **Context Manager** | `utils/context_manager.py` | Gestão de recursos (transacções, ficheiros) |

---

## 22. Melhorias Futuras

- [ ] Autenticação com JWT e refresh tokens
- [ ] Múltiplos utilizadores simultâneos (multi-thread)
- [ ] Notificações automáticas de stock baixo (email/SMS)
- [ ] Modelos IA mais avançados: Random Forest, ARIMA, Prophet
- [ ] Dashboard com dados em tempo real (WebSocket)
- [ ] Importação de produtos via Excel/CSV
- [ ] Versão Web (Flask/FastAPI + React)
- [ ] Relatórios PDF com ReportLab
- [ ] Integração com sistemas de pagamento
- [ ] Backup automático da base de dados
- [ ] API REST para integração com outros sistemas
- [ ] Temas claros/escuros dinâmicos

---

## 23. Solução de Erros Comuns

### ❌ Erro: "Não foi possível conectar ao MongoDB"

```
Causa: O servidor MongoDB não está em execução.
Solução:
  # Windows:
  net start MongoDB
  # ou abrir "Serviços" e iniciar "MongoDB"

  # Linux:
  sudo systemctl start mongod

  # Manual:
  mkdir -p ~/data/db && mongod --dbpath ~/data/db
```

### ❌ Erro: "ModuleNotFoundError: No module named 'customtkinter'"

```
Causa: Dependências não instaladas.
Solução:
  pip install -r requirements.txt
```

### ❌ Erro: "NotUniqueError: Tried to save duplicate unique keys"

```
Causa: Produto ou utilizador com nome já existente.
Solução: A aplicação trata este erro com DuplicateProductException.
         Escolha um nome diferente para o produto/utilizador.
```

### ❌ Erro: "Modelo não treinado" na IA

```
Causa: O produto seleccionado não tem histórico de vendas suficiente.
Solução: Registe pelo menos 2 meses de vendas para esse produto
         antes de tentar treinar o modelo de IA.
```

### ❌ Gráficos não aparecem no Dashboard

```
Causa: Backend Matplotlib incompatível.
Solução:
  pip install --upgrade matplotlib pillow
  # Verificar:
  python -c "import matplotlib; print(matplotlib.get_backend())"
  # Deve mostrar: TkAgg
```

### ❌ Erro no Python 3.11 ou inferior

```
Causa: Projecto requer Python 3.12+.
Solução:
  python --version   # Verificar versão
  # Instalar Python 3.12 em: https://www.python.org/downloads/
```

---

## 24. Dependências Detalhadas

| Pacote | Versão | Propósito |
|--------|--------|-----------|
| `customtkinter` | 5.2.2 | Framework GUI moderna baseada em Tkinter |
| `mongoengine` | 0.27.0 | ODM para MongoDB (mapeamento classes↔documentos) |
| `pymongo` | 4.6.3 | Driver nativo Python para MongoDB |
| `scikit-learn` | 1.4.2 | Regressão Linear e métricas de ML |
| `numpy` | 1.26.4 | Vectores e operações matemáticas |
| `matplotlib` | 3.8.4 | Gráficos 2D integrados na GUI |
| `joblib` | 1.3.2 | Serialização eficiente (usado pelo sklearn) |
| `pillow` | 10.3.0 | Processamento de imagens para CustomTkinter |

---

## 25. Referências Bibliográficas

1. **Python Software Foundation**. *Python 3.12 Documentation*. https://docs.python.org/3/
2. **MongoDB Inc.** *MongoDB Manual*. https://www.mongodb.com/docs/manual/
3. **MongoEngine**. *MongoEngine User Documentation*. https://mongoengine.org/
4. **Géron, A.** (2022). *Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow* (3rd ed.). O'Reilly Media.
5. **scikit-learn Developers**. *scikit-learn: Machine Learning in Python*. https://scikit-learn.org/
6. **CustomTkinter**. *Modern GUI Framework Documentation*. https://customtkinter.tomschimansky.com/
7. **Matplotlib**. *Matplotlib: Visualization with Python*. https://matplotlib.org/
8. **Gamma, E., Helm, R., Johnson, R., & Vlissides, J.** (1994). *Design Patterns: Elements of Reusable Object-Oriented Software*. Addison-Wesley.
9. **Martin, R. C.** (2008). *Clean Code: A Handbook of Agile Software Craftsmanship*. Prentice Hall.
10. **Lutz, M.** (2013). *Learning Python* (5th ed.). O'Reilly Media.

---

> **Autor**: Estudante — Instituto Politécnico - UNIKIVI  
> **Docente**: Moyo Kanivengidio  
> **Disciplina**: Linguagem de Programação VI (Python)  
> **Data**: Maio 2026
