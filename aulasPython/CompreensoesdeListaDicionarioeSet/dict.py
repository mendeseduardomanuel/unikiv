quadrados_dict = {x: x**2 for x in range(5)}
print(f"Dicionário de quadrados: {quadrados_dict}")  # Saída: {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

# Inverter chaves e valores de um dicionário
original = {"a": 1, "b": 2, "c": 3}
invertido = {valor: chave for chave, valor in original.items()}
print(f"Dicionário invertido: {invertido}")  # Saída: {1: 'a', 2: 'b', 3: 'c'}