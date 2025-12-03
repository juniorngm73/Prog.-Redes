import socket
import struct
import sys
import os
import time

HOST = '127.0.0.1'
PORT = 65432
DOWNLOAD_DIR = 'downloads/'
TIMEOUT = 5.0 # Timeout para esperar a resposta
BUFFER_SIZE = 1024 + 10 # Buffer maior que o servidor para garantir cabeçalhos

print("--- Cliente UDP de Arquivos ---")

# Verifica se o argumento do nome do arquivo foi fornecido
if len(sys.argv) != 2:
    print("Uso: python client_file_udp.py <nome_do_arquivo>")
    sys.exit(1)

filename = sys.argv[1]

# 1. PREPARA O DATAGRAMA DE SOLICITAÇÃO
filename_bytes = filename.encode('utf-8')
filename_size = len(filename_bytes) 

# O datagrama de solicitação será: [1 byte: Tamanho] [Nome do Arquivo]
size_byte_to_send = struct.pack('>B', filename_size) 
request_datagram = size_byte_to_send + filename_bytes

try:
    # 2. Configuração e Envio
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(TIMEOUT) # Define um timeout para as operações de recebimento
    
    # Envia a solicitação
    client_socket.sendto(request_datagram, (HOST, PORT))
    print(f"[*] Solicitado arquivo: **{filename}**")

    # 3. RECEBE A CONFIRMAÇÃO DO SERVIDOR
    data, addr = client_socket.recvfrom(BUFFER_SIZE)
    
    status = data[:1].decode('utf-8')

    if status == '0': # Código '0' = Arquivo Encontrado
        print("[+] Servidor confirmou: Arquivo encontrado. Recebendo...")

        # O restante dos 8 bytes contém o tamanho total do arquivo
        size_file_bytes = data[1:9]
        file_size = struct.unpack('>Q', size_file_bytes)[0]
        print(f"[*] Tamanho total do arquivo a receber: {file_size} bytes")

        # 4. RECEBE O CONTEÚDO (em múltiplos datagramas)
        bytes_received = 0
        file_data = b''
        start_time = time.time()
        
        while bytes_received < file_size and (time.time() - start_time) < TIMEOUT:
            try:
                chunk, addr = client_socket.recvfrom(BUFFER_SIZE)
                file_data += chunk
                bytes_received += len(chunk)
            except socket.timeout:
                print("[-] Timeout na espera do próximo pedaço. Transferência incompleta.")
                break
        
        # 5. SALVA O ARQUIVO (se a contagem de bytes for próxima)
        if bytes_received >= file_size * 0.9: # Tolerância de 10% de perda
            os.makedirs(DOWNLOAD_DIR, exist_ok=True)
            download_path = os.path.join(DOWNLOAD_DIR, filename)
            with open(download_path, 'wb') as f:
                # Trunca (corta) os dados para o tamanho esperado, caso tenha recebido lixo a mais
                f.write(file_data[:file_size]) 
            
            loss_percent = (1 - (bytes_received / file_size)) * 100 if bytes_received < file_size else 0
            
            print(f"🎉 Arquivo recebido (teoricamente {bytes_received} bytes) e salvo em: **{download_path}**")
            
            if loss_percent > 0:
                print(f"⚠️ AVISO: {loss_percent:.2f}% dos dados originais foram perdidos.")
        else:
            print(f"[-] Erro: Recebido apenas {bytes_received} bytes. Falha na transferência UDP.")

    elif status == '1': # Código '1' = Arquivo Não Encontrado
        print(f"❌ Servidor informou: Arquivo '{filename}' não encontrado.")
        
    else:
        print(f"[-] Resposta desconhecida do servidor: {data}")

except socket.timeout:
    print("[-] Timeout: Nenhuma resposta inicial recebida do servidor.")
except Exception as e:
    print(f"[-] Ocorreu um erro: {e}")
finally:
    client_socket.close()