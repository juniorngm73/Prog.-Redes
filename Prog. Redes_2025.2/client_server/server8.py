import socket
import os

HOST = ''
PORT = 60000
BUFFER_SIZE = 4096

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    server_socket.bind((HOST, PORT))
    print(f" Servidor escutando em {HOST}:{PORT}...")
except Exception as e:
    print(f" Erro ao iniciar o servidor: {e}")
    exit() 

while True:
    try:
        
        print("\n\n-- Aguardando nova solicitação --")
        tam_nome_dados, end_cliente = server_socket.recvfrom(1)    # Recebe o tamanho do nome do arquivo (1 byte)     
        tam_nome = int.from_bytes(tam_nome_dados, 'big')           # Converte o tamanho do nome
        print(f" Tamanho do nome do arquivo recebido: {tam_nome} bytes.")
         
        dados_nome, _ = server_socket.recvfrom(BUFFER_SIZE) 
        dados_nome = dados_nome[:tam_nome]
        nome_arquivo = dados_nome.decode('utf-8')
        
        print(f" Nome do arquivo recebido: '{nome_arquivo}' de {end_cliente}")

        if not os.path.exists(nome_arquivo) or not os.path.isfile(nome_arquivo):
            # Arquivo não existe: Envia 0
            print(f" Arquivo '{nome_arquivo}' não encontrado.")
            server_socket.sendto(b'\x00', end_cliente)
        else:
            # Arquivo existe: Envia 1
            print(f" Arquivo '{nome_arquivo}' encontrado. Iniciando envio.")
            server_socket.sendto(b'\x01', end_cliente) 
            tam_arquivo = os.path.getsize(nome_arquivo)
            
            # Envia o tamanho do arquivo (4 bytes, big-endian)
            tam_dados = tam_arquivo.to_bytes(4, 'big')
            server_socket.sendto(tam_dados, end_cliente)
            print(tam_dados)
            # Envia o conteúdo do arquivo
            with open(nome_arquivo, 'rb') as f:
                bytes_enviados = 0
                while bytes_enviados < tam_arquivo:
                    chunk = f.read(BUFFER_SIZE) 
                    server_socket.sendto(chunk, end_cliente)
                    bytes_enviados += len(chunk)
            
            print(f" Transferência de '{nome_arquivo}' completa. Total de {bytes_enviados} bytes enviados.")

    except Exception as e:
        print(f" Ocorreu um erro no servidor: {e}")
        
server_socket.close()