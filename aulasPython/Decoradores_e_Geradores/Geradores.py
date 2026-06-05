def gerador_pares(limite): 
    n = 0 
    while n < limite: 
        yield n # Pausa a execução e retorna n. Retoma daqui na próxima chamada. 
        n += 2
# Usando o gerador 
for numero in gerador_pares(10): 
    print(numero)

def ler_grandes_dados(caminho_arquivo): 
    with open(caminho_arquivo, 'r') as f: 
        for linha in f: 
            yield linha.strip().split(',') # Processa linha por linha 
# Supondo um arquivo 'dados.csv' com milhões de linhas 
# for registro in ler_grandes_dados('dados.csv'): 
#     processar_registro(registro)