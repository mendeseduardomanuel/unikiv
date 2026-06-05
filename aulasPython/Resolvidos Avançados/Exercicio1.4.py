"""Problema: Dada uma lista de dicionários representando estudantes, filtre apenas os estudantes 
com idade superior a 20 anos e crie uma nova lista contendo apenas os seus nomes em 
maiúsculas."""
estudantes = [ 
{"nome": "Ana", "idade": 21, "curso": "Eng. Informática"}, 
{"nome": "Bruno", "idade": 19, "curso": "Gestão"}, 
{"nome": "Carla", "idade": 22, "curso": "Eng. Civil"}, 
{"nome": "Daniel", "idade": 20, "curso": "Eng. Informática"} 
] 
# Usando compreensão de lista para filtrar e transformar 
nomes_estudantes_maiores_20 = [estudante["nome"].upper()  
for estudante in estudantes  
if estudante["idade"] > 20] 
print(f"Nomes dos estudantes com mais de 20 anos: {nomes_estudantes_maiores_20}") 
# Saída esperada: ['ANA', 'CARLA'] 