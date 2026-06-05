"""Problema: Crie uma função geradora que produza números primos até um limite especificado."""
def gerar_primos(limite):
    def eh_primo(n):
        if n < 2:
            return False
        for i in range(2, int(n ** 0.5) + 1):
            if n % i == 0:
                return False
        return True

    for num in range(2, limite + 1):
        if eh_primo(num):
            yield num

# Exemplo de uso
primos_ate_20 = list(gerar_primos(20))
print(f"Números primos até 20: {primos_ate_20}")