import socket, os, json, sys

# Verificação de argumentos
if len(sys.argv) != 2:
    print("Uso correto: python servidor.py <porta>")
    sys.exit(1)

HOST = ''  # Escuta em todas as interfaces
PORT = int(sys.argv[1])
BUFFER_SIZE = 4096

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)

# Listar IPs disponíveis no servidor
hostname = socket.gethostname()
ips = socket.gethostbyname_ex(hostname)[2]
print(f" Servidor iniciado!")
print(f" Escutando em todas as interfaces na porta: {PORT}")
print(f" IPs disponíveis para conexão: {ips}")

def get_lista_arquivos_json():
    arquivos_info = []
    for f in os.listdir('.'):
        if os.path.isfile(f) and f not in ('servidor.py', 'cliente.py'):
            tamanho = os.path.getsize(f)
            arquivos_info.append({"nome": f, "tamanho_bytes": tamanho})
    return json.dumps(arquivos_info, indent=4)

while True:
    con = None
    try:
        con, cliente = server_socket.accept()
        print('\n\n-- Conectado por:', cliente)

        op_byte = con.recv(1)
        if not op_byte: continue
        operacao = int.from_bytes(op_byte, 'big')

        # DOWNLOAD (10)
        if operacao == 10:
            tam_nome = int.from_bytes(con.recv(4), 'big')
            nome_arquivo = con.recv(tam_nome).decode('utf-8')
            
            if os.path.exists(nome_arquivo):
                con.send(b'\x00') # 0 = Sucesso
                tam_arquivo = os.path.getsize(nome_arquivo)
                con.send(tam_arquivo.to_bytes(4, 'big'))
                with open(nome_arquivo, 'rb') as f:
                    while (chunk := f.read(BUFFER_SIZE)):
                        con.sendall(chunk)
            else:
                con.send(b'\x01') # 1 = Erro

        # LISTAGEM (20)
        elif operacao == 20:
            json_str = get_lista_arquivos_json()
            json_bytes = json_str.encode('utf-8')
            con.send(b'\x00') 
            con.send(len(json_bytes).to_bytes(4, 'big'))
            con.sendall(json_bytes)

        # UPLOAD (30)
        elif operacao == 30:
            tam_nome = int.from_bytes(con.recv(4), 'big')
            nome_arquivo = con.recv(tam_nome).decode('utf-8')
            con.send(b'\x00') 
            tam_arquivo = int.from_bytes(con.recv(4), 'big')
            bytes_recebidos = 0
            with open(nome_arquivo, 'wb') as f:
                while bytes_recebidos < tam_arquivo:
                    chunk = con.recv(min(BUFFER_SIZE, tam_arquivo - bytes_recebidos))
                    if not chunk: break
                    f.write(chunk)
                    bytes_recebidos += len(chunk)
            con.send(b'\x00' if bytes_recebidos == tam_arquivo else b'\x01')

    except Exception as e:
        print(f" Erro: {e}")
    finally:
        if con: con.close()