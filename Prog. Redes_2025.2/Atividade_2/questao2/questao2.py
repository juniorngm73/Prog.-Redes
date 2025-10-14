def validar_ip(entrada):  # Função 'validar_ip' ; Parâmetro 'entrada'
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

ip1l = [int(x) for x in ip1.split('.')]
ip2l = [int(x) for x in ip2.split('.')]
ip1b = bytes (ip1l)
ip2b = bytes (ip2l)
ip1i = int.from_bytes(ip1b)
ip2i = int.from_bytes(ip2b)

host = 32 - mask

net1 = ip1i >> host << host
net2 = ip2i >> host << host

bcast1 = ip1i | ((1 << host) - 1)
bcast2 = ip2i | ((1 << host) - 1)
gw1 = net1 | 1
gw2 = net2 | 1

print("*" * 70)
if net1 == net2:
    print (" " * 25 + "Mesma Rede!!!")
else:
    print (" " * 25 + "Redes Diferentes!!!")
print("*" * 70)

ip1_binario =  f'{ip1i:032b}'
# 1. Fatiar a string binária em 4 octetos (grupos de 8 bits)
octeto_1 = ip1_binario[0:8]
octeto_2 = ip1_binario[8:16]
octeto_3 = ip1_binario[16:24]
octeto_4 = ip1_binario[24:32]

# 2. Juntar os octetos com um ponto ('.')
ip1_binario_formatado = f"{octeto_1}.{octeto_2}.{octeto_3}.{octeto_4}"
print('O IP1 Binario em Octetos é: ', (ip1_binario_formatado))
#print (f'IP 1: {ip1i :032b}')
# Conversão de Binário para Decimal
decimal_1 = int(octeto_1, 2)
decimal_2 = int(octeto_2, 2)
decimal_3 = int(octeto_3, 2)
decimal_4 = int(octeto_4, 2)

# Juntar os valores decimais com um ponto ('.')
ip1_decimal = f"{decimal_1}.{decimal_2}.{decimal_3}.{decimal_4}"
print('O IP1 Decimal em Octetos é: ', (ip1_decimal))

net1_binario =  f'{net1:032b}'
# 1. Fatiar a string binária em 4 octetos (grupos de 8 bits)
octeto_1 = net1_binario[0:8]
octeto_2 = net1_binario[8:16]
octeto_3 = net1_binario[16:24]
octeto_4 = net1_binario[24:32]

# 2. Juntar os octetos com um ponto ('.')
net1_binario_formatado = f"{octeto_1}.{octeto_2}.{octeto_3}.{octeto_4}"
print('A Rede 1 Binario em Octetos é: ', (net1_binario_formatado))

# Conversão de Binário para Decimal
decimal_1 = int(octeto_1, 2)
decimal_2 = int(octeto_2, 2)
decimal_3 = int(octeto_3, 2)
decimal_4 = int(octeto_4, 2)

# Juntar os valores decimais com um ponto ('.')
net1_decimal = f"{decimal_1}.{decimal_2}.{decimal_3}.{decimal_4}"
print('A Rede 1 Decimal em Octetos é: ', (net1_decimal))

gw1_binario =  f'{gw1:032b}'
# 1. Fatiar a string binária em 4 octetos (grupos de 8 bits)
octeto_1 = gw1_binario[0:8]
octeto_2 = gw1_binario[8:16]
octeto_3 = gw1_binario[16:24]
octeto_4 = gw1_binario[24:32]

# 2. Juntar os octetos com um ponto ('.')
gw1_binario_formatado = f"{octeto_1}.{octeto_2}.{octeto_3}.{octeto_4}"
print('O Gateway 1 Binario em Octetos é: ', (gw1_binario_formatado))

# Conversão de Binário para Decimal
decimal_1 = int(octeto_1, 2)
decimal_2 = int(octeto_2, 2)
decimal_3 = int(octeto_3, 2)
decimal_4 = int(octeto_4, 2)

# Juntar os valores decimais com um ponto ('.')
gw1_decimal = f"{decimal_1}.{decimal_2}.{decimal_3}.{decimal_4}"
print('O Gateway 1 Decimal em Octetos é: ', (gw1_decimal))

bcast1_binario =  f'{bcast1:032b}'
# 1. Fatiar a string binária em 4 octetos (grupos de 8 bits)
octeto_1 = bcast1_binario[0:8]
octeto_2 = bcast1_binario[8:16]
octeto_3 = bcast1_binario[16:24]
octeto_4 = bcast1_binario[24:32]

# 2. Juntar os octetos com um ponto ('.')
bcast1_binario_formatado = f"{octeto_1}.{octeto_2}.{octeto_3}.{octeto_4}"
print('O Broadcast 1 Binario em Octetos é: ', (bcast1_binario_formatado))

# Conversão de Binário para Decimal
decimal_1 = int(octeto_1, 2)
decimal_2 = int(octeto_2, 2)
decimal_3 = int(octeto_3, 2)
decimal_4 = int(octeto_4, 2)

# Juntar os valores decimais com um ponto ('.')
bcast1_decimal = f"{decimal_1}.{decimal_2}.{decimal_3}.{decimal_4}"
print('O Broadcast 1 Decimal em Octetos é: ', (bcast1_decimal))
print("*" * 70)

ip2_binario =  f'{ip2i:032b}'
# 1. Fatiar a string binária em 4 octetos (grupos de 8 bits)
octeto_1 = ip2_binario[0:8]
octeto_2 = ip2_binario[8:16]
octeto_3 = ip2_binario[16:24]
octeto_4 = ip2_binario[24:32]

# 2. Juntar os octetos com um ponto ('.')
ip2_binario_formatado = f"{octeto_1}.{octeto_2}.{octeto_3}.{octeto_4}"
print('O IP2 Binario em Octetos é: ', (ip2_binario_formatado))
#print (f'IP 1: {ip1i :032b}')
# Conversão de Binário para Decimal
decimal_1 = int(octeto_1, 2)
decimal_2 = int(octeto_2, 2)
decimal_3 = int(octeto_3, 2)
decimal_4 = int(octeto_4, 2)

# Juntar os valores decimais com um ponto ('.')
ip2_decimal = f"{decimal_1}.{decimal_2}.{decimal_3}.{decimal_4}"
print('O IP2 Decimal em Octetos é: ', (ip2_decimal))

net2_binario =  f'{net2:032b}'
# 1. Fatiar a string binária em 4 octetos (grupos de 8 bits)
octeto_1 = net2_binario[0:8]
octeto_2 = net2_binario[8:16]
octeto_3 = net2_binario[16:24]
octeto_4 = net2_binario[24:32]

# 2. Juntar os octetos com um ponto ('.')
net2_binario_formatado = f"{octeto_1}.{octeto_2}.{octeto_3}.{octeto_4}"
print('A Rede 2 Binario em Octetos é: ', (net2_binario_formatado))

# Conversão de Binário para Decimal
decimal_1 = int(octeto_1, 2)
decimal_2 = int(octeto_2, 2)
decimal_3 = int(octeto_3, 2)
decimal_4 = int(octeto_4, 2)

# Juntar os valores decimais com um ponto ('.')
net2_decimal = f"{decimal_1}.{decimal_2}.{decimal_3}.{decimal_4}"
print('A Rede 2 Decimal em Octetos é: ', (net2_decimal))

gw2_binario =  f'{gw2:032b}'
# 1. Fatiar a string binária em 4 octetos (grupos de 8 bits)
octeto_1 = gw2_binario[0:8]
octeto_2 = gw2_binario[8:16]
octeto_3 = gw2_binario[16:24]
octeto_4 = gw2_binario[24:32]

# 2. Juntar os octetos com um ponto ('.')
gw2_binario_formatado = f"{octeto_1}.{octeto_2}.{octeto_3}.{octeto_4}"
print('O Gateway 2 Binario em Octetos é: ', (gw2_binario_formatado))

# Conversão de Binário para Decimal
decimal_1 = int(octeto_1, 2)
decimal_2 = int(octeto_2, 2)
decimal_3 = int(octeto_3, 2)
decimal_4 = int(octeto_4, 2)

# Juntar os valores decimais com um ponto ('.')
gw2_decimal = f"{decimal_1}.{decimal_2}.{decimal_3}.{decimal_4}"
print('O Gateway 1 Decimal em Octetos é: ', (gw2_decimal))

bcast2_binario =  f'{bcast2:032b}'
# 1. Fatiar a string binária em 4 octetos (grupos de 8 bits)
octeto_1 = bcast2_binario[0:8]
octeto_2 = bcast2_binario[8:16]
octeto_3 = bcast2_binario[16:24]
octeto_4 = bcast2_binario[24:32]

# 2. Juntar os octetos com um ponto ('.')
bcast2_binario_formatado = f"{octeto_1}.{octeto_2}.{octeto_3}.{octeto_4}"
print('O Broadcast 1 Binario em Octetos é: ', (bcast1_binario_formatado))

# Conversão de Binário para Decimal
decimal_1 = int(octeto_1, 2)
decimal_2 = int(octeto_2, 2)
decimal_3 = int(octeto_3, 2)
decimal_4 = int(octeto_4, 2)

# Juntar os valores decimais com um ponto ('.')
bcast2_decimal = f"{decimal_1}.{decimal_2}.{decimal_3}.{decimal_4}"
print('O Broadcast 2 Decimal em Octetos é: ', (bcast2_decimal))
print("*" * 70)
