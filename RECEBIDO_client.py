import socket

HOST = 'localhost' # Definindo o IP do servidor
PORT = 50000 # Definindo a porta do servidor


# Criando o socket UDP (correto)
socketCliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:

    msg = input('Digite sua mensagem (!q para sair): ') 
    if (msg == "!q"): break

 # 1. Enviando a mensagem
    msgb = msg.encode('utf-8')
    socketCliente.sendto(msgb, (HOST, PORT))
# 2. RECEBENDO A RESPOSTA (ECO) DO SERVIDOR
    
    dados_recebidos, servidor = socketCliente.recvfrom(1024)
    print(f'Resposta do Servidor ({servidor}): {dados_recebidos.decode("utf-8")}')

# Fechando Conexão com o Servidor
socketCliente.close()