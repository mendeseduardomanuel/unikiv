# Criar uma lista de quadrados dos números de 0 a 9
quadrados = [x**2 for x in range(10)]
print(f"Quadrados: {quadrados}")  # Saída: [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

# Filtrar números pares
pares = [x for x in range(20) if x % 2 == 0]
print(f"Pares: {pares}")  # Saída: [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]

# Compreensão de lista aninhada
matriz = [[j for j in range(3)] for i in range(3)]
print(f"Matriz: {matriz}")  # Saída: [[0, 1, 2], [0, 1, 2], [0, 1, 2]]