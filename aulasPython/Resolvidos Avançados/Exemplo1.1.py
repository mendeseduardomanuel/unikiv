import re
from collections import Counter

def analisar_frequencia_palavras(texto, num_palavras=5):
    # 1. Converter para minúsculas e remover pontuação
    texto_limpo = re.sub(r"[^\w\s]", "", texto).lower()
    # 2. Dividir o texto em palavras
    palavras = texto_limpo.split()
    # 3. Contar a frequência das palavras usando Counter
    # frequencia = {palavra: palavras.count(palavra) for palavra in set(palavras)}
    frequencia = Counter(palavras)
    # 4. Obter as palavras mais comuns
    palavras_mais_comuns = frequencia.most_common(num_palavras)
    return palavras_mais_comuns


# Exemplo de uso
texto_exemplo = (
    "Python é uma linguagem de programação poderosa. "
    "Python é fácil de aprender e usar. Programação com Python é "
    "divertida!"
)
resultado = analisar_frequencia_palavras(texto_exemplo, 3)
print("Palavras mais frequentes:")
for palavra, contagem in resultado:
    print(f"- {palavra}: {contagem}")

# Saída esperada:
# Palavras mais frequentes:
# - python: 3
# - é: 3
# - de: 2
