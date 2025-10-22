from hashlib import sha256
from time import time
from struct import pack


def findnounce(data_To_Hash, bitsToBeZero, start_nonce=0):
    """
    Encontra o nonce e retorna o nonce e o tempo gasto.
    (Removidas as impressões para usar o valor retornado)
    """
    timestart = time()
    current_nonce = start_nonce

    target_prefix = "0" * bitsToBeZero

    while True:
        # 1. Cria o hash e concatena o nonce (little-endian) + dados (codificados)
        hashbinario = sha256()
        hashbinario.update(pack("<i", current_nonce) + data_To_Hash.encode("utf-8"))
        hashbinario = hashbinario.digest()

        # 2. Converte para binário para checagem da dificuldade
        hashtextobinario = ''.join([f'{i:08b}' for i in hashbinario])

        if hashtextobinario.startswith(target_prefix):
            break

        current_nonce += 1

    tempo_total = time() - timestart

    # Retorna o nonce e o tempo
    return current_nonce, tempo_total

