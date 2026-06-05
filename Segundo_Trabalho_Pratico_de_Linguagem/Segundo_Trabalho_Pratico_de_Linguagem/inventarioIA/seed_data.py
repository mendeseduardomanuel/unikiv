"""
=============================================================================
Ficheiro: seed_data.py
Descrição: Script para popular a base de dados com dados de exemplo.
           Execute uma vez após a primeira instalação para ter dados
           de demonstração prontos a usar.

Uso:
    python seed_data.py

O script cria:
  - 1 administrador + 1 operador
  - 15 produtos em 6 categorias
  - 90 dias de histórico de vendas simulado (ideal para treinar a IA)
=============================================================================
"""

import sys
import os
import random
import logging
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))

# Configura logging mínimo
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("seed")


def main() -> None:
    """Executa o seed de dados de demonstração."""

    # -------------------------------------------------------------------
    # 1. Conecta ao MongoDB
    # -------------------------------------------------------------------
    logger.info("A conectar ao MongoDB...")
    from database.connection import DatabaseConnection

    db = DatabaseConnection.get_instance()
    try:
        db.connect()
        logger.info("Ligação ao MongoDB estabelecida.")
    except ConnectionError as e:
        logger.error(f"Falha na ligação: {e}")
        logger.error("Certifique-se de que o MongoDB está em execução.")
        sys.exit(1)

    # -------------------------------------------------------------------
    # 2. Utilizadores
    # -------------------------------------------------------------------
    logger.info("A criar utilizadores...")
    from models.usuario import Usuario
    from mongoengine.errors import NotUniqueError

    utilizadores = [
        {
            "username": "admin",
            "password": "admin123",
            "nome_completo": "Administrador do Sistema",
            "role": "admin",
        },
        {
            "username": "joao.silva",
            "password": "joao2026",
            "nome_completo": "João Silva",
            "role": "operador",
        },
        {
            "username": "maria.santos",
            "password": "maria2026",
            "nome_completo": "Maria Santos",
            "role": "operador",
        },
    ]

    utilizadores_criados = 0
    for u in utilizadores:
        existente = Usuario.objects(username=u["username"]).first()
        if not existente:
            Usuario.criar_utilizador(
                username=u["username"],
                password=u["password"],
                nome_completo=u["nome_completo"],
                role=u["role"],
            )
            utilizadores_criados += 1
            logger.info(f"  ✓ Utilizador criado: {u['username']} ({u['role']})")
        else:
            logger.info(f"  → Utilizador já existe: {u['username']}")

    # -------------------------------------------------------------------
    # 3. Produtos
    # -------------------------------------------------------------------
    logger.info("A criar produtos...")
    from models.produto import Produto

    produtos_dados = [
        # Alimentação
        {"nome": "Arroz Agulha 5kg",        "categoria": "Alimentação",  "preco": 2500.0,  "stock": 120, "stock_minimo": 20},
        {"nome": "Feijão Preto 1kg",         "categoria": "Alimentação",  "preco": 850.0,   "stock": 80,  "stock_minimo": 15},
        {"nome": "Óleo de Girassol 1L",      "categoria": "Alimentação",  "preco": 1200.0,  "stock": 65,  "stock_minimo": 20},
        {"nome": "Açúcar Refinado 2kg",      "categoria": "Alimentação",  "preco": 950.0,   "stock": 8,   "stock_minimo": 10},  # stock baixo!
        {"nome": "Farinha de Trigo 1kg",     "categoria": "Alimentação",  "preco": 680.0,   "stock": 90,  "stock_minimo": 15},
        # Bebidas
        {"nome": "Água Mineral 1.5L",        "categoria": "Bebidas",      "preco": 350.0,   "stock": 200, "stock_minimo": 30},
        {"nome": "Sumo de Laranja 1L",       "categoria": "Bebidas",      "preco": 750.0,   "stock": 45,  "stock_minimo": 10},
        {"nome": "Refrigerante Cola 2L",     "categoria": "Bebidas",      "preco": 900.0,   "stock": 0,   "stock_minimo": 10},  # sem stock!
        # Higiene
        {"nome": "Sabão em Pó 1kg",          "categoria": "Higiene",      "preco": 1100.0,  "stock": 55,  "stock_minimo": 10},
        {"nome": "Champô Anticaspa 400ml",   "categoria": "Higiene",      "preco": 2200.0,  "stock": 30,  "stock_minimo": 8},
        {"nome": "Pasta de Dentes 90g",      "categoria": "Higiene",      "preco": 680.0,   "stock": 5,   "stock_minimo": 10},  # stock crítico!
        # Electrónica
        {"nome": "Pilhas AA (pack 4)",       "categoria": "Electrónica",  "preco": 850.0,   "stock": 100, "stock_minimo": 20},
        {"nome": "Carregador USB-C 65W",     "categoria": "Electrónica",  "preco": 8500.0,  "stock": 15,  "stock_minimo": 5},
        # Limpeza
        {"nome": "Detergente Loiça 500ml",   "categoria": "Limpeza",      "preco": 750.0,   "stock": 70,  "stock_minimo": 15},
        # Material Escolar
        {"nome": "Caderno Pautado A4",       "categoria": "Material Escolar", "preco": 450.0, "stock": 150, "stock_minimo": 20},
    ]

    produtos_criados = 0
    produtos_obj = {}

    for dados in produtos_dados:
        existente = Produto.objects(nome=dados["nome"]).first()
        if not existente:
            p = Produto(
                nome=dados["nome"],
                categoria=dados["categoria"],
                preco=dados["preco"],
                stock=dados["stock"],
                stock_minimo=dados["stock_minimo"],
                descricao=f"Produto de {dados['categoria']} — qualidade garantida.",
            )
            p.save()
            produtos_obj[dados["nome"]] = p
            produtos_criados += 1
            logger.info(
                f"  ✓ Produto criado: {dados['nome']} "
                f"(stock={dados['stock']}, preço={dados['preco']:.2f})"
            )
        else:
            produtos_obj[dados["nome"]] = existente
            logger.info(f"  → Produto já existe: {dados['nome']}")

    # -------------------------------------------------------------------
    # 4. Histórico de Vendas (últimos 90 dias)
    #    Gera padrão de vendas realista com tendência crescente
    #    para que a IA tenha dados suficientes para treinar.
    # -------------------------------------------------------------------
    logger.info("A gerar histórico de vendas (90 dias)...")
    from models.venda import Venda

    total_vendas_existentes = Venda.objects().count()
    if total_vendas_existentes > 0:
        logger.info(
            f"  → Já existem {total_vendas_existentes} vendas. "
            "A ignorar geração de histórico."
        )
    else:
        # Produtos com histórico de vendas (para treinar a IA)
        produtos_vender = {
            "Arroz Agulha 5kg":      {"base": 12, "tendencia": 2.0, "variancia": 3},
            "Feijão Preto 1kg":      {"base": 8,  "tendencia": 1.5, "variancia": 2},
            "Água Mineral 1.5L":     {"base": 25, "tendencia": 3.0, "variancia": 5},
            "Sumo de Laranja 1L":    {"base": 10, "tendencia": 1.0, "variancia": 2},
            "Sabão em Pó 1kg":       {"base": 7,  "tendencia": 0.8, "variancia": 2},
            "Caderno Pautado A4":    {"base": 15, "tendencia": 2.5, "variancia": 4},
            "Óleo de Girassol 1L":   {"base": 9,  "tendencia": 1.2, "variancia": 2},
            "Pilhas AA (pack 4)":    {"base": 6,  "tendencia": 0.5, "variancia": 1},
            "Detergente Loiça 500ml":{"base": 8,  "tendencia": 1.0, "variancia": 2},
        }

        operadores = ["admin", "joao.silva", "maria.santos"]
        vendas_criadas = 0

        for nome_produto, config in produtos_vender.items():
            produto_obj = produtos_obj.get(nome_produto)
            if not produto_obj:
                continue

            # Gera vendas para os últimos 90 dias
            for dia_atras in range(90, 0, -1):
                data_venda = datetime.utcnow() - timedelta(days=dia_atras)

                # Probabilidade de venda neste dia (60%)
                if random.random() < 0.60:
                    # Quantidade com tendência crescente ao longo do tempo
                    mes = (90 - dia_atras) / 30  # 0 a 3 meses
                    base_com_tendencia = (
                        config["base"] + config["tendencia"] * mes
                    )
                    quantidade = max(
                        1,
                        int(
                            base_com_tendencia
                            + random.uniform(
                                -config["variancia"], config["variancia"]
                            )
                        ),
                    )

                    # Não vende mais do que o stock restante
                    produto_actual = Produto.objects(id=produto_obj.id).first()
                    if produto_actual and produto_actual.stock >= quantidade:
                        venda = Venda(
                            produto=produto_obj,
                            quantidade=quantidade,
                            preco_unitario=produto_obj.preco,
                            total=round(produto_obj.preco * quantidade, 2),
                            vendido_por=random.choice(operadores),
                            observacoes="",
                            data_venda=data_venda,
                        )
                        venda.save()

                        # Actualiza stock
                        produto_actual.stock = max(0, produto_actual.stock - quantidade)
                        produto_actual.save()

                        vendas_criadas += 1

        logger.info(f"  ✓ {vendas_criadas} registos de vendas criados.")

    # -------------------------------------------------------------------
    # 5. Resumo
    # -------------------------------------------------------------------
    logger.info("=" * 55)
    logger.info("  SEED CONCLUÍDO COM SUCESSO")
    logger.info("=" * 55)
    logger.info(f"  Utilizadores : {Usuario.objects().count()}")
    logger.info(f"  Produtos     : {Produto.objects().count()}")
    logger.info(f"  Vendas       : {Venda.objects().count()}")
    logger.info("=" * 55)
    logger.info("  Credenciais de acesso:")
    logger.info("    Admin   → username: admin    | password: admin123")
    logger.info("    Operador→ username: joao.silva| password: joao2026")
    logger.info("=" * 55)
    logger.info("  Execute agora: python main.py")


if __name__ == "__main__":
    main()
