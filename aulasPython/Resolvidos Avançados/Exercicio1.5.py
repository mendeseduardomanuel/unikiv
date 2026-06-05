"""Problema: Crie um decorador que valide se os argumentos de uma função são do tipo 
esperado. Se os tipos não corresponderem, deve lançar um TypeError."""


def validar_tipos(*expected_types):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if len(args) != len(expected_types):
                raise TypeError(
                    f"Esperava {len(expected_types)} argumentos posicionais, mas recebeu {len(args)}."
                )
            for arg, expected_type in zip(args, expected_types):
                if not isinstance(arg, expected_type):
                    raise TypeError(
                        f"Argumento '{arg}' deve ser do tipo {expected_type.__name__}, mas é {type(arg).__name__}."
                    )
            return func(*args, **kwargs)

        return wrapper

    return decorator


@validar_tipos(int, int)
def somar(a, b):
    return a + b


@validar_tipos(str, list)
def adicionar_item(lista_str, item):
    lista_str.append(item)
    return lista_str


print("\n--- Teste Somar ---")
print(f"Soma (2, 3): {somar(2, 3)}")
try:
    somar(2, "3")
except TypeError as e:
    print(f"Erro ao somar: {e}")

print("\n--- Teste Adicionar Item ---")
minha_lista = ["a", "b"]
print(f"Lista após adicionar 'c': {adicionar_item(minha_lista, 'c')}")
try:
    adicionar_item("string", "d")
except TypeError as e:
    print(f"Erro ao adicionar item: {e}")