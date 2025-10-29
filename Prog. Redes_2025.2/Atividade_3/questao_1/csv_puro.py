import csv
import os
import io  # Importar para manipulação de strings/bytes em memória

from funcoes import findnounce

# 1. Definição do bloco de dados e parâmetros
dados = "Bloco de Dados!"
NUM_ENTRADAS = 4
dificuldades = []
resultados = []  # Inicializa a lista que será usada para o CSV

# --- 2. Captura de Entradas (Dificuldades) ---

print(f"Digite exatamente {NUM_ENTRADAS} números inteiros para as Dificuldades:")

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

# --- 3. Processamento (Chamada da função findnounce) ---

print(f"\n--- Iniciando Prova de Trabalho para {len(dificuldades)} dificuldades: {dificuldades} ---")

for dificuldade in dificuldades:
    print(f"\n-> Processando dificuldade: {dificuldade} bits...")

    # Chama a função findnounce
    nonce_encontrado, tempo_gasto = findnounce(dados, dificuldade)

    # Armazena o resultado no formato de dicionário para o CSV
    resultados.append({
        'Texto a validar': dados,
        'Bits em zero': dificuldade,
        'nonce': nonce_encontrado,
        # Formata o tempo para ter no máximo 4 casas decimais para o CSV
        'Tempo (em s)': f"{tempo_gasto:.4f}"
    })

    # Imprime um resumo simples no console durante o processamento
    print(f"   [OK] Nonce: {nonce_encontrado}, Tempo: {tempo_gasto:.4f}s")

# --- 4. Geração do Arquivo CSV ---

NOME_ARQUIVO = 'resultados_mineracao.csv'
nomes_colunas = ['Texto a validar', 'Bits em zero', 'nonce', 'Tempo (em s)']

try:
    # 4.1. Escreve o CSV inicialmente com o delimitador padrão (ponto-e-vírgula)
    with open(NOME_ARQUIVO, 'w', newline='', encoding='utf-8') as arquivo_csv:

        # Cria o escritor de dicionários
        escritor = csv.DictWriter(arquivo_csv, fieldnames=nomes_colunas, delimiter=';')

        escritor.writeheader()
        escritor.writerows(resultados)

    # 4.2. Lê o arquivo, adiciona o espaço e reescreve o arquivo

    # Lê o conteúdo do arquivo
    with open(NOME_ARQUIVO, 'r', encoding='utf-8') as arquivo_csv:
        conteudo = arquivo_csv.read()

    # Substitui o delimitador ';' por '; ' (ponto-e-vírgula seguido de espaço)
    conteudo_formatado = conteudo.replace(';', '  #  ')


    # Reescreve o arquivo com o novo espaçamento
    with open(NOME_ARQUIVO, 'w', encoding='utf-8') as arquivo_csv:
        arquivo_csv.write(conteudo_formatado)

    # --- Saída de confirmação ---
    print("\n==============================================")
    print("Processamento Concluído.")
    print("O arquivo CSV foi formatado com espaços após cada #.")
    # Exibe o caminho absoluto do arquivo para facilitar a localização
    print(f"Resultados salvos com sucesso em: {os.path.abspath(NOME_ARQUIVO)}")
    print("==============================================")

except IOError:
    print(f"Erro ao tentar escrever ou ler o arquivo: {NOME_ARQUIVO}")
