import socket
import os
import time # Adicionado para debug

HOST = '127.0.0.1' # Usamos 127.0.0.1 ou o IP do seu servidor
PORT = 60000
BUFFER_SIZE = 4096

# 1. Criação do socket TCP (SOCK_STREAM)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Configurações para reutilizar o endereço imediatamente (útil para testes)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # 2. Bind do socket
    server_socket.bind((HOST, PORT))
    
    # 3. Escuta por conexões de entrada
    server_socket.listen(1) 
    print(f" Servidor TCP escutando em {HOST}:{PORT}. Aguardando conexões...")

except Exception as e:
    print(f" Erro ao iniciar o servidor: {e}")
    exit() 

while True:
    # 4. Aceita uma nova conexão
    conn = None
    try:
        # A thread principal bloqueia aqui até que um cliente se conecte
        conn, addr = server_socket.accept()
        print(f"\n\n-- Nova solicitação aceita de {addr} --")

        # --- RECEBIMENTO DO TAMANHO DO NOME (1 BYTE) ---
        tam_nome_dados = b''
        bytes_a_receber = 1
        while len(tam_nome_dados) < bytes_a_receber:
            chunk = conn.recv(bytes_a_receber - len(tam_nome_dados))
            if not chunk:
                raise Exception("Conexão encerrada pelo cliente ao receber tamanho do nome.")
            tam_nome_dados += chunk
            
        tam_nome = int.from_bytes(tam_nome_dados, 'big')
        print(f" Tamanho do nome do arquivo recebido: {tam_nome} bytes.")
        
        # --- RECEBIMENTO DO NOME DO ARQUIVO ---
        dados_nome = b''
        bytes_a_receber = tam_nome
        while len(dados_nome) < bytes_a_receber:
            chunk = conn.recv(bytes_a_receber - len(dados_nome))
            if not chunk:
                raise Exception("Conexão encerrada pelo cliente ao receber nome do arquivo.")
            dados_nome += chunk
            
        nome_arquivo = dados_nome.decode('utf-8')
        print(f" Nome do arquivo recebido: '{nome_arquivo}'")

        if not os.path.exists(nome_arquivo) or not os.path.isfile(nome_arquivo):
            # Arquivo não existe: Envia 0
            print(f" Arquivo '{nome_arquivo}' não encontrado.")
            conn.sendall(b'\x00') # Usa sendall
        else:
            # Arquivo existe: Envia 1
            print(f" Arquivo '{nome_arquivo}' encontrado. Iniciando envio.")
            conn.sendall(b'\x01') # Usa sendall
            
            tam_arquivo = os.path.getsize(nome_arquivo)
            
            # Envia o tamanho do arquivo (4 bytes, big-endian)
            tam_dados = tam_arquivo.to_bytes(4, 'big')
            conn.sendall(tam_dados)
            
            # Envia o conteúdo do arquivo
            with open(nome_arquivo, 'rb') as f:
                bytes_enviados = 0
                while bytes_enviados < tam_arquivo:
                    chunk = f.read(BUFFER_SIZE) 
                    if not chunk:
                        break # Fim do arquivo
                        
                    conn.sendall(chunk) # Usa sendall
                    bytes_enviados += len(chunk)
                    print(f"  Enviado: {bytes_enviados}/{tam_arquivo} bytes ({(bytes_enviados / tam_arquivo) * 100:.2f}%)", end='\r')
            
            print(f"\n Transferência de '{nome_arquivo}' completa. Total de {bytes_enviados} bytes enviados.")

    except Exception as e:
        print(f" Ocorreu um erro no servidor durante o atendimento ao cliente: {e}")
        
    finally:
        # 5. Fecha a conexão com o cliente atual
        if conn:
            conn.close()
            print(" Conexão TCP com o cliente encerrada.")