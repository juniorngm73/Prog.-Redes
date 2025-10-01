import socket, sys

# ----------------------------------------------------------------------
PORT        = 80
BUFFER_SIZE = 2048  #  Capacidade de armazenamento de dados em um buffer(Alocação Memória).
# ----------------------------------------------------------------------


host = 'www.globo.com'
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.settimeout(10)

try:
    tcp_socket.connect((host, PORT))
except:
    print(f'\nERRO.... {sys.exc_info()[0]}')
else:
    requisicao = f'GET / HTTP/1.1\r\nHost: {host}\r\nAccept: text/html\r\n\r\n'
    try:
        tcp_socket.sendall(requisicao.encode('ISO-8859-1'))
    except:
        print(f'\nERRO.... {sys.exc_info()[0]}')
    else:


        while True:
            output = tcp_socket.recv(BUFFER_SIZE)

            if not output:
                    break

            with open('output.html ', 'wb') as file:
                file.write(output)

tcp_socket.close()

