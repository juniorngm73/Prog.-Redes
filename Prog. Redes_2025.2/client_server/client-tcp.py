# Importando a biblioteca socket
import socket
import os
import sys

HOST = '127.0.0.1' # IP do servidor
PORT = 60000 # Porta
BUFFER_SIZE = 4096

# CORREÇÃO: SOCK_STREAM para TCP
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    tcp_socket.connect((HOST, PORT)) # Conecta ao servidor
    print(f" Conectado ao servidor {HOST}:{PORT}.")

    # 1. SOLICITAÇÃO DO NOME DO ARQUIVO
    nome_arquivo_str = input('Digite o nome do arquivo para baixar: ')
    nome_arquivo_bytes = nome_arquivo_str.encode('utf-8')
    tam_nome = len(nome_arquivo_bytes)

    if tam_nome > 255:
        print("Nome do arquivo muito longo. Máximo de 255 bytes.")
        sys.exit()

    # 2. ENVIO DO TAMANHO DO NOME (1 byte)
    tam_nome_dados = tam_nome.to_bytes(1, 'big')
    tcp_socket.send(tam_nome_dados)
    
    # 3. ENVIO DO NOME DO ARQUIVO
    tcp_socket.send(nome_arquivo_bytes)
    print(f" Solicitando arquivo: '{nome_arquivo_str}'")

    # 4. RECEBIMENTO DO STATUS (1 byte)
    status_dados = b''
    # Garante a leitura de 1 byte
    while len(status_dados) < 1:
        chunk = tcp_socket.recv(1 - len(status_dados))
        if not chunk:
            raise EOFError("Conexão encerrada antes de receber o status.")
        status_dados += chunk
        
    status = int.from_bytes(status_dados, 'big')
    
    if status == 0:
        print(" ❌ O servidor informou que o arquivo não foi encontrado.")
    elif status == 1:
        print(" ✅ Arquivo encontrado. Recebendo metadados...")
        
        # 5. RECEBIMENTO DO TAMANHO DO ARQUIVO (4 bytes)
        tam_arquivo_dados = b''
        # Garante a leitura de 4 bytes
        while len(tam_arquivo_dados) < 4:
            chunk = tcp_socket.recv(4 - len(tam_arquivo_dados))
            if not chunk:
                 raise EOFError("Conexão encerrada antes de receber o tamanho do arquivo.")
            tam_arquivo_dados += chunk
            
        tam_arquivo = int.from_bytes(tam_arquivo_dados, 'big')
        print(f" Tamanho total do arquivo a receber: {tam_arquivo} bytes.")

        # 6. RECEBIMENTO DO CONTEÚDO DO ARQUIVO
        bytes_recebidos = 0
        with open("RECEBIDO_" + nome_arquivo_str, 'wb') as f:
            while bytes_recebidos < tam_arquivo:
                # O TCP garantirá que não recebemos mais do que falta
                data = tcp_socket.recv(min(BUFFER_SIZE, tam_arquivo - bytes_recebidos)) 
                if not data:
                    break # Conexão fechada
                f.write(data)
                bytes_recebidos += len(data)
        
        if bytes_recebidos == tam_arquivo:
            print(f" ⭐ Download de '{nome_arquivo_str}' completo. Total de {bytes_recebidos} bytes salvos.")
        else:
            print(f" ⚠️ Download incompleto. Esperado: {tam_arquivo}, Recebido: {bytes_recebidos}.")
        
    else:
        print(f" Status desconhecido recebido: {status}")

except ConnectionRefusedError:
    print(f" Erro: Conexão recusada. Certifique-se de que o servidor está em execução em {HOST}:{PORT}.")
except EOFError as e:
    print(f" Erro de protocolo/conexão: {e}")
except Exception as e:
    print(f" Ocorreu um erro: {e}")
finally:
    # Fechando o socket
    tcp_socket.close()
    print(" Conexão encerrada.")