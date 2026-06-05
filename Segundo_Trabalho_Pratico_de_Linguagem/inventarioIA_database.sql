-- =============================================================================
-- Script de Base de Dados: InventárioIA
-- Descrição: Script SQL equivalente ao modelo MongoDB do projecto InventárioIA.
--            Converte os modelos MongoEngine (Produto, Usuario, Venda) para
--            tabelas SQL relacionais (PostgreSQL / MySQL compatível).
-- Autor: Gerado a partir dos modelos Python (MongoEngine)
-- Data: 2026-06-05
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Criação da base de dados
-- -----------------------------------------------------------------------------
CREATE DATABASE IF NOT EXISTS inventario_ia
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE inventario_ia;

-- =============================================================================
-- TABELA: usuarios
-- Origem: models/usuario.py → class Usuario(Document)
-- =============================================================================
CREATE TABLE IF NOT EXISTS usuarios (
    id              CHAR(24)        NOT NULL,           -- ObjectId do MongoDB (24 hex chars)
    username        VARCHAR(50)     NOT NULL UNIQUE,    -- username único, mín. 3 chars
    password_hash   VARCHAR(64)     NOT NULL,           -- Hash SHA-256 (64 hex chars)
    salt            VARCHAR(64)     NOT NULL,           -- Salt criptográfico (32 bytes hex)
    nome_completo   VARCHAR(100)    NOT NULL DEFAULT '',
    role            ENUM('admin', 'operador') NOT NULL DEFAULT 'operador',
    ativo           BOOLEAN         NOT NULL DEFAULT TRUE,
    tentativas_login INT            NOT NULL DEFAULT 0,
    ultimo_login    DATETIME        NULL,               -- NULL se nunca fez login
    criado_em       DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_usuarios PRIMARY KEY (id),
    CONSTRAINT chk_username_length CHECK (CHAR_LENGTH(username) >= 3)
);

-- Índices da tabela usuarios
CREATE INDEX idx_usuarios_username ON usuarios (username);
CREATE INDEX idx_usuarios_role     ON usuarios (role);
CREATE INDEX idx_usuarios_ativo    ON usuarios (ativo);


-- =============================================================================
-- TABELA: produtos
-- Origem: models/produto.py → class Produto(Document)
-- =============================================================================
CREATE TABLE IF NOT EXISTS produtos (
    id              CHAR(24)        NOT NULL,
    nome            VARCHAR(100)    NOT NULL UNIQUE,    -- Nome único no inventário
    categoria       VARCHAR(50)     NOT NULL DEFAULT 'Geral',
    preco           DECIMAL(12, 2)  NOT NULL,           -- FloatField → DECIMAL para precisão
    stock           INT             NOT NULL DEFAULT 0,
    stock_minimo    INT             NOT NULL DEFAULT 10,
    descricao       VARCHAR(500)    NOT NULL DEFAULT '',
    ativo           BOOLEAN         NOT NULL DEFAULT TRUE,
    criado_em       DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                    ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_produtos       PRIMARY KEY (id),
    CONSTRAINT chk_nome_length   CHECK (CHAR_LENGTH(nome) >= 2),
    CONSTRAINT chk_preco_min     CHECK (preco >= 0.00),
    CONSTRAINT chk_stock_min     CHECK (stock >= 0),
    CONSTRAINT chk_stk_min_min   CHECK (stock_minimo >= 0)
);

-- Índices da tabela produtos
CREATE INDEX idx_produtos_nome      ON produtos (nome);
CREATE INDEX idx_produtos_categoria ON produtos (categoria);
CREATE INDEX idx_produtos_stock     ON produtos (stock);
CREATE INDEX idx_produtos_ativo     ON produtos (ativo);


-- =============================================================================
-- TABELA: vendas
-- Origem: models/venda.py → class Venda(Document)
-- =============================================================================
CREATE TABLE IF NOT EXISTS vendas (
    id              CHAR(24)        NOT NULL,
    produto_id      CHAR(24)        NOT NULL,           -- FK → produtos.id
    quantidade      INT             NOT NULL,
    preco_unitario  DECIMAL(12, 2)  NOT NULL,           -- Preço no momento da venda (histórico)
    total           DECIMAL(14, 2)  NOT NULL,           -- quantidade × preco_unitario
    observacoes     VARCHAR(300)    NOT NULL DEFAULT '',
    vendido_por     VARCHAR(50)     NOT NULL DEFAULT 'sistema', -- username do utilizador
    data_venda      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_vendas            PRIMARY KEY (id),
    CONSTRAINT fk_vendas_produto    FOREIGN KEY (produto_id)
                                    REFERENCES produtos (id)
                                    ON DELETE CASCADE       -- CASCADE: elimina vendas se produto for eliminado
                                    ON UPDATE CASCADE,
    CONSTRAINT chk_quantidade_min   CHECK (quantidade >= 1),
    CONSTRAINT chk_preco_unit_min   CHECK (preco_unitario >= 0.00),
    CONSTRAINT chk_total_min        CHECK (total >= 0.00)
);

-- Índices da tabela vendas
CREATE INDEX idx_vendas_produto_id  ON vendas (produto_id);
CREATE INDEX idx_vendas_data_venda  ON vendas (data_venda);
CREATE INDEX idx_vendas_vendido_por ON vendas (vendido_por);


-- =============================================================================
-- TABELA: logs_sessao  (inferida do sistema de autenticação)
-- Origem: services/auth_service.py (registros de login)
-- =============================================================================
CREATE TABLE IF NOT EXISTS logs_sessao (
    id              BIGINT          NOT NULL AUTO_INCREMENT,
    usuario_id      CHAR(24)        NOT NULL,
    tipo_evento     ENUM('login_sucesso', 'login_falha', 'logout') NOT NULL,
    ip_address      VARCHAR(45)     NULL,               -- IPv4 ou IPv6
    user_agent      VARCHAR(255)    NULL,
    criado_em       DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_logs_sessao        PRIMARY KEY (id),
    CONSTRAINT fk_logs_sessao_usuario FOREIGN KEY (usuario_id)
                                      REFERENCES usuarios (id)
                                      ON DELETE CASCADE
);

CREATE INDEX idx_logs_usuario_id ON logs_sessao (usuario_id);
CREATE INDEX idx_logs_criado_em  ON logs_sessao (criado_em);


-- =============================================================================
-- DADOS INICIAIS (seed) — extraídos de seed_data.py
-- =============================================================================

-- Utilizador administrador padrão
-- NOTA: Em produção, nunca use passwords em texto claro.
--       O hash e salt devem ser gerados pelo sistema (SHA-256 + salt).
INSERT INTO usuarios (id, username, password_hash, salt, nome_completo, role, ativo)
VALUES (
    'aaaaaaaaaaaaaaaaaaaaaaaa',
    'admin',
    'HASH_GERADO_PELO_SISTEMA',   -- substituir pelo hash real
    'SALT_GERADO_PELO_SISTEMA',   -- substituir pelo salt real
    'Administrador do Sistema',
    'admin',
    TRUE
);

-- Categorias de exemplo (produtos)
INSERT INTO produtos (id, nome, categoria, preco, stock, stock_minimo, descricao, ativo)
VALUES
    ('bbbbbbbbbbbbbbbbbbbbbbbb', 'Arroz Branco 5kg',     'Alimentação',  1500.00, 100, 20, 'Arroz branco de primeira qualidade', TRUE),
    ('cccccccccccccccccccccccc', 'Óleo de Soja 1L',      'Alimentação',   800.00,  80, 15, 'Óleo de soja refinado',              TRUE),
    ('dddddddddddddddddddddddd', 'Açúcar Refinado 1kg',  'Alimentação',   600.00,  60, 10, 'Açúcar branco refinado',             TRUE),
    ('eeeeeeeeeeeeeeeeeeeeeeee', 'Leite Condensado',     'Alimentação',   450.00,  50, 10, 'Leite condensado 395g',              TRUE),
    ('ffffffffffffffffffffffff', 'Sabão em Pó 500g',     'Higiene',       350.00,  40, 10, 'Sabão em pó para roupa',             TRUE);


-- =============================================================================
-- VIEWS ÚTEIS
-- =============================================================================

-- Vista: Produtos com stock baixo
CREATE OR REPLACE VIEW vw_produtos_stock_baixo AS
    SELECT
        id,
        nome,
        categoria,
        stock,
        stock_minimo,
        preco,
        CASE
            WHEN stock = 0              THEN 'Sem Stock'
            WHEN stock <= stock_minimo / 2 THEN 'Crítico'
            WHEN stock <= stock_minimo  THEN 'Baixo'
            WHEN stock <= stock_minimo * 3 THEN 'Normal'
            ELSE 'Elevado'
        END AS estado_stock
    FROM produtos
    WHERE ativo = TRUE
      AND stock <= stock_minimo
    ORDER BY stock ASC;


-- Vista: Resumo de vendas por produto
CREATE OR REPLACE VIEW vw_vendas_por_produto AS
    SELECT
        p.id            AS produto_id,
        p.nome          AS produto_nome,
        p.categoria,
        COUNT(v.id)     AS total_vendas,
        SUM(v.quantidade) AS unidades_vendidas,
        SUM(v.total)    AS receita_total,
        MAX(v.data_venda) AS ultima_venda
    FROM produtos p
    LEFT JOIN vendas v ON v.produto_id = p.id
    GROUP BY p.id, p.nome, p.categoria
    ORDER BY receita_total DESC;


-- Vista: Histórico de vendas detalhado
CREATE OR REPLACE VIEW vw_historico_vendas AS
    SELECT
        v.id,
        v.data_venda,
        p.nome          AS produto,
        p.categoria,
        v.quantidade,
        v.preco_unitario,
        v.total,
        v.vendido_por,
        v.observacoes
    FROM vendas v
    INNER JOIN produtos p ON p.id = v.produto_id
    ORDER BY v.data_venda DESC;


-- =============================================================================
-- FIM DO SCRIPT
-- =============================================================================
