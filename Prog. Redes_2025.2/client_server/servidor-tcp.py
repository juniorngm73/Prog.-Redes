import socket
import os

HOST = '' 
PORT = 60000
BUFFER_SIZE = 4096
MAX_CONNECTIONS = 5 

# CORREÇÃO: Usar SOCK_STREAM para TCP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    server_socket.bind((HOST, PORT)) 
    # ADIÇÃO: O TCP precisa 'escutar' (listen)
    server_socket.listen(MAX_CONNECTIONS) 
    print(f' Servidor TCP escutando em {HOST}:{PORT}...')
except Exception as e:
    print(f" Erro ao iniciar o servidor: {e}")
    exit()

while True:
    con = None 
    try:
        # ADIÇÃO: Aceitar a conexão. 'con' é o socket de comunicação
        con, cliente = server_socket.accept() 
        print('\n\n-- Conectado por:', cliente)

        # 1. RECEBIMENTO DO TAMANHO DO NOME (1 byte)
        tam_nome_dados = b''
        while len(tam_nome_dados) < 1:
            chunk = con.recv(1 - len(tam_nome_dados))
            if not chunk:
                raise EOFError("Conexão encerrada prematuramente ao ler o tamanho do nome.")
            tam_nome_dados += chunk
            
        tam_nome = int.from_bytes(tam_nome_dados, 'big')
        print(f" Tamanho do nome do arquivo recebido: {tam_nome} bytes.")
        
        # 2. RECEBIMENTO DO NOME DO ARQUIVO
        dados_nome = b''
        while len(dados_nome) < tam_nome:
            chunk = con.recv(tam_nome - len(dados_nome))
            if not chunk:
                raise EOFError("Conexão encerrada prematuramente ao ler o nome do arquivo.")
            dados_nome += chunk

        nome_arquivo = dados_nome.decode('utf-8')
        print(f" Nome do arquivo solicitado: '{nome_arquivo}'")

        # 3. VERIFICAÇÃO E RESPOSTA
        if not os.path.exists(nome_arquivo) or not os.path.isfile(nome_arquivo):
            print(f" Arquivo '{nome_arquivo}' não encontrado.")
            con.send(b'\x00') # Envia status 0
        else:
            print(f" Arquivo '{nome_arquivo}' encontrado. Iniciando envio.")
            con.send(b'\x01') # Envia status 1
            tam_arquivo = os.path.getsize(nome_arquivo)
            
            # 4. ENVIO DO TAMANHO DO ARQUIVO (4 bytes)
            tam_dados = tam_arquivo.to_bytes(4, 'big')
            con.send(tam_dados)
            print(f" Tamanho do arquivo: {tam_arquivo} bytes.")
            
            # 5. ENVIO DO CONTEÚDO DO ARQUIVO
            with open(nome_arquivo, 'rb') as f:
                bytes_enviados = 0
                while bytes_enviados < tam_arquivo:
                    chunk = f.read(BUFFER_SIZE) 
                    con.send(chunk)
                    bytes_enviados += len(chunk)
            
            print(f" Transferência de '{nome_arquivo}' completa. Total de {bytes_enviados} bytes enviados.")

    except EOFError as e:
        print(f" Conexão com {cliente} perdida: {e}")
    except Exception as e:
        print(f" Ocorreu um erro na comunicação com {cliente}: {e}")
    finally:
        # FECHAMENTO OBRIGATÓRIO NO TCP
        if con:
            con.close() 
            print(f" Conexão com {cliente} encerrada.")