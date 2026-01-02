import socket, os, json, sys, threading

if len(sys.argv) != 2:
    print("Uso correto: python servidor.py <porta>")
    sys.exit(1)

HOST = ''
PORT = int(sys.argv[1])
BUFFER_SIZE = 4096

# --- INFORMAÇÕES DE REDE ---
hostname = socket.gethostname()
ips_disponiveis = socket.gethostbyname_ex(hostname)[2]

print("-" * 50)
print(f" SERVIDOR MULTI-THREAD")
print(f" Porta: {PORT}")
print(" IPs disponíveis para conexão:")
for ip in ips_disponiveis:
    print(f"   > {ip}")
print("-" * 50)

# --- CONFIGURAÇÃO DO SOCKET ---
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(10)

def get_lista_arquivos_json():
    arquivos_info = []
    for f in os.listdir('.'):
        if os.path.isfile(f) and not f.endswith('.py'):
            tamanho = os.path.getsize(f)
            arquivos_info.append({"nome": f, "tamanho_bytes": tamanho})
    return json.dumps(arquivos_info, indent=4)

def tratar_cliente(con, cliente):
    try:
        print(f'\n[CONEXÃO] {cliente} conectado.')
        op_byte = con.recv(1)
        if not op_byte: return
        operacao = int.from_bytes(op_byte, 'big')

        # OPÇÃO 1: DOWNLOAD
        if operacao == 10:
            tam_nome = int.from_bytes(con.recv(4), 'big')
            nome_arquivo = con.recv(tam_nome).decode('utf-8')
            if os.path.exists(nome_arquivo):
                tam_arquivo = os.path.getsize(nome_arquivo)
                con.send(b'\x00') 
                con.send(tam_arquivo.to_bytes(4, 'big'))
                with open(nome_arquivo, 'rb') as f:
                    while (chunk := f.read(BUFFER_SIZE)):
                        con.sendall(chunk)
                print(f" [DOWNLOAD] '{nome_arquivo}' enviado para {cliente}")
            else:
                con.send(b'\x01')

        # OPÇÃO 2: LISTAGEM
        elif operacao == 20:
            json_bytes = get_lista_arquivos_json().encode('utf-8')
            con.send(b'\x00') 
            con.send(len(json_bytes).to_bytes(4, 'big'))
            con.sendall(json_bytes)

        # OPÇÃO 3: UPLOAD
        elif operacao == 30:
            tam_nome = int.from_bytes(con.recv(4), 'big')
            nome_arquivo = con.recv(tam_nome).decode('utf-8')
            con.send(b'\x00') # Confirma recebimento do nome
            
            tam_arquivo = int.from_bytes(con.recv(4), 'big')
            nome_final = f"RECV_{cliente[0]}_{nome_arquivo}"
            
            bytes_recebidos = 0
            with open(nome_final, 'wb') as f:
                while bytes_recebidos < tam_arquivo:
                    chunk = con.recv(min(BUFFER_SIZE, tam_arquivo - bytes_recebidos))
                    if not chunk: break
                    f.write(chunk)
                    bytes_recebidos += len(chunk)
            
            con.send(b'\x00' if bytes_recebidos == tam_arquivo else b'\x01')
            print(f" [UPLOAD] '{nome_final}' concluído de {cliente}")

    except Exception as e:
        print(f" [ERRO] Cliente {cliente}: {e}")
    finally:
        con.close()
        print(f" [DESCONECTADO] {cliente}")

# --- LOOP PRINCIPAL ---
while True:
    try:
        con, cliente = server_socket.accept()
        thread = threading.Thread(target=tratar_cliente, args=(con, cliente))
        thread.daemon = True
        thread.start()
        print(f" [SISTEMA] Clientes ativos: {threading.active_count() - 1}")
    except KeyboardInterrupt:
        print("\n Desligando servidor...")
        break
server_socket.close()