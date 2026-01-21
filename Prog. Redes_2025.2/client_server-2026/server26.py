import socket, os, json, sys, threading, hashlib, fnmatch

# Configurações iniciais
if len(sys.argv) != 2:
    print("Uso correto: python servidor.py <porta>")
    sys.exit(1)

PORT = int(sys.argv[1])
BUFFER_SIZE = 4096
BASE_DIR = os.path.abspath("server_files")

if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

def get_all_ips():
    """Busca todos os endereços IP das interfaces de rede locais."""
    ips = []
    try:
        hostname = socket.gethostname()
        for info in socket.getaddrinfo(hostname, None, socket.AF_INET):
            ip = info[4][0]
            if ip not in ips:
                ips.append(ip)
    except Exception:
        pass
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        real_ip = s.getsockname()[0]
        if real_ip not in ips:
            ips.append(real_ip)
        s.close()
    except Exception:
        pass

    if "127.0.0.1" not in ips:
        ips.append("127.0.0.1")
    return sorted(ips)

def get_md5(file_path, limit):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        bytes_read = 0
        while bytes_read < limit:
            chunk = f.read(min(4096, limit - bytes_read))
            if not chunk: break
            hash_md5.update(chunk)
            bytes_read += len(chunk)
    return hash_md5.digest()

def safe_path(filename):
    path = os.path.normpath(os.path.join(BASE_DIR, filename))
    if os.path.commonpath([BASE_DIR, os.path.abspath(path)]) == BASE_DIR:
        return path
    return None

def handle_client(con, cliente):
    print(f"[*] Nova conexão estabelecida com {cliente}")
    try:
        while True:
            op_byte = con.recv(1)
            if not op_byte: break 
            
            operacao = int.from_bytes(op_byte, 'big')
            print(f"[>] Cliente {cliente} solicitou operação {operacao}")

            if operacao == 10: # DOWNLOAD
                tam_nome = int.from_bytes(con.recv(4), 'big')
                nome_arquivo = con.recv(tam_nome).decode('utf-8')
                path = safe_path(nome_arquivo)
                if path and os.path.exists(path):
                    con.send(b'\x00') 
                    tam_arq = os.path.getsize(path)
                    con.send(tam_arq.to_bytes(4, 'big'))
                    with open(path, 'rb') as f:
                        while (chunk := f.read(BUFFER_SIZE)):
                            con.sendall(chunk)
                else:
                    con.send(b'\x01')

            elif operacao == 20: # LISTAR
                arquivos_info = []
                for f in os.listdir(BASE_DIR):
                    p = os.path.join(BASE_DIR, f)
                    if os.path.isfile(p):
                        arquivos_info.append({"nome": f, "tamanho": os.path.getsize(p)})
                json_bytes = json.dumps(arquivos_info).encode('utf-8')
                con.send(b'\x00')
                con.send(len(json_bytes).to_bytes(4, 'big'))
                con.sendall(json_bytes)

            elif operacao == 30: # UPLOAD
                tam_nome = int.from_bytes(con.recv(4), 'big')
                nome_arquivo = con.recv(tam_nome).decode('utf-8')
                path = safe_path(nome_arquivo)
                con.send(b'\x00')
                tam_arq = int.from_bytes(con.recv(4), 'big')
                recebido = 0
                with open(path, 'wb') as f:
                    while recebido < tam_arq:
                        chunk = con.recv(min(BUFFER_SIZE, tam_arq - recebido))
                        if not chunk: break
                        f.write(chunk)
                        recebido += len(chunk)
                con.send(b'\x00' if recebido == tam_arq else b'\x01')

            elif operacao == 40: # RESUME
                tam_nome = int.from_bytes(con.recv(4), 'big')
                nome_arquivo = con.recv(tam_nome).decode('utf-8')
                posicao = int.from_bytes(con.recv(4), 'big')
                hash_cliente = con.recv(16)
                path = safe_path(nome_arquivo)
                if not path or not os.path.exists(path):
                    con.send(b'\x01')
                    con.send(b'\x0a')
                elif posicao > 0 and get_md5(path, posicao) != hash_cliente:
                    con.send(b'\x00')
                    con.send(b'\x14')
                else:
                    con.send(b'\x00')
                    con.send(b'\x00')
                    tam_rem = os.path.getsize(path) - posicao
                    con.send(tam_rem.to_bytes(4, 'big'))
                    with open(path, 'rb') as f:
                        f.seek(posicao)
                        while (chunk := f.read(BUFFER_SIZE)):
                            con.sendall(chunk)

            elif operacao == 50: # MASK
                tam_mask = int.from_bytes(con.recv(4), 'big')
                mascara = con.recv(tam_mask).decode('utf-8')
                arquivos = [f for f in os.listdir(BASE_DIR) if fnmatch.fnmatch(f, mascara)]
                lista_json = json.dumps(arquivos).encode('utf-8')
                con.send(len(lista_json).to_bytes(4, 'big'))
                con.sendall(lista_json)
                for nome in arquivos:
                    path = os.path.join(BASE_DIR, nome)
                    tam = os.path.getsize(path)
                    con.send(tam.to_bytes(4, 'big'))
                    with open(path, 'rb') as f:
                        while (chunk := f.read(BUFFER_SIZE)):
                            con.sendall(chunk)

    except Exception as e:
        print(f"[!] Erro no atendimento a {cliente}: {e}")
    finally:
        con.close()
        print(f"[*] Conexão encerrada com {cliente}.")

def main():
    # Criação do socket TCP/IP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Permite reiniciar o servidor imediatamente sem erro de 'Address already in use'
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        # Faz o bind em todas as interfaces disponíveis (0.0.0.0)
        server_socket.bind(("0.0.0.0", PORT))
        server_socket.listen(5)
        
        # Mostra informações de rede para o usuário
        lista_ips = get_all_ips()
        print("="*50)
        print("SERVIDOR DE ARQUIVOS INICIADO")
        print(f"Porta: {PORT}")
        print(f"IPs para conexão: {', '.join(lista_ips)}")
        print(f"Diretório base: {BASE_DIR}")
        print("="*50)

        while True:
            # Aguarda nova conexão
            con, cliente = server_socket.accept()
            # Cria uma nova thread para gerenciar o cliente
            client_thread = threading.Thread(target=handle_client, args=(con, cliente))
            client_thread.daemon = True
            client_thread.start()

    except Exception as e:
        print(f"[!] Erro fatal no servidor: {e}")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()