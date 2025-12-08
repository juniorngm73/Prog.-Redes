# fileserver_server.py
import socket
import os
import json
import struct
import glob
import hashlib # Necessário para a operação 40

HOST = '' 
PORT = 20000  # Alterado para 20000
BUFFER_SIZE = 1024 # Reduzido para o tamanho de bloco especificado (1024)
MAX_CONNECTIONS = 5 
FILE_ROOT = 'fileserver_root' # Pasta base para arquivos

# --- Funções Auxiliares ---

def safe_path(filename):
    """Garante que o caminho do arquivo está DENTRO do FILE_ROOT."""
    # Cria a pasta se não existir
    if not os.path.exists(FILE_ROOT):
        os.makedirs(FILE_ROOT)
        
    full_path = os.path.join(FILE_ROOT, filename)
    # Garante que o caminho canônico (sem ..) ainda está dentro do root.
    if not os.path.abspath(full_path).startswith(os.path.abspath(FILE_ROOT)):
        return None # Tentativa de escape
    return full_path

def recv_all(con, size):
    """Garante o recebimento do número exato de bytes."""
    data = b''
    while len(data) < size:
        chunk = con.recv(size - len(data))
        if not chunk:
            raise EOFError("Conexão encerrada prematuramente.")
        data += chunk
    return data

def handle_op_10_download(con, filename):
    """Lida com a operação de Download (Op: 10)."""
    full_path = safe_path(filename)
    
    if not full_path or not os.path.exists(full_path) or not os.path.isfile(full_path):
        print(f" Arquivo '{filename}' não encontrado ou acesso negado.")
        con.sendall(b'\x00') # Envia status 0
        return
        
    print(f" Arquivo '{filename}' encontrado. Iniciando envio.")
    con.sendall(b'\x01') # Envia status 1
    
    tam_arquivo = os.path.getsize(full_path)
    # 4 bytes (big endian) com o tamanho do arquivo
    tam_dados = struct.pack('>I', tam_arquivo)
    con.sendall(tam_dados)
    print(f" Tamanho do arquivo: {tam_arquivo} bytes.")
    
    # ENVIO DO CONTEÚDO DO ARQUIVO
    try:
        with open(full_path, 'rb') as f:
            bytes_enviados = 0
            while bytes_enviados < tam_arquivo:
                chunk = f.read(BUFFER_SIZE) 
                if not chunk: break
                con.sendall(chunk)
                bytes_enviados += len(chunk)
        
        print(f" Transferência de '{filename}' completa. Total de {bytes_enviados} bytes enviados.")
    except Exception as e:
        print(f" Erro ao enviar arquivo: {e}")


def handle_op_20_list(con):
    """Lida com a operação de Listagem (Op: 20)."""
    try:
        if not os.path.exists(FILE_ROOT):
            os.makedirs(FILE_ROOT)

        list_data = []
        for file_name in os.listdir(FILE_ROOT):
            full_path = os.path.join(FILE_ROOT, file_name)
            if os.path.isfile(full_path):
                list_data.append({
                    'nome': file_name,
                    'tamanho': str(os.path.getsize(full_path))
                })

        json_list = json.dumps(list_data).encode('utf-8')
        tam_json = len(json_list)

        con.sendall(b'\x01') # Status 1: Listagem será enviada
        # 4 bytes (big endian) com o tamanho do JSON
        con.sendall(struct.pack('>I', tam_json)) 
        con.sendall(json_list)
        print(f" Listagem enviada. {len(list_data)} arquivos listados.")
        
    except Exception as e:
        print(f" Erro ao listar arquivos: {e}")
        con.sendall(b'\x00') # Status 0: Erro

def handle_op_30_upload(con, filename):
    """Lida com a operação de Upload (Op: 30)."""
    full_path = safe_path(filename)
    
    if not full_path:
        print(f" Tentativa de acesso fora do root: {filename}. Upload negado.")
        con.sendall(b'\x00') # Status 0: Upload negado
        return
        
    try:
        con.sendall(b'\x01') # Status 1: Upload aceito, esperando tamanho e dados
        
        # 1. RECEBIMENTO DO TAMANHO DO ARQUIVO (4 bytes)
        tam_arquivo_dados = recv_all(con, 4)
        tam_arquivo = struct.unpack('>I', tam_arquivo_dados)[0]
        print(f" Tamanho do arquivo a receber: {tam_arquivo} bytes.")

        # 2. RECEBIMENTO DO CONTEÚDO DO ARQUIVO
        bytes_recebidos = 0
        with open(full_path, 'wb') as f:
            while bytes_recebidos < tam_arquivo:
                # Recebe o mínimo entre o BUFFER_SIZE e o que falta
                data = con.recv(min(BUFFER_SIZE, tam_arquivo - bytes_recebidos)) 
                if not data:
                    break # Conexão fechada
                f.write(data)
                bytes_recebidos += len(data)

        # 3. ENVIO DO STATUS FINAL
        if bytes_recebidos == tam_arquivo:
            print(f" Upload de '{filename}' completo. {bytes_recebidos} bytes salvos.")
            con.sendall(b'\x01') # Status 1: Sucesso
        else:
            print(f" Upload de '{filename}' incompleto. Recebido: {bytes_recebidos}/{tam_arquivo}.")
            con.sendall(b'\x00') # Status 0: Erro
            # Limpar arquivo incompleto (opcional)
            if os.path.exists(full_path):
                os.remove(full_path)

    except EOFError:
        print(f" Conexão perdida durante o upload de {filename}.")
        if os.path.exists(full_path): os.remove(full_path)
    except Exception as e:
        print(f" Erro no upload de {filename}: {e}")
        con.sendall(b'\x00') # Status 0: Erro


# --- Configuração e Loop Principal ---

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    server_socket.bind((HOST, PORT)) 
    server_socket.listen(MAX_CONNECTIONS) 
    print(f' 🚀 Servidor TCP escutando em {HOST}:{PORT}...')
except Exception as e:
    print(f" ❌ Erro ao iniciar o servidor: {e}")
    exit()

# Cria o diretório raiz se não existir
if not os.path.exists(FILE_ROOT):
    os.makedirs(FILE_ROOT)
    print(f" Diretório base '{FILE_ROOT}' criado.")

while True:
    con = None 
    try:
        # Define um timeout para o 'accept' (opcional, mas bom para interromper)
        server_socket.settimeout(5) 
        con, cliente = server_socket.accept() 
        print('\n\n-- Conectado por:', cliente)
        con.settimeout(10) # Timeout para operações de leitura/escrita
        
        # 1. RECEBIMENTO DO BYTE DE OPERAÇÃO
        op_data = recv_all(con, 1)
        op = struct.unpack('>B', op_data)[0]
        print(f" Código de operação recebido: {op}")

        if op == 10 or op == 30 or op == 40 or op == 50:
            # Operações que precisam do nome/máscara do arquivo
            # 2. RECEBIMENTO DO TAMANHO DO NOME/MÁSCARA (4 bytes)
            tam_nome_dados = recv_all(con, 4)
            tam_nome = struct.unpack('>I', tam_nome_dados)[0]
            print(f" Tamanho do nome/máscara a seguir: {tam_nome} bytes.")
            
            # 3. RECEBIMENTO DO NOME/MÁSCARA
            dados_nome = recv_all(con, tam_nome)
            nome_ou_mascara = dados_nome.decode('utf-8')
            print(f" Nome/Máscara recebida: '{nome_ou_mascara}'")

            if op == 10:
                handle_op_10_download(con, nome_ou_mascara)
            elif op == 30:
                handle_op_30_upload(con, nome_ou_mascara)
            elif op == 40:
                # Esta operação é mais complexa e precisaria de mais código para hash e offset
                # con.sendall(b'\x00') # Placeholder: Erro, não implementado
                print(" ❌ Operação 40 (Download Parcial) não implementada neste exemplo.")
            elif op == 50:
                # Esta operação é mais complexa e precisaria de uma proposta de protocolo
                # con.sendall(b'\x00') # Placeholder: Erro, não implementado
                print(" ❌ Operação 50 (Download Múltiplo) não implementada neste exemplo.")
        
        elif op == 20:
            handle_op_20_list(con)
        
        else:
            print(f" Operação desconhecida: {op}")

    except EOFError as e:
        print(f" Conexão com {cliente} perdida: {e}")
    except socket.timeout:
        print(" Timeout de conexão.")
    except Exception as e:
        print(f" Ocorreu um erro na comunicação com {cliente}: {e}")
    finally:
        if con:
            con.close() 
            print(f" Conexão com {cliente} encerrada.")