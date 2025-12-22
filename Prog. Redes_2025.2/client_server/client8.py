2import socket, os, sys, json

if len(sys.argv) != 2:
    print("Uso correto: python cliente.py <ip>:<porta>")
    sys.exit(1)

try:
    alvo = sys.argv[1].split(':')
    HOST = alvo[0]
    PORT = int(alvo[1])
except (IndexError, ValueError):
    print("Erro: Formato inválido. Use IP:PORTA (Ex: 127.0.0.1:20000)")
    sys.exit(1)

BUFFER_SIZE = 4096
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    tcp_socket.connect((HOST, PORT))
    print(f" Conectado ao servidor {HOST}:{PORT}.")
    print("\nEscolha uma opção:\n 1 - Baixar\n 2 - Listar\n 3 - Upload")
    escolha = input('Digite 1, 2 ou 3: ').strip()

    if escolha == '1':
        nome_arquivo = input('Digite o nome do arquivo para baixar: ').strip()
        print(f" Enviado para o servidor: '{nome_arquivo}'")
        nome_bytes = nome_arquivo.encode('utf-8')
        tcp_socket.send(b'\x0a') 
        tcp_socket.send(len(nome_bytes).to_bytes(4, 'big'))
        tcp_socket.send(nome_bytes)

        if tcp_socket.recv(1) == b'\x00':
            print(" Arquivo encontrado. Recebendo metadados...")
            tam_arq = int.from_bytes(tcp_socket.recv(4), 'big')
            print(f" Tamanho total do arquivo a receber: {tam_arq} bytes.")
            with open("RECEBIDO_" + nome_arquivo, 'wb') as f:
                recebido = 0
                while recebido < tam_arq:
                    chunk = tcp_socket.recv(min(BUFFER_SIZE, tam_arq - recebido))
                    f.write(chunk)
                    recebido += len(chunk)
            print(f" Download de '{nome_arquivo}' completo. Total de {recebido} bytes salvos.")
        else:
            print(f" O servidor informou que o arquivo '{nome_arquivo}' não foi encontrado.")

    elif escolha == '2':
        tcp_socket.send(b'\x14') 
        if tcp_socket.recv(1) == b'\x00':
            tam_json = int.from_bytes(tcp_socket.recv(4), 'big')
            json_dados = b""
            while len(json_dados) < tam_json:
                json_dados += tcp_socket.recv(tam_json - len(json_dados))
            lista = json.loads(json_dados.decode('utf-8'))
            print("\n" + json.dumps(lista, indent=4))
            print("-" * 40)
            print(f"Total de Arquivos: {len(lista)}")

    elif escolha == '3':
        nome_arquivo = input('Digite o nome do arquivo LOCAL para upload: ').strip()
        if not os.path.exists(nome_arquivo):
            print("Erro: Arquivo local não encontrado.")
        else:
            tam_arquivo = os.path.getsize(nome_arquivo)
            tcp_socket.send(b'\x1e')  # Envia comando 30
            
            # Envia nome do arquivo
            nome_bytes = nome_arquivo.encode('utf-8')
            tcp_socket.send(len(nome_bytes).to_bytes(4, 'big'))
            tcp_socket.send(nome_bytes)

            # ESPERA o servidor dizer que recebeu o nome e está pronto
            confirmacao = tcp_socket.recv(1)
            if confirmacao == b'\x00':
                # Agora envia o tamanho do conteúdo
                tcp_socket.send(tam_arquivo.to_bytes(4, 'big'))
                
                print(f" Enviando '{nome_arquivo}' ({tam_arquivo} bytes)...")
                with open(nome_arquivo, 'rb') as f:
                    while True:
                        chunk = f.read(BUFFER_SIZE)
                        if not chunk:
                            break
                        tcp_socket.sendall(chunk)
                
                # ESPERA o servidor confirmar que salvou tudo
                if tcp_socket.recv(1) == b'\x00':
                    print(f" Upload concluído com sucesso!")
                else:
                    print(" Erro: O servidor não confirmou o recebimento total.")

except Exception as e:
    print(f" Ocorreu um erro: {e}")
finally:
    tcp_socket.close()
    print(" Conexão encerrada.")