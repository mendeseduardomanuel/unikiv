ponto = (100, 20) # Tupla de dois elementos 
coordenadas = ('latitude', 34.0522, 'longitude', -118.2437) 
print(ponto[0]) # Acesso por índice: 10 
# ponto[0] = 15 # Erro: Tuplas são imutáveis 
# Desempacotamento de tuplas 
x, y = ponto 
print(f"X: {x}, Y: {y}")
print(ponto) # Imprime a tupla completa