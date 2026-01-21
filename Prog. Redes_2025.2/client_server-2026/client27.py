import socket, os, sys, json, hashlib
from tqdm import tqdm

if len(sys.argv) != 2:
    print("Uso: python cliente.py <ip>:<porta>")
    sys.exit(1)

try:
    alvo = sys.argv[1].split(':')
    HOST, PORT = alvo[0], int(alvo[1])
except:
    print("Erro formato IP:PORTA"); sys.exit(1)

BUFFER_SIZE = 4096
CLIENT_DIR = "client_files"
if not os.path.exists(CLIENT_DIR): os.makedirs(CLIENT_DIR)

def calculate_md5_local(filepath):
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.digest()

tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.settimeout(60)

try:
    tcp_socket.connect((HOST, PORT))
    print(f"Conectado a {HOST}:{PORT}")

    while True:
        print("\n--- MENU ---")
        print("1-Download  2-Listar  3-Upload  4-Resume  5-Múltiplos  0-Sair")
        escolha = input('Opção: ').strip()

        if escolha == '0': break

        # 1: DOWNLOAD
        if escolha == '1':
            nome = input('Digite o nome do arquivo para baixar: ').strip()
            nome_b = nome.encode('utf-8')
            tcp_socket.send((10).to_bytes(1, 'big'))
            tcp_socket.send(len(nome_b).to_bytes(4, 'big'))
            tcp_socket.send(nome_b)
            
            if tcp_socket.recv(1) == b'\x00':
                tam = int.from_bytes(tcp_socket.recv(4), 'big')
                
                # Criamos a barra de progresso aqui
                # unit='B' diz que a unidade é bytes, unit_scale converte para KB/MB
                progress_bar = tqdm(total=tam, unit='iB', unit_scale=True, desc=f"Baixando {nome}")

                with open(os.path.join(CLIENT_DIR, "DL_"+nome), 'wb') as f:
                    recebido = 0
                    while recebido < tam:
                        chunk = tcp_socket.recv(min(BUFFER_SIZE, tam - recebido))
                        if not chunk: break
                        f.write(chunk)
                        recebido += len(chunk)
                        
                        # Atualiza a barra com o tamanho do pedaço recebido
                        progress_bar.update(len(chunk))
                
                progress_bar.close() # Fecha a barra ao terminar
                print(f"\n Download concluído.")

        # 2: LISTAR
        elif escolha == '2':
            tcp_socket.send((20).to_bytes(1, 'big'))
            if tcp_socket.recv(1) == b'\x00':
                tam = int.from_bytes(tcp_socket.recv(4), 'big')
                dados = b""
                while len(dados) < tam: dados += tcp_socket.recv(tam - len(dados))
                print("\nArquivos no servidor:")
                print(json.dumps(json.loads(dados.decode()), indent=2))

        # 3: UPLOAD
        elif escolha == '3':
            nome = input('Nome do arquivo em client_files para upload: ').strip()
            path = os.path.join(CLIENT_DIR, nome)
            if os.path.exists(path):
                nome_b = nome.encode('utf-8')
                tcp_socket.send((30).to_bytes(1, 'big'))
                tcp_socket.send(len(nome_b).to_bytes(4, 'big'))
                tcp_socket.send(nome_b)
                
                if tcp_socket.recv(1) == b'\x00':
                    tam = os.path.getsize(path)
                    print(f" Arquivo '{nome}' pronto para upload. Tamanho: {tam} bytes.")
                    tcp_socket.send(tam.to_bytes(4, 'big'))
                    with open(path, 'rb') as f:
                        enviado = 0
                        while (chunk := f.read(BUFFER_SIZE)):
                            tcp_socket.sendall(chunk)
                            enviado += len(chunk)
                    
                    if tcp_socket.recv(1) == b'\x00':
                        print(f" Upload de '{nome}' concluído com sucesso ({enviado} bytes).")
                    else:
                        print(" Erro durante o salvamento no servidor.")
            else: print(" Arquivo local não existe.")

        # 4: RESUME
        elif escolha == '4':
            nome = input('Retomar download de (nome original): ').strip()
            path = os.path.join(CLIENT_DIR, "RS_"+nome)
            pos = os.path.getsize(path) if os.path.exists(path) else 0
            h = calculate_md5_local(path) if pos > 0 else b'\x00'*16
            
            print(f" Solicitando retomada de '{nome}' a partir de {pos} bytes...")
            nome_b = nome.encode('utf-8')
            tcp_socket.send((40).to_bytes(1, 'big'))
            tcp_socket.send(len(nome_b).to_bytes(4, 'big'))
            tcp_socket.send(nome_b)
            tcp_socket.send(pos.to_bytes(4, 'big'))
            tcp_socket.send(h)
            
            if tcp_socket.recv(1) == b'\x00':
                status = tcp_socket.recv(1)
                if status == b'\x00':
                    tam_rem = int.from_bytes(tcp_socket.recv(4), 'big')
                    print(f" Resume aceito. Faltam {tam_rem} bytes.")
                    with open(path, 'ab') as f:
                        rec = 0
                        while rec < tam_rem:
                            chunk = tcp_socket.recv(min(BUFFER_SIZE, tam_rem - rec))
                            f.write(chunk); rec += len(chunk)
                    print(f" Resume de '{nome}' concluído. Arquivo atualizado.")
                else: 
                    print(f" Erro no Resume. Código de erro: {status}")
            else: print(" Erro na comunicação com servidor.")

        # 5: MASK
        elif escolha == '5':
            mask_str = input('Digite a máscara (ex: *.jpg): ').strip()
            mask = mask_str.encode('utf-8')
            tcp_socket.send((50).to_bytes(1, 'big'))
            tcp_socket.send(len(mask).to_bytes(4, 'big'))
            tcp_socket.send(mask)
            
            tam_j = int.from_bytes(tcp_socket.recv(4), 'big')
            arqs = json.loads(tcp_socket.recv(tam_j).decode())
            
            if not arqs:
                print(" Nenhum arquivo corresponde à máscara.")
            else:
                print(f" Encontrado(s) {len(arqs)} arquivo(s). Iniciando downloads...")
                for n in arqs:
                    t = int.from_bytes(tcp_socket.recv(4), 'big')
                    print(f" -> Baixando {n} ({t} bytes)...", end="", flush=True)
                    with open(os.path.join(CLIENT_DIR, "MASK_"+n), 'wb') as f:
                        r = 0
                        while r < t:
                            c = tcp_socket.recv(min(BUFFER_SIZE, t-r))
                            f.write(c); r += len(c)
                    print(" OK")
                print(" Todos os arquivos da máscara foram baixados.")

except Exception as e: print(f"Erro inesperado: {e}")
finally: tcp_socket.close(); print("Conexão encerrada.")