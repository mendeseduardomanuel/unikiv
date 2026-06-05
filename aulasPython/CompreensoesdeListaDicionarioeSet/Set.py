# Criar um set de caracteres únicos de uma string 
letras_unicas = {char for char in "abracadabra" if char != 'a'} 
print(f"Letras únicas (sem 'a'): {letras_unicas}") # Saída: {'r', 'b', 'c', 'd'} python -m pip install -r requirements.txt