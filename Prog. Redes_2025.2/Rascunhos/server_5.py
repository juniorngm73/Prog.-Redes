import socket

HOST = '127.0.0.1' # Definindo o IP do servidor
PORT = 50000 # Definindo a porta do servidor


# Criando o socket UDP (correto)
socketServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Ligando o servidor ao IP e porta que será "escutado"
socketServer.bind((HOST, PORT))


print('\nServidor UDP aguardando mensagens...\nPressione Ctrl+C para interromper...\n')

while True:
         # 1. Aceitando/Recebendo mensagem do cliente. 'cliente' armazena o endereço de retorno.
        msg, cliente = socketServer.recvfrom(1024)
        print(f'Mensagem recebida de {cliente}: {msg.decode("utf-8")}')
        
        # 2. ENVIANDO A MENSAGEM DE VOLTA (ECO)
        # Usamos o endereço 'cliente' que recebemos em recvfrom
        socketServer.sendto(msg, cliente) 
        print(f'Eco enviado para {cliente}')

# Fechando o socket (Esta linha só será alcançada se houver uma exceção, como Ctrl+C)
# **Observação**: Seu código original tinha 'SocketServer.close()' com 'S' maiúsculo. 
# Deve ser 'socketServer.close()'.
socketServer.close()