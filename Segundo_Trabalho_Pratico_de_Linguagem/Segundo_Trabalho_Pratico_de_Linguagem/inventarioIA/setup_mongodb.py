"""
=============================================================================
Ficheiro: setup_mongodb.py
Descrição: Script de verificação e configuração do ambiente MongoDB.
           Execute para validar que tudo está pronto antes de lançar
           a aplicação pela primeira vez.

Uso:
    python setup_mongodb.py
=============================================================================
"""

import sys
import os
import subprocess
import platform

sys.path.insert(0, os.path.dirname(__file__))


def separador(titulo: str = "") -> None:
    """Imprime um separador formatado."""
    if titulo:
        print(f"\n{'─' * 55}")
        print(f"  {titulo}")
        print(f"{'─' * 55}")
    else:
        print(f"{'─' * 55}")


def check(mensagem: str, ok: bool = True) -> None:
    """Imprime resultado de uma verificação."""
    simbolo = "✓" if ok else "✗"
    cor = "\033[92m" if ok else "\033[91m"  # Verde / Vermelho
    reset = "\033[0m"
    print(f"  {cor}{simbolo}{reset}  {mensagem}")


def verificar_python() -> bool:
    """Verifica a versão do Python."""
    separador("1. Verificação do Python")
    versao = sys.version_info
    ok = versao >= (3, 12)
    check(
        f"Python {versao.major}.{versao.minor}.{versao.micro} "
        f"(mínimo: 3.12)",
        ok,
    )
    if not ok:
        print("\n  ► Instale Python 3.12+ em: https://www.python.org/downloads/")
    return ok


def verificar_dependencias() -> bool:
    """Verifica se todas as dependências estão instaladas."""
    separador("2. Verificação de Dependências")
    deps = [
        ("customtkinter",  "customtkinter"),
        ("mongoengine",    "mongoengine"),
        ("pymongo",        "pymongo"),
        ("sklearn",        "scikit-learn"),
        ("numpy",          "numpy"),
        ("matplotlib",     "matplotlib"),
        ("PIL",            "pillow"),
    ]
    todas_ok = True
    for modulo, nome_pacote in deps:
        try:
            __import__(modulo)
            check(f"{nome_pacote}")
        except ImportError:
            check(f"{nome_pacote} — NÃO INSTALADO", False)
            todas_ok = False

    if not todas_ok:
        print("\n  ► Execute: pip install -r requirements.txt")
    return todas_ok


def verificar_mongodb() -> bool:
    """Verifica se o MongoDB está acessível."""
    separador("3. Verificação do MongoDB")
    try:
        import pymongo
        from pymongo import MongoClient
        from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

        client = MongoClient(
            "mongodb://localhost:27017/",
            serverSelectionTimeoutMS=3000,
        )
        client.admin.command("ping")
        client.close()
        check("MongoDB está em execução em localhost:27017")
        check(f"PyMongo versão: {pymongo.version}")
        return True
    except Exception as e:
        check(f"MongoDB não acessível: {e}", False)
        sistema = platform.system()
        print("\n  ► Para iniciar o MongoDB:")
        if sistema == "Windows":
            print("    net start MongoDB")
            print("    ou: mongod --dbpath C:\\data\\db")
        elif sistema == "Linux":
            print("    sudo systemctl start mongod")
        elif sistema == "Darwin":
            print("    brew services start mongodb-community@7.0")
        print("    Manual: mkdir -p ~/data/db && mongod --dbpath ~/data/db")
        return False


def verificar_ligacao_mongoengine() -> bool:
    """Verifica a ligação via MongoEngine."""
    separador("4. Verificação da Ligação MongoEngine")
    try:
        from database.connection import DatabaseConnection
        from config.settings import MONGO_DATABASE

        db = DatabaseConnection.get_instance()
        db.connect()
        check(f"Ligação MongoEngine estabelecida")
        check(f"Base de dados: {MONGO_DATABASE}")
        db.disconnect()
        return True
    except Exception as e:
        check(f"Erro MongoEngine: {e}", False)
        return False


def verificar_pastas() -> None:
    """Cria as pastas necessárias."""
    separador("5. Verificação de Pastas")
    pastas = ["logs", "reports", "data"]
    for pasta in pastas:
        caminho = os.path.join(os.path.dirname(__file__), pasta)
        if not os.path.exists(caminho):
            os.makedirs(caminho, exist_ok=True)
            check(f"Pasta '{pasta}' criada")
        else:
            check(f"Pasta '{pasta}' já existe")


def verificar_ia() -> bool:
    """Verifica se a IA funciona correctamente."""
    separador("6. Verificação do Módulo IA")
    try:
        from sklearn.linear_model import LinearRegression
        import numpy as np

        # Teste rápido
        X = np.array([[1], [2], [3], [4], [5], [6]])
        y = np.array([12.0, 15.0, 18.0, 20.0, 23.0, 26.0])
        modelo = LinearRegression()
        modelo.fit(X, y)
        previsao = modelo.predict([[7]])[0]

        check(f"scikit-learn LinearRegression OK")
        check(f"Teste de previsão: período 7 → {previsao:.1f} unidades")
        return True
    except Exception as e:
        check(f"Erro no módulo IA: {e}", False)
        return False


def resumo_final(resultados: dict) -> None:
    """Apresenta o resumo final das verificações."""
    separador("RESUMO FINAL")
    tudo_ok = all(resultados.values())

    for nome, ok in resultados.items():
        check(nome, ok)

    print()
    if tudo_ok:
        print("  \033[92m✓ SISTEMA PRONTO!\033[0m")
        print("  Execute: python main.py")
        print()
        print("  Ou para popular com dados de exemplo:")
        print("  python seed_data.py")
    else:
        print("  \033[91m✗ Corrija os erros acima antes de executar a aplicação.\033[0m")

    separador()


def main() -> None:
    """Executa todas as verificações."""
    print()
    print("  ╔══════════════════════════════════════════════════╗")
    print("  ║   InventárioIA — Verificação de Ambiente         ║")
    print("  ║   Instituto Politécnico - UNIKIVI                ║")
    print("  ╚══════════════════════════════════════════════════╝")

    resultados = {}
    resultados["Python 3.12+"]        = verificar_python()
    resultados["Dependências Python"] = verificar_dependencias()
    resultados["MongoDB activo"]       = verificar_mongodb()

    if resultados["MongoDB activo"]:
        resultados["Ligação MongoEngine"] = verificar_ligacao_mongoengine()
    else:
        resultados["Ligação MongoEngine"] = False

    verificar_pastas()
    resultados["Módulo IA (sklearn)"] = verificar_ia()

    resumo_final(resultados)


if __name__ == "__main__":
    main()
