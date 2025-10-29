from funcoes import findnounce

#1. Defina os parâmetros para a chamada da função
dados = "Bloco de Dados!"
dificuldade = int(input('Digite um Número Inteiro: '))

# 2. Chama a função e armazena os valores retornados (o nonce e o tempo)
nonce_encontrado, tempo_gasto = findnounce(dados, dificuldade)

# 3. Imprime os resultados de forma formatada
print(f"--- Resultado da Prova de Trabalho (Dificuldade: {dificuldade} bits) ---")
print(f"Dados usados: '{dados}'")
print(f"Nonce Encontrado: {nonce_encontrado}")
print(f"Tempo Gasto: {tempo_gasto:.4f} segundos")