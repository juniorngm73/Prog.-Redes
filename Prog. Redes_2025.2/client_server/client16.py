import socket, os, sys, json

def exibir_progresso(atual, total):
    percentual = (atual / total) * 100
    barra = '#' * int(percentual // 5)
    sys.stdout.write(f"\rProgresso: [{barra:-<20}] {percentual:.1f}% ({atual}/{total} bytes)")
    sys.stdout.flush()

if len(sys.argv) != 2:
    print("Uso: python cliente.py <ip>:<porta>")
    sys.exit(1)

try:
    alvo = sys.argv[1].split(':')
    HOST, PORT = alvo[0], int(alvo[1])
    BUFFER_SIZE = 4096
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((HOST, PORT))
    print(f" Conectado a {HOST}:{PORT}")

    print("\n1 - Baixar | 2 - Listar | 3 - Upload")
    escolha = input('Escolha: ').strip()

    if escolha == '1': # DOWNLOAD
        nome_arquivo = input('Nome do arquivo para baixar: ').strip()
        nome_bytes = nome_arquivo.encode('utf-8')
        tcp_socket.send(b'\x0a')
        tcp_socket.send(len(nome_bytes).to_bytes(4, 'big'))
        tcp_socket.send(nome_bytes)

        if tcp_socket.recv(1) == b'\x00':
            tam_arq = int.from_bytes(tcp_socket.recv(4), 'big')
            with open("DOWNLOAD_" + nome_arquivo, 'wb') as f:
                recebido = 0
                while recebido < tam_arq:
                    chunk = tcp_socket.recv(min(BUFFER_SIZE, tam_arq - recebido))
                    f.write(chunk)
                    recebido += len(chunk)
                    exibir_progresso(recebido, tam_arq)
            print(f"\n Download concluído!")
        else:
            print(" Arquivo não encontrado no servidor.")

    elif escolha == '2': # LISTAGEM
        tcp_socket.send(b'\x14')
        if tcp_socket.recv(1) == b'\x00':
            tam_json = int.from_bytes(tcp_socket.recv(4), 'big')
            dados = b"".join([tcp_socket.recv(tam_json)]) # Simplificado para listas pequenas
            lista = json.loads(dados.decode('utf-8'))
            print("\nARQUIVOS NO SERVIDOR:")
            for item in lista:
                print(f" - {item['nome']} ({item['tamanho_bytes']} bytes)")

    elif escolha == '3': # UPLOAD
        caminho = input('Caminho do arquivo local: ').strip()
        if os.path.exists(caminho):
            tam_arquivo = os.path.getsize(caminho)
            tcp_socket.send(b'\x1e')
            nome_bytes = os.path.basename(caminho).encode('utf-8')
            tcp_socket.send(len(nome_bytes).to_bytes(4, 'big'))
            tcp_socket.send(nome_bytes)

            if tcp_socket.recv(1) == b'\x00':
                tcp_socket.send(tam_arquivo.to_bytes(4, 'big'))
                enviado = 0
                with open(caminho, 'rb') as f:
                    while (chunk := f.read(BUFFER_SIZE)):
                        tcp_socket.sendall(chunk)
                        enviado += len(chunk)
                        exibir_progresso(enviado, tam_arquivo)
                
                if tcp_socket.recv(1) == b'\x00':
                    print(f"\n Upload realizado com sucesso!")
        else:
            print(" Arquivo local não existe.")

except Exception as e:
    print(f"\n Erro: {e}")
finally:
    tcp_socket.close()