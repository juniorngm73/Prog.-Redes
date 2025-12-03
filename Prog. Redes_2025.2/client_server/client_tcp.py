import socket
import os
import time 

SERVER_IP = '127.0.0.1'
SERVER_PORT = 60000
BUFFER_SIZE = 4096

# 1. Criação do socket TCP (SOCK_STREAM)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # 2. Conexão ao servidor
    print(f"Tentando conectar a {SERVER_IP}:{SERVER_PORT}...")
    client_socket.connect((SERVER_IP, SERVER_PORT))
    print("Conexão estabelecida com sucesso.")

    nome_arquivo = input(" Digite o nome do arquivo que deseja baixar: ")
    nome_arquivob = nome_arquivo.encode('utf-8')

    # Calcula o tamanho do nome do arquivo
    tam_nome = 0
    for byte in nome_arquivob:
        tam_nome += 1

    if tam_nome > 255:
        print(" Erro: O nome do arquivo excede o limite (máximo 255 bytes).")
        client_socket.close()
        exit()

    # Prepara e envia o tamanho do nome (1 byte)
    tam_nome_dados = tam_nome.to_bytes(1, 'big')
    client_socket.sendall(tam_nome_dados)   # Usa sendall para garantir o envio total

    # Envia o nome do arquivo
    client_socket.sendall(nome_arquivob)    # Usa sendall para garantir o envio total

    print(f" Solicitado o arquivo: '{nome_arquivo}'")

    # --- RECEBIMENTO DO CABEÇALHO DE EXISTÊNCIA (1 BYTE) ---
    dados_resposta = b''
    bytes_a_receber = 1
    while len(dados_resposta) < bytes_a_receber:
        # Tenta receber o restante dos bytes
        chunk = client_socket.recv(bytes_a_receber - len(dados_resposta))
        if not chunk:
            raise Exception("Conexão encerrada prematuramente ao receber flag de existência.")
        dados_resposta += chunk

    arquivo_existe = dados_resposta[0]

    if arquivo_existe != 1:
        print(f" O arquivo '{nome_arquivo}' não existe no servidor ou houve erro.")
        client_socket.close()
        exit()

    # --- RECEBIMENTO DO TAMANHO TOTAL DO ARQUIVO (4 BYTES) ---
    tam_dados = b''
    bytes_a_receber = 4
    while len(tam_dados) < bytes_a_receber:
        # Tenta receber o restante dos bytes
        chunk = client_socket.recv(bytes_a_receber - len(tam_dados))
        if not chunk:
            raise Exception("Conexão encerrada prematuramente ao receber tamanho do arquivo.")
        tam_dados += chunk

    tam_arq = int.from_bytes(tam_dados, 'big')
    print(f" Arquivo existe. Tamanho total: {tam_arq} bytes.")

    # Recebe o conteúdo do arquivo
    local_arquivo = f"baixado_{nome_arquivo}"

    with open(local_arquivo, 'wb') as f:
        bytes_recebidos = 0
        while bytes_recebidos < tam_arq:
            # Em TCP, apenas chamamos recv(), sem precisar de recvfrom()
            chunk = client_socket.recv(BUFFER_SIZE)

            if not chunk:
                # Se o servidor fechar a conexão antes de terminar, é um erro
                raise Exception("Conexão perdida. Arquivo incompleto.")

            # Verifica se o chunk recebido excede o que falta (segurança)
            if bytes_recebidos + len(chunk) > tam_arq:
                chunk = chunk[:tam_arq - bytes_recebidos]

            f.write(chunk)
            bytes_recebidos += len(chunk)

            # Atraso para que a mensagem de progresso possa ser exibida
            print(f"  Recebido: {bytes_recebidos}/{tam_arq} bytes ({(bytes_recebidos / tam_arq) * 100:.2f}%)", end='\r')

    print(f"\n Transferência de '{nome_arquivo}' completa.")
    print(f" Arquivo salvo localmente como '{local_arquivo}'.")


except ConnectionRefusedError:
    print("\n Erro: Conexão recusada. O servidor não está ativo ou o IP/Porta está incorreto.")
except Exception as e:
    print(f"\n Ocorreu um erro no cliente: {e}")

finally:
    # Garante que o socket seja fechado
    if client_socket:
        client_socket.close()
        print("Conexão TCP encerrada.")