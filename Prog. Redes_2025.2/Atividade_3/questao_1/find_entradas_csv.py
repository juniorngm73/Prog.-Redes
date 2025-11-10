from funcoes import findnounce
import csv
import os

# 1. Defina o bloco de dados (permanece fixo para todos os testes)
dados = "Bloco de Dados!"

# --- Captura EXATAMENTE 4 Dificuldades (Mantida do código anterior) ---

NUM_ENTRADAS = 4
dificuldades = []

print(f"Digite exatamente {NUM_ENTRADAS} números inteiros para as Dificuldades:")

# Loop for para coletar exatamente 4 entradas
for i in range(NUM_ENTRADAS):
    while True:
        entrada = input(f'Dificuldade #{i + 1} de {NUM_ENTRADAS}: ').strip()

        try:
            dificuldade = int(entrada)
            if dificuldade < 1:
                print("Por favor, digite um número inteiro positivo.")
                continue
            dificuldades.append(dificuldade)
            break
        except ValueError:
            print("Entrada inválida. Por favor, digite um número inteiro.")

# Fim da coleta de entradas. Agora, processamos.

print(f"\n--- Iniciando Prova de Trabalho para {len(dificuldades)} dificuldades: {dificuldades} ---")

# 2. Loop para chamar a função para cada dificuldade
resultados = []

for dificuldade in dificuldades:
    print(f"\n-> Processando dificuldade: {dificuldade} bits...")

    nonce_encontrado, tempo_gasto = findnounce(dados, dificuldade)

    resultados.append({
        'Texto a validar': dados,
        'Bits em zero': dificuldade,
        'nonce': nonce_encontrado,
        'Tempo (em s)': tempo_gasto
    })

# 3. Escrita dos Resultados no Arquivo CSV (Mantida do código anterior)
NOME_ARQUIVO = 'resultados_mineracao.csv'
nomes_colunas = ['Texto a validar', 'Bits em zero', 'nonce', 'Tempo (em s)']

try:
    with open(NOME_ARQUIVO, 'w', newline='', encoding='utf-8') as arquivo_csv:
        escritor = csv.DictWriter(arquivo_csv, fieldnames=nomes_colunas, delimiter=';')
        escritor.writeheader()
        escritor.writerows(resultados)

    print("\n==============================================")
    print("Processamento Concluído e CSV Salvo.")
    print(f"Arquivo: {os.path.abspath(NOME_ARQUIVO)}")
    print("==============================================")

except IOError:
    print(f"Erro ao tentar escrever no arquivo: {NOME_ARQUIVO}")

# --- MUDANÇA APLICADA AQUI: IMPRESSÃO COM SEPARADORES ---

print("\n------------------------------------------------")
print("RELATÓRIO DE TESTES (Resultados da Tabela)")
print("------------------------------------------------")

# Imprime o cabeçalho uma vez
print(f"| {'Texto a validar':<18} | {'Bits em zero':<12} | {'nonce':<10} | {'Tempo (em s)':<12} |")
print("|" + "-" * 20 + "|" + "-" * 14 + "|" + "-" * 12 + "|" + "-" * 14 + "|")

for resultado in resultados:
    # Imprime cada linha
    print(
        f"| {resultado['Texto a validar']:<18} | "
        f"{resultado['Bits em zero']:<12} | "
        f"{resultado['nonce']:<10} | "
        f"{resultado['Tempo (em s)']:.4f}s"
    )
    # Imprime uma linha separadora após cada resultado
    print("|" + "=" * 20 + "|" + "=" * 14 + "|" + "=" * 12 + "|" + "=" * 14 + "|")