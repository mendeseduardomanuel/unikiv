aluno = { 
    "nome": "Ana Silva", 
    "idade": 20, 
    "curso": "Engenharia Informática", 
    "notas": [18, 15, 19] 
} 
print(f"Nome do aluno: {aluno['nome']}") 
aluno["idade"] = 21 # Modificar valor 
aluno["universidade"] = "Kimpa Vita" # Adicionar novo par chave

print(f"Chaves: {aluno.keys()}") 
print(f"Valores: {aluno.values()}") 
print(f"Itens: {aluno.items()}") 
# Iterar sobre um dicionário 
for chave, valor in aluno.items(): 
    print(f"{chave}: {valor}") 