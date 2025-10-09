def validar_ip(entrada):  # Função  'validar_ip' ; Parâmetro  'entrada'
    """
    Lê um IP do usuário, repetindo a solicitação (entrada) até que
    o IP seja válido (formato IPv4: quatro octetos entre 0 e 255).
    """
    while True:
        ip = input(entrada)

        octetos = ip.split('.')

        # 1. Checa o número de octetos
        if len(octetos) != 4:
            print(f"ERRO: O IP '{ip}' é INVÁLIDO. Tente Novamente.")
            continue

        # 2. Checa o valor de cada octeto
        is_valid = True
        for octeto in octetos:
            try:
                valor = int(octeto)
                if valor < 0 or valor > 255:
                    is_valid = False
                    break
            except ValueError:
                is_valid = False
                break

        # 3. Retorna o IP se for válido, ou exibe erro e repete
        if is_valid:
            return ip  # IP válido: retorna e encerra a função
        else:
            print(
                f"ERRO: O IP '{ip}' é INVÁLIDO. Tente Novamente.")


#  CHAMANDO  A FUNÇÃO
# Chamada 1: Chama 'validar_ip' e a mensagem passada é o valor do parâmetro 'entrada'
ip1 = validar_ip('Digite o PRIMEIRO IP válido: ')

# Chamada 2:Chama 'validar_ip' e a mensagem passada é o valor do parâmetro 'entrada'
ip2 = validar_ip('Digite o SEGUNDO IP válido: ')
mask = int(input ("Digite o tamanho da máscara de rede (em bits): "))



ip1_int = ip1.split('.')
ip10 = 0
for i, ip1_int in enumerate (ip1_int):
    pot = 3 - i
    ip10 = ip10 + int(ip1_int)* (256 ** pot)
ip10b = (f'{ip10:032b}')

ip2_int = ip2.split('.')
ip20 = 0
for i, ip2_int in enumerate (ip2_int):
    pot = 3 - i
    ip20 = ip20 + int(ip2_int)* (256 ** pot)
ip20b = (f'{ip20:032b}')

bitsHost = 32 - mask
mask10 = ((2**32) - 1) - ((2**bitsHost) - 1)
host_mask = (2**bitsHost) - 1
net1 = ip10 & mask10
net2 = ip20 & mask10
gw1 = net1 | 1
gw2 = net2 | 1
bcast1 = net1 | host_mask
bcast2 = net2 | host_mask
net1b = f"{net1:032b}"
net2b = f"{net2:032b}"
gw1b = f'{gw1:032b}'
gw2b = f'{gw2:032b}'
bc1b = f'{bcast1:032b}'
bc2b = f'{bcast2:032b}'
print("*" * 60)
if net1 == net2:
    print (" " * 20 + "Mesma Rede!!!")
else:
    print (" " * 20 + "Redes Diferentes!!!")



ip1_binario = ip10b
# 1. Fatiar a string binária em 4 octetos (grupos de 8 bits)
octeto_1 = ip1_binario[0:8]     # 11000000
octeto_2 = ip1_binario[8:16]    # 10101000
octeto_3 = ip1_binario[16:24]   # 00001010
octeto_4 = ip1_binario[24:32]   # 00001100

# 2. Juntar os octetos com um ponto ('.')
ip1_binario_formatado = f"{octeto_1}.{octeto_2}.{octeto_3}.{octeto_4}"

# Conversão de Binário para Decimal
decimal_1 = int(octeto_1, 2)
decimal_2 = int(octeto_2, 2)
decimal_3 = int(octeto_3, 2)
decimal_4 = int(octeto_4, 2)

# Juntar os valores decimais com um ponto ('.')
ip1_decimal = f"{decimal_1}.{decimal_2}.{decimal_3}.{decimal_4}"


ip2_binario = ip20b
# 1. Fatiar a string binária em 4 octetos (grupos de 8 bits)
octeto_1 = ip2_binario[0:8]     # 11000000
octeto_2 = ip2_binario[8:16]    # 10101000
octeto_3 = ip2_binario[16:24]   # 00001010
octeto_4 = ip2_binario[24:32]   # 00001100

# 2. Juntar os octetos com um ponto ('.')
ip2_binario_formatado = f"{octeto_1}.{octeto_2}.{octeto_3}.{octeto_4}"

# Conversão de Binário para Decimal
decimal_1 = int(octeto_1, 2)
decimal_2 = int(octeto_2, 2)
decimal_3 = int(octeto_3, 2)
decimal_4 = int(octeto_4, 2)

# Juntar os valores decimais com um ponto ('.')
ip2_decimal = f"{decimal_1}.{decimal_2}.{decimal_3}.{decimal_4}"


net1_binario = net1b
# 1. Fatiar a string binária em 4 octetos (grupos de 8 bits)
octeto_1 = net1_binario[0:8]     # 11000000
octeto_2 = net1_binario[8:16]    # 10101000
octeto_3 = net1_binario[16:24]   # 00001010
octeto_4 = net1_binario[24:32]   # 00001100

# 2. Juntar os octetos com um ponto ('.')
net1_binario_formatado = f"{octeto_1}.{octeto_2}.{octeto_3}.{octeto_4}"

# Conversão de Binário para Decimal
decimal_1 = int(octeto_1, 2)
decimal_2 = int(octeto_2, 2)
decimal_3 = int(octeto_3, 2)
decimal_4 = int(octeto_4, 2)

# Juntar os valores decimais com um ponto ('.')
net1_decimal = f"{decimal_1}.{decimal_2}.{decimal_3}.{decimal_4}"


net2_binario = net2b
# 1. Fatiar a string binária em 4 octetos (grupos de 8 bits)
octeto_1 = net2_binario[0:8]     # 11000000
octeto_2 = net2_binario[8:16]    # 10101000
octeto_3 = net2_binario[16:24]   # 00001010
octeto_4 = net2_binario[24:32]   # 00001100

# 2. Juntar os octetos com um ponto ('.')
net2_binario_formatado = f"{octeto_1}.{octeto_2}.{octeto_3}.{octeto_4}"

# Conversão de Binário para Decimal
decimal_1 = int(octeto_1, 2)
decimal_2 = int(octeto_2, 2)
decimal_3 = int(octeto_3, 2)
decimal_4 = int(octeto_4, 2)

# Juntar os valores decimais com um ponto ('.')
net2_decimal = f"{decimal_1}.{decimal_2}.{decimal_3}.{decimal_4}"


gw1_binario = gw1b
# 1. Fatiar a string binária em 4 octetos (grupos de 8 bits)
octeto_1 = gw1_binario[0:8]     # 11000000
octeto_2 = gw1_binario[8:16]    # 10101000
octeto_3 = gw1_binario[16:24]   # 00001010
octeto_4 = gw1_binario[24:32]   # 00001100

# 2. Juntar os octetos com um ponto ('.')
gw1_binario_formatado = f"{octeto_1}.{octeto_2}.{octeto_3}.{octeto_4}"

# Conversão de Binário para Decimal
decimal_1 = int(octeto_1, 2)
decimal_2 = int(octeto_2, 2)
decimal_3 = int(octeto_3, 2)
decimal_4 = int(octeto_4, 2)

# Juntar os valores decimais com um ponto ('.')
gw1_decimal = f"{decimal_1}.{decimal_2}.{decimal_3}.{decimal_4}"


gw2_binario = gw2b
# 1. Fatiar a string binária em 4 octetos (grupos de 8 bits)
octeto_1 = gw2_binario[0:8]     # 11000000
octeto_2 = gw2_binario[8:16]    # 10101000
octeto_3 = gw2_binario[16:24]   # 00001010
octeto_4 = gw2_binario[24:32]   # 00001100

# 2. Juntar os octetos com um ponto ('.')
gw2_binario_formatado = f"{octeto_1}.{octeto_2}.{octeto_3}.{octeto_4}"

# Conversão de Binário para Decimal
decimal_1 = int(octeto_1, 2)
decimal_2 = int(octeto_2, 2)
decimal_3 = int(octeto_3, 2)
decimal_4 = int(octeto_4, 2)

# Juntar os valores decimais com um ponto ('.')
gw2_decimal = f"{decimal_1}.{decimal_2}.{decimal_3}.{decimal_4}"


bc1_binario = bc1b
# 1. Fatiar a string binária em 4 octetos (grupos de 8 bits)
octeto_1 = bc1_binario[0:8]     # 11000000
octeto_2 = bc1_binario[8:16]    # 10101000
octeto_3 = bc1_binario[16:24]   # 00001010
octeto_4 = bc1_binario[24:32]   # 00001100

# 2. Juntar os octetos com um ponto ('.')
bc1_binario_formatado = f"{octeto_1}.{octeto_2}.{octeto_3}.{octeto_4}"

# Conversão de Binário para Decimal
decimal_1 = int(octeto_1, 2)
decimal_2 = int(octeto_2, 2)
decimal_3 = int(octeto_3, 2)
decimal_4 = int(octeto_4, 2)

# Juntar os valores decimais com um ponto ('.')
bc1_decimal = f"{decimal_1}.{decimal_2}.{decimal_3}.{decimal_4}"


bc2_binario = bc2b
# 1. Fatiar a string binária em 4 octetos (grupos de 8 bits)
octeto_1 = bc2_binario[0:8]     # 11000000
octeto_2 = bc2_binario[8:16]    # 10101000
octeto_3 = bc2_binario[16:24]   # 00001010
octeto_4 = bc2_binario[24:32]   # 00001100

# 2. Juntar os octetos com um ponto ('.')
bc2_binario_formatado = f"{octeto_1}.{octeto_2}.{octeto_3}.{octeto_4}"

# Conversão de Binário para Decimal
decimal_1 = int(octeto_1, 2)
decimal_2 = int(octeto_2, 2)
decimal_3 = int(octeto_3, 2)
decimal_4 = int(octeto_4, 2)

# Juntar os valores decimais com um ponto ('.')
bc2_decimal = f"{decimal_1}.{decimal_2}.{decimal_3}.{decimal_4}"

print("*" * 60)
print('Primeiro IP:')
print(f"IP1  Octetos Binário: {ip1_binario_formatado}")
print(f"IP1  Octetos Decimal: {ip1_decimal}")
print(f"Net1 Octetos Binário: {net1_binario_formatado}")
print(f"Net1 Octetos Decimal: {net1_decimal}")
print(f"Gw_1 Octetos Binário: {gw1_binario_formatado}")
print(f"Gw_1 Octetos Decimal: {gw1_decimal}")
print(f"BC_1 Octetos Binário: {bc1_binario_formatado}")
print(f"BC_1 Octetos Decimal: {bc1_decimal}")
print("*" * 60)
print('Segundo IP:')
print(f"IP2  Octetos Binário: {ip2_binario_formatado}")
print(f"IP2  Octetos Decimal: {ip2_decimal}")
print(f"Net2 Octetos Binário: {net2_binario_formatado}")
print(f"Net2 Octetos Decimal: {net2_decimal}")
print(f"Gw_2 Octetos Binário: {gw2_binario_formatado}")
print(f"Gw_2 Octetos Decimal: {gw2_decimal}")
print(f"BC_2 Octetos Binário: {bc2_binario_formatado}")
print(f"BC_2 Octetos Decimal: {bc2_decimal}")
print("*" * 60)