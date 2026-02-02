import random

def sortear_atividades(nomes, atividades):
  """
  Sorteia uma atividade para cada nome e retorna os pares.
  
  :param nomes: Uma lista de strings (os participantes).
  :param atividades: Uma lista de strings (as tarefas).
  :return: Um dicionário onde a chave é o nome e o valor é a atividade sorteada.
  """
  
  # 1. Verificar o tamanho das listas
  
  # Se houver mais atividades do que nomes, as atividades excedentes não serão usadas.
  # Se houver mais nomes do que atividades, a lista de atividades precisa ser repetida (se for esse o objetivo).
  
  if len(nomes) > len(atividades):
    print("Aviso: Há mais nomes do que atividades disponíveis.")
    print("Para garantir que todos tenham uma atividade, as atividades serão repetidas aleatoriamente.")
    
    # Criamos uma nova lista de atividades repetindo e embaralhando a lista original
    # até que seja pelo menos tão grande quanto a lista de nomes.
    
    atividades_estendidas = atividades * ((len(nomes) // len(atividades)) + 1)
    
    # Usamos apenas o número exato de atividades necessárias (igual ao número de nomes)
    atividades_para_sorteio = atividades_estendidas[:len(nomes)]
    
  elif len(atividades) > len(nomes):
    print("Aviso: Há mais atividades do que nomes. As atividades excedentes serão ignoradas no sorteio.")
    atividades_para_sorteio = atividades
    
  else:
    # O número de nomes e atividades é o mesmo
    atividades_para_sorteio = atividades
    
  
  # 2. Embaralhar a lista de atividades (a chave do sorteio)
  
  # O shuffle() mistura a lista in-place (no local)
  random.shuffle(atividades_para_sorteio)
  
  
  # 3. Emparelhar Nomes e Atividades
  
  # O zip() combina o primeiro nome com a primeira atividade, o segundo nome com a segunda, etc.
  # Como a lista de atividades foi embaralhada, o emparelhamento é aleatório.
  pares_sorteados = dict(zip(nomes, atividades_para_sorteio))
  
  return pares_sorteados

# --- Listas de Exemplo ---
nomes_participantes = ["Ana Livia", "Natanael", "Fernanda", "Pedro"]
atividades_disponiveis = ["proxy", "portal", "hotsite", "sign"]

# --- Execução do Programa ---
resultado = sortear_atividades(nomes_participantes, atividades_disponiveis)

# --- Impressão dos Resultados ---
print("### 📋 Resultado do Sorteio de Atividades ###")
print("-" * 35)

# O resultado é um dicionário, perfeito para iteração
for nome, atividade in resultado.items():
  print (f"**{nome}** faz: **{atividade}**")