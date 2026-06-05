import time


def medir_tempo(func):
	def wrapper(*args, **kwargs):
		inicio = time.time()
		resultado = func(*args, **kwargs)
		fim = time.time()
		print(f"A função {func.__name__} levou {fim - inicio:.4f} segundos para executar.")
		return resultado

	return wrapper


@medir_tempo
def somar_numeros(n):
	total = 0
	for i in range(n):
		total += i
	return total


@medir_tempo
def multiplicar_numeros(n):
	total = 1
	for i in range(1, n + 1):
		total *= i
	return total


somar_numeros(1000000)
multiplicar_numeros(10000)