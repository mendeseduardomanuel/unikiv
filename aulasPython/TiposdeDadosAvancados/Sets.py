frutas = {"maçã", "banana", "laranja", "maçã"} 
print(frutas) # Saída: {"banana", "laranja", "maçã"} (ordem pode variar) 
numeros_primos = {2, 3, 5, 7, 11} 
numeros_pares = {2, 4, 6, 8, 10} 
print(f"União: {numeros_primos.union(numeros_pares)}") 
print(f"Interseção: {numeros_primos.intersection(numeros_pares)}") 
print(f"Diferença: {numeros_primos.difference(numeros_pares)}") 
print(f"5 está nos primos? {5 in numeros_primos}")