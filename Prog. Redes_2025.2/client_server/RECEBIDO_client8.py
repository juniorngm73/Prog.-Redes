import socket
import os

SERVER_IP = '127.0.0.1'
SERVER_PORT = 60000
BUFFER_SIZE = 4096

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    nome_arquivo = input(" Digite o nome do arquivo que deseja baixar: ")     
    nome_arquivob = nome_arquivo.encode('utf-8')                              #  Prepara e envia o tamanho do nome (1 byte)
    
    tam_nome = 0
    for byte in nome_arquivob:
        tam_nome += 1
    
    if tam_nome > 255:
        print(" Erro: O nome do arquivo excede numero de bytes (máximo 255 bytes).")
        client_socket.close() 
        exit()

    tam_nome_dados = tam_nome.to_bytes(1, 'big')
    client_socket.sendto(tam_nome_dados, (SERVER_IP, SERVER_PORT))    #  Envia o Tamanho do nome do arquivo.
    client_socket.sendto(nome_arquivob, (SERVER_IP, SERVER_PORT))     #  Envia o nome do arquivo
    
    print(f" Solicitado o arquivo: '{nome_arquivo}'")

    dados_resposta, _ = client_socket.recvfrom(1)                     # Recebe a resposta do servidor: existência (1 byte)
    arquivo_existe = dados_resposta[0]
    
    if arquivo_existe != 1:
        print(f" O arquivo '{nome_arquivo}' não existe no servidor ou houve erro.")
        client_socket.close() 
        exit()

    tam_dados, _ = client_socket.recvfrom(4)     # Recebe o tamanho total (4 bytes, big-endian)
    tam_arq = int.from_bytes(tam_dados, 'big')
    print(f" Arquivo existe. Tamanho total: {tam_arq} bytes.")
    
    
    local_arquivo = f"baixado_{nome_arquivo}"   # Recebe o conteúdo do arquivo
    
    with open(local_arquivo, 'wb') as f:
        bytes_recebidos = 0
        while bytes_recebidos < tam_arq:
            bytes_left = tam_arq - bytes_recebidos 
            chunk, _ = client_socket.recvfrom(BUFFER_SIZE) 
            
            if bytes_recebidos + len(chunk) > tam_arq:
                chunk = chunk[:tam_arq - bytes_recebidos]
            
            f.write(chunk)
            bytes_recebidos += len(chunk)
            
            print(f"  Recebido: {bytes_recebidos}/{tam_arq} bytes ({(bytes_recebidos / tam_arq) * 100:.2f}%)", end='\r')

    print(f"\n Transferência de '{nome_arquivo}' completa.")
    print(f" Arquivo salvo localmente como '{local_arquivo}'.")


except Exception as e:
    print(f"\n Ocorreu um erro no cliente: {e}")
    
client_socket.close()