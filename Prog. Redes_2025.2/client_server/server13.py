import socket, os, json

HOST = ''
PORT = 20000
BUFFER_SIZE = 4096

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)
print(f" Servidor TCP escutando em {HOST}:{PORT}...")

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

        # DOWNLOAD 
        if operacao == 10:
            tam_nome = int.from_bytes(con.recv(4), 'big')
            nome_arquivo = con.recv(tam_nome).decode('utf-8')
            print(f" Solicitação recebida: '{nome_arquivo}'")
            
            if os.path.exists(nome_arquivo):
                print(f" Arquivo '{nome_arquivo}' encontrado. Iniciando envio.")
                con.send(b'\x00') # INVERTIDO: 0 = Encontrado
                tam_arquivo = os.path.getsize(nome_arquivo)
                con.send(tam_arquivo.to_bytes(4, 'big'))

                with open(nome_arquivo, 'rb') as f:
                    bytes_enviados = 0
                    while (chunk := f.read(BUFFER_SIZE)):
                        con.sendall(chunk)
                        bytes_enviados += len(chunk)
                print(f" Transferência de '{nome_arquivo}' completa.")
            else:
                print(f" Arquivo '{nome_arquivo}' não encontrado.")
                con.send(b'\x01') # INVERTIDO: 1 = Não encontrado

        # LISTAGEM
        elif operacao == 20:
            print(" Solicitação recebida: 'Listar_Arquivos'")
            json_str = get_lista_arquivos_json()
            json_bytes = json_str.encode('utf-8')
            
            con.send(b'\x00') # INVERTIDO: 0 = Sucesso
            con.send(len(json_bytes).to_bytes(4, 'big'))
            con.sendall(json_bytes)
            print(f" JSON de listagem enviado.")

        # UPLOAD
        elif operacao == 30:
            tam_nome = int.from_bytes(con.recv(4), 'big')
            nome_arquivo = con.recv(tam_nome).decode('utf-8')
            print(f" Solicitação recebida: 'Upload_Arquivo:{nome_arquivo}'")
            
            con.send(b'\x00') # INVERTIDO: 0 = OK (Pode enviar)
            tam_arquivo = int.from_bytes(con.recv(4), 'big')
            
            bytes_recebidos = 0
            with open(nome_arquivo, 'wb') as f:
                while bytes_recebidos < tam_arquivo:
                    chunk = con.recv(min(BUFFER_SIZE, tam_arquivo - bytes_recebidos))
                    if not chunk: break
                    f.write(chunk)
                    bytes_recebidos += len(chunk)
            
            if bytes_recebidos == tam_arquivo:
                con.send(b'\x00') # INVERTIDO: 0 = Sucesso
            else:
                con.send(b'\x01') # INVERTIDO: 1 = Falha

    except Exception as e:
        print(f" Erro: {e}")
    finally:
        if con: con.close()