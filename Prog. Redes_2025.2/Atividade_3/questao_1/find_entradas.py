import os
from funcoes import findnounce

# 1. Definição do bloco de dados e parâmetros
dados = "Bloco de Dados!"
NUM_ENTRADAS = 4
dificuldades = []
resultados = []  # Inicializa a lista que armazenará os resultados formatados

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

    # Armazena o resultado com CHAVES que correspondem aos cabeçalhos da tabela
    resultados.append({
        'Texto a validar': dados,
        'Bits em zero': dificuldade,
        'nonce': nonce_encontrado,
        'Tempo (em s)': tempo_gasto  # Armazena o float, será formatado na impressão
    })

    # Imprime um resumo simples no console durante o processamento
    print(f"   [OK] Nonce: {nonce_encontrado}, Tempo: {tempo_gasto:.4f}s")

# --- 4. Impressão na Tela em Formato de Tabela ---

# Definindo a linha de separação
# Larguras: Texto(20), Bits(14), Nonce(12), Tempo(14)
separador_linha = "|" + "-" * 20 + "|" + "-" * 14 + "|" + "-" * 12 + "|" + "-" * 14 + "|"

print("\n\n==============================================")
print("RELATÓRIO DE TESTES (Resultados da Tabela)")
print("==============================================")

# Imprime o cabeçalho
# Nota: As larguras são ajustadas para que o texto do cabeçalho caiba
print(f"| {'Texto a validar':<20} | {'Bits em zero':<12} | {'nonce':<10} | {'Tempo (em s)':<12} |")
print(separador_linha)

# Imprime cada linha de resultado
for resultado in resultados:
    # Formata o tempo e adiciona 's', garantindo que o alinhamento total seja 14 caracteres
    tempo_formatado = f"{resultado['Tempo (em s)']:.4f}s"

    print(
        f"| {resultado['Texto a validar']:<20} | "
        f"{resultado['Bits em zero']:<12} | "
        f"{resultado['nonce']:<10} | "
        f"{tempo_formatado:<14} |"
    )
print(separador_linha)
