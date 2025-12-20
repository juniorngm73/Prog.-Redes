import socket, os, sys, json

HOST = '127.0.0.1' 
PORT = 20000
BUFFER_SIZE = 4096

tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    tcp_socket.connect((HOST, PORT))
    print(f" Conectado ao servidor {HOST}:{PORT}.")
    print("\nEscolha uma opção:\n 1 - Baixar\n 2 - Listar\n 3 - Upload")
    escolha = input('Digite 1, 2 ou 3: ').strip()

    # DOWNLOAD
    if escolha == '1':
        nome_arquivo = input('Digite o nome do arquivo para baixar: ').strip()
        nome_bytes = nome_arquivo.encode('utf-8')
        
        tcp_socket.send(b'\x0a') 
        tcp_socket.send(len(nome_bytes).to_bytes(4, 'big'))
        tcp_socket.send(nome_bytes)

        status = tcp_socket.recv(1)
        if status == b'\x00': # INVERTIDO: 0 significa encontrado
            print(" Arquivo encontrado. Recebendo metadados...")
            tam_arq = int.from_bytes(tcp_socket.recv(4), 'big')
            with open("RECEBIDO_" + nome_arquivo, 'wb') as f:
                recebido = 0
                while recebido < tam_arq:
                    chunk = tcp_socket.recv(min(BUFFER_SIZE, tam_arq - recebido))
                    f.write(chunk)
                    recebido += len(chunk)
            print(f" Download de '{nome_arquivo}' completo.")
        else:
            print(f" O servidor informou que o arquivo '{nome_arquivo}' não foi encontrado.")

    # LISTAGEM 
    elif escolha == '2':
        tcp_socket.send(b'\x14') 
        status = tcp_socket.recv(1)
        if status == b'\x00': # INVERTIDO: 0 significa sucesso
            tam_json = int.from_bytes(tcp_socket.recv(4), 'big')
            json_dados = b""
            while len(json_dados) < tam_json:
                json_dados += tcp_socket.recv(tam_json - len(json_dados))
            
            lista = json.loads(json_dados.decode('utf-8'))
            print("\n" + json.dumps(lista, indent=4))
            print("-" * 40)
            print(f"Total de Arquivos: **{len(lista)}**") # Mantido conforme original
        else:
            print(" Erro ao obter a lista de arquivos.")

    # UPLOAD 
    elif escolha == '3':
        nome_arquivo = input('Digite o nome do arquivo LOCAL para upload: ').strip()
        if not os.path.exists(nome_arquivo):
            sys.exit("Erro: Arquivo local não encontrado.")
            
        nome_bytes = nome_arquivo.encode('utf-8')
        tcp_socket.send(b'\x1e') 
        tcp_socket.send(len(nome_bytes).to_bytes(4, 'big'))
        tcp_socket.send(nome_bytes)

        if tcp_socket.recv(1) == b'\x00': # INVERTIDO: 0 significa servidor pronto
            tam_arquivo = os.path.getsize(nome_arquivo)
            tcp_socket.send(tam_arquivo.to_bytes(4, 'big'))
            with open(nome_arquivo, 'rb') as f:
                while (chunk := f.read(BUFFER_SIZE)):
                    tcp_socket.sendall(chunk)
            
            if tcp_socket.recv(1) == b'\x00': # INVERTIDO: 0 significa sucesso final
                print(" Sucesso no Upload: Servidor confirmou o recebimento.")

except Exception as e:
    print(f" Ocorreu um erro: {e}")
finally:
    tcp_socket.close()