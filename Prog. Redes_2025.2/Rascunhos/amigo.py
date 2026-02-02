import random
import os
import time

def limpar_tela():
  """Limpa o console de forma compatível com Windows ('cls') e outros ('clear')."""
  # 'nt' é o nome do OS para Windows
  if os.name == 'nt':
    os.system('cls')
  else:
    # 'posix' é o nome do OS para Linux, macOS e outros
    os.system('clear')

def sortear_amigo_secreto(nomes):
  """
  Realiza o sorteio do Amigo Secreto, garantindo que ninguém tire a si mesmo.
  O algoritmo tenta diversas vezes até encontrar uma combinação válida.
  """
  doadores = nomes[:]
  recebedores = nomes[:]
  
  max_tentativas = 100
  tentativas = 0
  sorteio_valido = False

  while not sorteio_valido and tentativas < max_tentativas:
    random.shuffle(recebedores)
    invalido = [doador for doador, recebedor in zip(doadores, recebedores) if doador == recebedor]
    
    if not invalido:
      sorteio_valido = True
    else:
      tentativas += 1
      
  # Se o sorteio não for válido após tentativas (muito raro), forçamos a correção
  if not sorteio_valido:
     random.shuffle(recebedores)
     try:
       index_invalido = next(i for i, (d, r) in enumerate(zip(doadores, recebedores)) if d == r)
       index_troca = (index_invalido + 1) % len(doadores)
       recebedores[index_invalido], recebedores[index_troca] = recebedores[index_troca], recebedores[index_invalido]
     except StopIteration:
        pass # Sem inválidos para corrigir

  resultado = dict(zip(doadores, recebedores))
  return resultado

# ----------------------------------------------------
# --- Execução do Programa Principal ---
# ----------------------------------------------------

# 1. Lista de Participantes
participantes = ["Alice", "Bernardo", "Clara", "David", "Eva", "Fábio", "Giovana", "Henrique"]

# 2. Realiza o Sorteio Completo
sorteio_completo = sortear_amigo_secreto(participantes)
total_pares = len(participantes)

# 3. Inicia a Revelação Sequencial
limpar_tela()

print("### 🎅 Sorteio de Amigo Secreto - Revelação Oculta 🎅 ###")
print("-" * 55)

# A lista de chaves (doadores) será a ordem de revelação
doadores_para_revelar = list(sorteio_completo.keys())

for i, doador in enumerate(doadores_para_revelar):
    
  pares_revelados = i
  pares_restantes = total_pares - i
  
  if i > 0:
    print(f"\nStatus: {pares_revelados} pares revelados | {pares_restantes} pares restantes.")
    
  print(f"\n*** PRÓXIMO A TIRAR: {doador} ***")
  
  # Espera o usuário confirmar para ver seu par
  input("Pressione ENTER para **REVELAR** seu Amigo Secreto...")
  
  recebedor = sorteio_completo[doador]
  
  # Revela o par
  print("-" * 55)
  print(f"🎉 **{doador}** tirou **{recebedor}**")
  print("-" * 55)
  
  # Pausa para a pessoa ler e guardar a informação
  input("\nPressione ENTER para **OCULTAR** a tela e chamar o próximo...")
  
  # OCULTA a informação e limpa a tela para a próxima pessoa
  limpar_tela()

print("### 🎊 Sorteio Concluído! 🎊 ###")
print("Todos os pares foram sorteados. Obrigado por participar!")
