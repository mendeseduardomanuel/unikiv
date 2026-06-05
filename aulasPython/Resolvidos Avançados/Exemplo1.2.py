"""Problema: Otimizar uma função que realiza cálculos custosos, armazenando em cache os 
resultados de chamadas anteriores com os mesmos argumentos."""

import time

def cache(func):
    cache_data = {}

    def wrapper(*args, **kwargs):
        # Gerar uma chave única para o cache com base nos argumentos
        # Tuplas são imutáveis e podem ser usadas como chaves de dicionário
        key = (args, tuple(sorted(kwargs.items())))
        if key in cache_data:
            print(f"Cache hit para {func.__name__} com {args}, {kwargs}")
            return cache_data[key]
        else:
            print(f"Cache miss para {func.__name__} com {args}, {kwargs}. Calculando...")
            result = func(*args, **kwargs)
            cache_data[key] = result
            return result

    return wrapper


@cache
def calcular_fibonacci(n):
    if n <= 1:
        return n
    return calcular_fibonacci(n-1) + calcular_fibonacci(n-2)


@cache
def potencia(base, expoente):
    time.sleep(0.1)  # Simula um cálculo demorado
    return base ** expoente

print("--- Teste Fibonacci ---")
print(f"Fibonacci(5): {calcular_fibonacci(5)}")  # Calcula
print(f"Fibonacci(5): {calcular_fibonacci(5)}")  # Cache hit
print(f"Fibonacci(7): {calcular_fibonacci(7)}")  # Calcula
print(f"Fibonacci(5): {calcular_fibonacci(5)}")  # Cache hit
print("--- Teste Potência ---")
print(f"Potência(2, 10): {potencia(2, 10)}")  # Calcula
print(f"Potência(2, 10): {potencia(2, 10)}")  # Cache hit
print(f"Potência(3, 5): {potencia(3, 5)}")  # Calcula
