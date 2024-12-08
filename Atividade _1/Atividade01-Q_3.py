import random

def carregar_palavras(arquivo):
    """Carrega palavras de um arquivo e retorna uma lista."""
    with open(arquivo, 'r') as f:
        return [palavra.strip() for palavra in f if 5 <= len(palavra) <= 8]

def sortear_palavra(palavras):
    """Sorteia uma palavra aleatória da lista."""
    return random.choice(palavras)

def verificar_palavra(palpite, palavra_secreta):
    """Verifica se o palpite está correto e retorna um feedback."""
    resultado = []
    for i in range(len(palavra_secreta)):
        if palpite[i] == palavra_secreta[i]:
            resultado.append('🟩')
        elif palpite[i] in palavra_secreta:
            resultado.append('🟨')
        else:
            resultado.append('⬜')
    return ''.join(resultado)

def jogar():
    """Função principal do jogo."""
    arquivo = 'atividade1.txt'
    palavras = carregar_palavras(arquivo)
    palavra_secreta = sortear_palavra(palavras)

    for tentativa in range(6):
        palpite = input(f"Tentativa {tentativa+1}: ").lower()
        if len(palpite) != len(palavra_secreta):
            print("A palavra deve ter o mesmo número de letras.")
            continue

        resultado = verificar_palavra(palpite, palavra_secreta)
        print(resultado)

        if resultado == '🟩' * len(palavra_secreta):
            print("Parabéns, você acertou!")
            return
    print(f"Você perdeu. A palavra era: {palavra_secreta}")

if __name__ == "__main__":
    jogar()