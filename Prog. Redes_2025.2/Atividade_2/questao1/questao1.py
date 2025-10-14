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

if net1 == net2:
    print ("Mesma Rede!!!")
else:
    print ("Redes Diferentes!!!")