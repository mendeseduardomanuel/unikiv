"""Problema: Processar um ficheiro CSV muito grande (milhões de linhas) sem carregar todo o 
seu conteúdo na memória, calculando a média de uma coluna numérica."""

import csv
import os

def ler_dados_csv_gerador(caminho_arquivo, coluna_numerica_idx):
    """Um gerador para ler um ficheiro CSV linha por linha e extrair um valor numérico."""
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Pular o cabeçalho
        for linha in reader:
            try:
                yield float(linha[coluna_numerica_idx])
            except (ValueError, IndexError):
                # Ignorar linhas com dados inválidos ou colunas ausentes
                continue


def calcular_media_gerador(caminho_arquivo, coluna_idx):
    total = 0
    contagem = 0
    for valor in ler_dados_csv_gerador(caminho_arquivo, coluna_idx):
        total += valor
        contagem += 1
    return total / contagem if contagem > 0 else 0


# Criar um ficheiro CSV de exemplo grande (simulado)
caminho_csv = 'dados_grandes.csv'
with open(caminho_csv, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['ID', 'Valor', 'Descrição'])
    for i in range(100000):
        writer.writerow([i, i * 1.5 + 0.5, f'Item {i}'])

# Exemplo de uso
caminho_do_arquivo = caminho_csv
coluna_para_media = 1  # Coluna 'Valor'
print(f"Calculando média da coluna {coluna_para_media}...")
media = calcular_media_gerador(caminho_do_arquivo, coluna_para_media)
print(f"Média calculada: {media:.2f}")

# Limpar o ficheiro de exemplo
os.remove(caminho_csv)
