

# --------------------------------------------------
# Documentação Protocolo HTTP
#
# https://datatracker.ietf.org/doc/html/rfc2616
# https://developer.mozilla.org/pt-BR/docs/Web/HTTP/Overview
# https://www.ibm.com/docs/pt-br/power10/7063-CR2?topic=apis-http-protocol
# --------------------------------------------------
import socket, sys
from collections import defaultdict

# --------------------------------------------------
PORT        = 80
CODE_PAGE   = 'utf-8'
BUFFER_SIZE = 1024
# --------------------------------------------------

host = input('\nInforme o nome do HOST ou URL do site: ')

tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    tcp_socket.connect((host, PORT))
except:
    print(f'\nERRO.... {sys.exc_info()[0]}')
else:
    requisicao = f'HEAD / HTTP/1.1\r\nHost: {host}\r\nAccept: text/html\r\n\r\n'
    try:
        tcp_socket.sendall(requisicao.encode(CODE_PAGE))
    except:
        print(f'\nERRO.... {sys.exc_info()[0]}')
    else:
        resposta = tcp_socket.recv(BUFFER_SIZE).decode(CODE_PAGE)

        # Criando um dicionário  para armazenar os cabeçalhos
        headers = defaultdict(list)

        # Separando a resposta em linhas e iterar sobre cada linha
        for line in resposta.splitlines():
            # Verificando se a linha contém um cabeçalho (chave:valor)
            if ':' in line:
                key, value = line.split(':', 1)
                headers[key.strip()].append(value.strip())

        print('-' * 50)

        for chave, valor in headers.items():
                print(f'A chave {chave} tem o valor {valor}.')

        print('-' * 50)

    tcp_socket.close()





