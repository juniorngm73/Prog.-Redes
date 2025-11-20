import socket

HOST = 'localhost' # Definindo o IP do servidor
PORT = 50000 # Definindo a porta do servidor


# Criando o socket UDP
socketServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Ligando o servidor ao IP e porta
socketServer.bind((HOST, PORT))


print('\nServidor UDP aguardando mensagens...\n')

while True:
    # 1. RECEBENDO: 
    # 'msg' guarda os dados (bytes)
    # 'cliente' guarda o endereço (IP, Porta) de quem enviou
    msg, cliente = socketServer.recvfrom(1024)
    
    # Decodificando a mensagem para imprimir
    print(f'Mensagem recebida de {cliente}: {msg.decode("utf-8")}')
    
    # 2. RESPONDENDO (ECO):
    # Envia a mesma 'msg' de volta para o endereço 'cliente' de onde ela veio.
    socketServer.sendto(msg, cliente) 
    
    print(f'Eco enviado de volta para {cliente}')

# Fechando o socket (Executado apenas ao interromper com Ctrl+C)
socketServer.close()