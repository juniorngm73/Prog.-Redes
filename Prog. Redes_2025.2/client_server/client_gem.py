# fileserver_client.py
import socket
import os
import sys
import struct
import json
import hashlib

HOST = '127.0.0.1' 
PORT = 20000 # Alterado para 20000
BUFFER_SIZE = 1024
FILE_ROOT_CLIENT = 'fileclient_downloads' # Pasta para salvar downloads

# --- Funções Auxiliares ---

def recv_all(sock, size):
    """Garante o recebimento do número exato de bytes."""
    data = b''
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            raise EOFError("Conexão encerrada prematuramente.")
        data += chunk
    return data

def connect_server():
    """Cria e conecta o socket TCP."""
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        tcp_socket.settimeout(10) # Timeout para conexão e operações
        tcp_socket.connect((HOST, PORT))
        print(f" ✅ Conectado ao servidor {HOST}:{PORT}.")
        return tcp_socket
    except ConnectionRefusedError:
        print(f" ❌ Erro: Conexão recusada. O servidor não está ativo em {HOST}:{PORT}.")
        sys.exit()
    except socket.timeout:
        print(f" ❌ Erro: Timeout ao tentar conectar em {HOST}:{PORT}.")
        sys.exit()
    except Exception as e:
        print(f" ❌ Ocorreu um erro na conexão: {e}")
        sys.exit()


# --- Implementação das Operações ---

def client_download(tcp_socket):
    """Implementa a Operação 10: Download de um arquivo."""
    nome_arquivo_str = input('Nome do arquivo para baixar: ')
    nome_arquivo_bytes = nome_arquivo_str.encode('utf-8')
    tam_nome = len(nome_arquivo_bytes)

    # ENVIO DA REQUISIÇÃO
    # 1. Operação (1 byte, valor 10)
    op_dados = struct.pack('>B', 10)
    # 2. Tamanho do nome (4 bytes, big endian)
    tam_nome_dados = struct.pack('>I', tam_nome)
    
    tcp_socket.sendall(op_dados + tam_nome_dados + nome_arquivo_bytes)
    print(f" Solicitando download: '{nome_arquivo_str}'")

    # RECEBIMENTO DA RESPOSTA
    status = struct.unpack('>B', recv_all(tcp_socket, 1))[0]
    
    if status == 0:
        print(" ❌ O servidor informou que o arquivo não foi encontrado.")
    elif status == 1:
        print(" ✅ Arquivo encontrado. Recebendo metadados...")
        
        # Recebimento do tamanho do arquivo (4 bytes)
        tam_arquivo = struct.unpack('>I', recv_all(tcp_socket, 4))[0]
        print(f" Tamanho total do arquivo a receber: {tam_arquivo} bytes.")

        # Recebimento do conteúdo do arquivo
        bytes_recebidos = 0
        if not os.path.exists(FILE_ROOT_CLIENT): os.makedirs(FILE_ROOT_CLIENT)
        save_path = os.path.join(FILE_ROOT_CLIENT, nome_arquivo_str)
        
        try:
            with open(save_path, 'wb') as f:
                while bytes_recebidos < tam_arquivo:
                    # Recebe o mínimo entre o BUFFER_SIZE e o que falta
                    data = tcp_socket.recv(min(BUFFER_SIZE, tam_arquivo - bytes_recebidos)) 
                    if not data:
                        break 
                    f.write(data)
                    bytes_recebidos += len(data)
            
            if bytes_recebidos == tam_arquivo:
                print(f" ⭐ Download de '{nome_arquivo_str}' completo. {bytes_recebidos} bytes salvos em '{save_path}'.")
            else:
                print(f" ⚠️ Download incompleto. Esperado: {tam_arquivo}, Recebido: {bytes_recebidos}. Arquivo salvo incompletamente.")
        except Exception as e:
            print(f" Erro ao salvar o arquivo: {e}")
            
    else:
        print(f" Status desconhecido recebido: {status}")


def client_list(tcp_socket):
    """Implementa a Operação 20: Listagem de arquivos."""
    # ENVIO DA REQUISIÇÃO
    # 1. Operação (1 byte, valor 20)
    op_dados = struct.pack('>B', 20)
    tcp_socket.sendall(op_dados)
    print(" Solicitando listagem de arquivos...")

    # RECEBIMENTO DA RESPOSTA
    status = struct.unpack('>B', recv_all(tcp_socket, 1))[0]

    if status == 0:
        print(" ❌ Erro não identificado na listagem pelo servidor.")
    elif status == 1:
        # Recebimento do tamanho do JSON (4 bytes)
        tam_json = struct.unpack('>I', recv_all(tcp_socket, 4))[0]
        print(f" Tamanho da listagem a receber: {tam_json} bytes.")
        
        # Recebimento do JSON
        json_data = recv_all(tcp_socket, tam_json)
        list_data = json.loads(json_data.decode('utf-8'))
        
        print("\n--- Arquivos Disponíveis no Servidor ---")
        if not list_data:
            print(" 📂 Nenhuma arquivo encontrado.")
        else:
            for item in list_data:
                print(f" - {item['nome']} (Tamanho: {item['tamanho']} bytes)")
        print("----------------------------------------")
    else:
        print(f" Status desconhecido recebido: {status}")


def client_upload(tcp_socket):
    """Implementa a Operação 30: Upload de um arquivo."""
    nome_arquivo_str = input('Nome do arquivo para enviar: ')
    full_path = os.path.join(os.getcwd(), nome_arquivo_str) # Assume que o arquivo está na pasta atual

    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        print(f" ❌ Arquivo local '{nome_arquivo_str}' não encontrado.")
        return

    nome_arquivo_bytes = nome_arquivo_str.encode('utf-8')
    tam_nome = len(nome_arquivo_bytes)
    tam_arquivo = os.path.getsize(full_path)

    # ENVIO DA REQUISIÇÃO INICIAL
    # 1. Operação (1 byte, valor 30)
    op_dados = struct.pack('>B', 30)
    # 2. Tamanho do nome (4 bytes, big endian)
    tam_nome_dados = struct.pack('>I', tam_nome)
    
    tcp_socket.sendall(op_dados + tam_nome_dados + nome_arquivo_bytes)
    print(f" Solicitando upload de: '{nome_arquivo_str}' ({tam_arquivo} bytes)")

    # RECEBIMENTO DO STATUS DE ACEITE (1 byte)
    status_aceite = struct.unpack('>B', recv_all(tcp_socket, 1))[0]

    if status_aceite == 0:
        print(" ❌ O servidor não aceitou o upload (erro ou acesso negado).")
        return

    if status_aceite == 1:
        # 1. ENVIO DO TAMANHO DO ARQUIVO (4 bytes)
        tam_dados = struct.pack('>I', tam_arquivo)
        tcp_socket.sendall(tam_dados)
        
        # 2. ENVIO DO CONTEÚDO DO ARQUIVO
        bytes_enviados = 0
        try:
            with open(full_path, 'rb') as f:
                while bytes_enviados < tam_arquivo:
                    chunk = f.read(BUFFER_SIZE) 
                    if not chunk: break
                    tcp_socket.sendall(chunk)
                    bytes_enviados += len(chunk)
            print(f" Conteúdo enviado. Total de {bytes_enviados} bytes.")

            # 3. RECEBIMENTO DO STATUS FINAL (1 byte)
            status_final = struct.unpack('>B', recv_all(tcp_socket, 1))[0]
            
            if status_final == 1:
                print(f" ⭐ Upload de '{nome_arquivo_str}' concluído com sucesso!")
            else:
                print(" ❌ Erro no servidor durante o salvamento do arquivo.")

        except Exception as e:
            print(f" Erro durante o envio dos dados: {e}")


# --- Loop Principal do Cliente ---

def main_menu():
    """Exibe o menu e lida com a seleção de operações."""
    while True:
        print("\n--- Menu do Cliente Fileserver ---")
        print(" 1. Download de Arquivo (Op 10)")
        print(" 2. Listar Arquivos (Op 20)")
        print(" 3. Upload de Arquivo (Op 30)")
        print(" 4. Sair")
        
        try:
            choice = input("Escolha uma opção: ")
            if choice == '4':
                print("Encerrando cliente.")
                break
            
            tcp_socket = connect_server()
            
            if choice == '1':
                client_download(tcp_socket)
            elif choice == '2':
                client_list(tcp_socket)
            elif choice == '3':
                client_upload(tcp_socket)
            else:
                print("Opção inválida.")
                
        except Exception as e:
            print(f"\n Ocorreu um erro na operação: {e}")
        finally:
            if 'tcp_socket' in locals() and tcp_socket.fileno() != -1:
                tcp_socket.close()
                print(" Conexão encerrada.")

if __name__ == '__main__':
    # Cria a pasta de downloads no cliente se não existir
    if not os.path.exists(FILE_ROOT_CLIENT):
        os.makedirs(FILE_ROOT_CLIENT)
    main_menu()