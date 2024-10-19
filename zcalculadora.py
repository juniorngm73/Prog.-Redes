def validar_ip(ip):
    try:
        octetos = ip.split('.')
        if len(octetos) != 4:
            return False

        for octeto in octetos:

            if  not octeto.isdigit() or not 0 <= int(octeto) <= 255:
                return False

        return True
    except ValueError:
        print(f'O endereço IP contém caracteres inválidos.')
        return False


def calcular_subrede(ip, mascara_inicial, mascara_final):
    """
    Calcula as informações de sub-rede para um intervalo de máscaras.

    Args:
        ip (str): Endereço IP em formato decimal com pontos.
        mascara_inicial (int): Máscara de rede inicial em notação CIDR.
        mascara_final (int): Máscara de rede final em notação CIDR.
    """

    # Converter IP para binário
    ip_binario = ''.join([bin(int(x))[2:].zfill(8) for x in ip.split('.')])

    for mascara in range(mascara_inicial, mascara_final + 1):
        # Máscara em binário
        mascara_binaria = '1' * mascara + '0' * (32 - mascara)

        # Calcular endereço de rede
        endereco_rede_binario = ip_binario[:mascara] + '0' * (32 - mascara)
        endereco_rede = '.'.join([str(int(endereco_rede_binario[i:i+8], 2)) for i in range(0, 32, 8)])

        # Calcular primeiro host
        primeiro_host = bin_to_ip(endereco_rede_binario[:mascara] + '0' * (31 - mascara) + '1')

        # Calcular último host
        ultimo_host = bin_to_ip(endereco_rede_binario[:mascara] + '1' * (31 - mascara) + '0')

        # Calcular endereço de broadcast
        broadcast_binario = endereco_rede_binario[:mascara] + '1' * (32 - mascara)
        broadcast = bin_to_ip(broadcast_binario)

        # Número de hosts válidos
        hosts_validos = 2**(32 - mascara) - 2

        print(f"Máscara / {mascara}")
        print(f"Endereço de Rede: {endereco_rede}")
        print(f"Primeiro Host: {primeiro_host}")
        print(f"Último Host: {ultimo_host}")
        print(f"Endereço de Broadcast: {broadcast}")
        print(f"Máscara em Binário: {mascara_binaria}")
        print(f"Número de Hosts Válidos: {hosts_validos}")


def bin_to_ip(binario):
    """Converte um endereço binário para decimal com pontos."""
    return '.'.join([str(int(binario[i:i+8], 2)) for i in range(0, 32, 8)])


while True:
    ip = input(' Digite um endereço IP: ')
    if validar_ip(ip):
        break
    else:
        print("O endereço IP é inválido, tente novamente.")

mascara_inicial = int(input("Máscara Inicial: "))
mascara_final = int(input("Máscara Final: "))
calcular_subrede(ip, mascara_inicial, mascara_final)
if __name__ == "__calcular_subrede__":
    calcular_subrede(ip, mascara_inicial, mascara_final)
