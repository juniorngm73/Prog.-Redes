from hashlib import sha256
from time import time
from typing import Tuple


# Usamos 'to_bytes' no lugar de 'struct.pack' para ter controle explícito do endianness
# e para que a conversão de Nonce para bytes seja Big-Endian (conforme a interpretação
# mais rigorosa do pedido original para a ordem de bytes no processo).

def findNonce(dataToHash: bytes, bitsToBeZero: int) -> Tuple[int, float]:
    # Pré-cálculos para verificação eficiente
    full_zero_bytes = bitsToBeZero // 8
    remaining_zero_bits = bitsToBeZero % 8

    # Máscara para verificar os bits restantes no byte parcial (se houver)
    # Ex: 3 bits restantes -> 0b11100000 (0xE0)
    partial_byte_mask = (0xFF << (8 - remaining_zero_bits)) & 0xFF

    timestart = time()
    nonce_candidate = 0

    # O nonce é de 4 bytes (2**32)
    while nonce_candidate < 2 ** 32:

        # 1. Nonce de 4 bytes em formato Big-Endian (ajuste para consistência)
        # O retorno é o inteiro 'nonce_candidate'.
        nonce_bytes = nonce_candidate.to_bytes(4, byteorder='big')

        # 2. Juntar nonce + dados
        input_data = nonce_bytes + dataToHash

        # 3. Calcular o hash
        hash_result = sha256(input_data).digest()  # hash_result é de 32 bytes

        # 4. Verificação de Dificuldade (otimizada):

        # a) Verificar bytes inteiros de zeros
        if full_zero_bytes > 0 and hash_result[:full_zero_bytes] != b'\x00' * full_zero_bytes:
            nonce_candidate += 1
            continue  # Próximo nonce

        # b) Verificar o byte parcial
        if remaining_zero_bits > 0:
            target_byte = hash_result[full_zero_bytes]
            if (target_byte & partial_byte_mask) != 0:
                nonce_candidate += 1
                continue  # Próximo nonce

        # 5. Se chegou aqui, o nonce foi encontrado
        time_taken = time() - timestart

        # 6. Devolver o nonce (inteiro) e o tempo
        return nonce_candidate, time_taken

    # Caso improvável de não encontrar o nonce após 2^32 tentativas
    return -1, time() - timestart


# Bloco de teste (ADICIONE ISSO APÓS A FUNÇÃO findNonce)
# ---

# Dados de teste (devem ser BYTES)
TEST_DATA = b"Teste de mineracao simples"
TEST_BITS = 20  # Uma dificuldade razoável para teste (cerca de 65.536 tentativas)

print(f"Iniciando teste de mineração:")
print(f"Dados: {TEST_DATA.decode()}")
print(f"Dificuldade: {TEST_BITS} bits zero")

# Chamada da função
nonce_encontrado, tempo_gasto = findNonce(TEST_DATA, TEST_BITS)

# ---

print("\n--- Resultado da Função ---")
if nonce_encontrado != -1:
    # Recalcular o hash para exibir o resultado completo
    nonce_bytes = nonce_encontrado.to_bytes(4, byteorder='big')
    input_data = nonce_bytes + TEST_DATA
    hash_final = sha256(input_data).digest()

    # Conversão para binário e hexadecimal para visualização
    hash_bin_view = ''.join([f'{i:08b}' for i in hash_final])
    hash_hex_view = hash_final.hex()

    print(f"✅ SUCESSO! Nonce encontrado: {nonce_encontrado}")
    print(f"⏱️ Tempo Gasto: {tempo_gasto:.4f} segundos")
    print(f"📜 Hash Final (256 bits):")

    # Exibe o hash e destaca os zeros iniciais
    print(f"   Binário: {'\033[92m'}{hash_bin_view[:TEST_BITS]}{'\033[0m'}{hash_bin_view[TEST_BITS:]}")
    print(f"   Comprimento da string binária do Hash: {len(hash_bin_view)} bits")
    print(f"   Hexa:    {hash_hex_view}")
    print(f"   (O hash começa com {TEST_BITS} zeros, marcados em verde)")
else:
    print("❌ FALHA! Nonce não encontrado no intervalo de 2^32.")

# ---
# Remova este bloco para o arquivo final 'hash_utils.py'