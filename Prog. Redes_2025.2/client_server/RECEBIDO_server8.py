import socket, os, json, sys

if len(sys.argv) != 2:
    print("Uso correto: python servidor.py <porta>")
    sys.exit(1)

HOST = ''
PORT = int(sys.argv[1])
BUFFER_SIZE = 4096

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)

hostname = socket.gethostname()
ips = socket.gethostbyname_ex(hostname)[2]
print(f" Servidor iniciado! Escutando na porta: {PORT}")
print(f" IPs disponíveis: {ips}")

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
        print(f'\n-- Conectado por: {cliente}')

        op_byte = con.recv(1)
        if not op_byte: continue
        operacao = int.from_bytes(op_byte, 'big')

        if operacao == 10: # DOWNLOAD
            tam_nome = int.from_bytes(con.recv(4), 'big')
            nome_arquivo = con.recv(tam_nome).decode('utf-8')
            print(f" Solicitação de download: '{nome_arquivo}'")
            
            if os.path.exists(nome_arquivo):
                tam_arquivo = os.path.getsize(nome_arquivo)
                print(f" Arquivo encontrado. Enviando {tam_arquivo} bytes...")
                con.send(b'\x00')
                con.send(tam_arquivo.to_bytes(4, 'big'))
                with open(nome_arquivo, 'rb') as f:
                    while (chunk := f.read(BUFFER_SIZE)):
                        con.sendall(chunk)
                print(f" Transferência de '{nome_arquivo}' completa.")
            else:
                print(f" Arquivo '{nome_arquivo}' não encontrado.")
                con.send(b'\x01')

        elif operacao == 20: # LISTAGEM
            print(" Enviando lista de arquivos...")
            json_str = get_lista_arquivos_json()
            json_bytes = json_str.encode('utf-8')
            con.send(b'\x00') 
            con.send(len(json_bytes).to_bytes(4, 'big'))
            con.sendall(json_bytes)

        elif operacao == 30: # UPLOAD
            # 1. Recebe o tamanho do nome e o nome
            dados_tam_nome = con.recv(4)
            if not dados_tam_nome: continue
            tam_nome = int.from_bytes(dados_tam_nome, 'big')
            nome_arquivo = con.recv(tam_nome).decode('utf-8')
            
            # 2. Avisa ao cliente: "Recebi o nome, pode me falar o tamanho do arquivo"
            con.send(b'\x00') 
            
            # 3. Recebe o tamanho real do arquivo
            dados_tam_arq = con.recv(4)
            if not dados_tam_arq: continue
            tam_arquivo = int.from_bytes(dados_tam_arq, 'big')
            
            print(f" Recebendo: {nome_arquivo} | Esperado: {tam_arquivo} bytes")
            
            # 4. Loop de gravação
            bytes_recebidos = 0
            with open("RECV_" + nome_arquivo, 'wb') as f:
                while bytes_recebidos < tam_arquivo:
                    # Lê apenas o que falta ou o tamanho do buffer
                    chunk = con.recv(min(BUFFER_SIZE, tam_arquivo - bytes_recebidos))
                    if not chunk:
                        break
                    f.write(chunk)
                    bytes_recebidos += len(chunk)
            
            # 5. Confirmação final
            if bytes_recebidos == tam_arquivo:
                con.send(b'\x00')
                print(f" Arquivo {nome_arquivo} salvo com sucesso.")
            else:
                con.send(b'\x01')
                print(f" Erro: Recebidos {bytes_recebidos} de {tam_arquivo}")

    except Exception as e:
        print(f" Erro: {e}")
    finally:
        if con: 
            con.close()
            print(f" Conexão com {cliente} encerrada.")