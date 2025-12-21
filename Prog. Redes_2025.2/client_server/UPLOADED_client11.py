import socket, os, sys, json

HOST = '127.0.0.1'
PORT = 20000
BUFFER_SIZE = 4096
LISTAGEM = 'Listar_Arquivos'
UPLOAD_CMD = 'Upload_Arquivo' # Novo comando para upload

tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    tcp_socket.connect((HOST, PORT))
    print(f" Conectado ao servidor {HOST}:{PORT}.")

    print("\nEscolha uma opção:")
    print(" 1 - Baixar um arquivo (informe o nome)")
    print(" 2 - Listar Arquivos ")
    print(" 3 - Fazer Upload de um arquivo (do cliente para o servidor)") # NOVA OPÇÃO

    # ESCOLHA DA OPÇÃO
    escolha = input('Digite 1, 2 ou 3: ').strip()

    if escolha == '1':
        # ... (Lógica de Download existente) ...
        nome_arquivo_str = input('Digite o nome do arquivo para baixar: ').strip()
        if not nome_arquivo_str:
            print("Nome do arquivo inválido. Encerrando.")
            sys.exit()
        solicitacao_str = nome_arquivo_str

    elif escolha == '2':
        # ... (Lógica de Listagem existente) ...
        solicitacao_str = LISTAGEM
        print(" Solicitando Lista de Arquivos em JSON...")

    elif escolha == '3': # LÓGICA DE UPLOAD
        nome_arquivo_str = input('Digite o nome do arquivo LOCAL para upload: ').strip()
        if not nome_arquivo_str:
            print("Nome do arquivo inválido. Encerrando.")
            sys.exit()
        
        if not os.path.exists(nome_arquivo_str) or not os.path.isfile(nome_arquivo_str):
            print(f"Erro: Arquivo local '{nome_arquivo_str}' não encontrado.")
            sys.exit()

        solicitacao_str = UPLOAD_CMD + ":" + nome_arquivo_str # Comando de upload + nome do arquivo
        
    else:
        print("Opção inválida. Encerrando.")
        sys.exit()

    # Preparação para envio (Comando/Solicitação)
    solicitacao_bytes = solicitacao_str.encode('utf-8')
    tam_solicitacao = len(solicitacao_bytes)

    if tam_solicitacao > 255:
        print("Solicitação muito longa. Máximo de 255 bytes.")
        sys.exit()

    # ENVIO DO TAMANHO DA SOLICITAÇÃO (1 byte)
    tam_dados = tam_solicitacao.to_bytes(1, 'big')
    tcp_socket.send(tam_dados)

    # ENVIO DA SOLICITAÇÃO
    tcp_socket.send(solicitacao_bytes)
    print(f" Enviado para o servidor: '{solicitacao_str}'")

    # ----- LÓGICA ESPECÍFICA PARA UPLOAD (ENVIANDO O ARQUIVO APÓS O COMANDO) -----
    if escolha == '3':
        nome_local = nome_arquivo_str
        tam_arquivo = os.path.getsize(nome_local)
        print(f" Preparando para enviar arquivo: {nome_local}, Tamanho: {tam_arquivo} bytes.")

        # RECEBIMENTO DO STATUS INICIAL (1 byte)
        status_dados = b''
        while len(status_dados) < 1:
            chunk = tcp_socket.recv(1 - len(status_dados))
            if not chunk:
                raise EOFError("Conexão encerrada antes de receber o status inicial do upload.")
            status_dados += chunk
        status = int.from_bytes(status_dados, 'big')
        
        if status == 3: # 3 = Servidor pronto para receber metadados de upload
            print(" Servidor pronto. Enviando tamanho do arquivo...")
            
            # ENVIO DO TAMANHO DO ARQUIVO (4 bytes)
            tam_arquivo_dados = tam_arquivo.to_bytes(4, 'big')
            tcp_socket.send(tam_arquivo_dados)
            
            # ENVIO DO CONTEÚDO DO ARQUIVO
            bytes_enviados = 0
            with open(nome_local, 'rb') as f:
                while bytes_enviados < tam_arquivo:
                    chunk = f.read(BUFFER_SIZE)
                    if not chunk:
                        break
                    tcp_socket.send(chunk)
                    bytes_enviados += len(chunk)
            
            if bytes_enviados == tam_arquivo:
                print(f" Upload de '{nome_local}' completo. Total de {bytes_enviados} bytes enviados.")
            else:
                print(f" Upload incompleto. Esperado: {tam_arquivo}, Enviado: {bytes_enviados}.")
            
            # Aguarda a resposta final do servidor
            status_final_dados = b''
            while len(status_final_dados) < 1:
                chunk = tcp_socket.recv(1 - len(status_final_dados))
                if not chunk:
                    raise EOFError("Conexão encerrada antes de receber o status final.")
                status_final_dados += chunk
            status_final = int.from_bytes(status_final_dados, 'big')
            
            if status_final == 4: # 4 = Sucesso no Upload
                print(" Sucesso no Upload: Servidor confirmou o recebimento e salvamento.")
            elif status_final == 5: # 5 = Falha no Upload
                print(" Falha no Upload: O servidor não conseguiu salvar o arquivo.")
            else:
                print(f" Status final de Upload inesperado: {status_final}")
                
            sys.exit() # Encerra após o upload
        else:
            print(f" Status inicial inesperado para upload: {status}")
            sys.exit()
    # -----------------------------------------------------------------------------
    
    # CÓDIGO DE RESPOSTA (LISTAGEM/DOWNLOAD) - (EXISTENTE, COM PEQUENAS ALTERAÇÕES)
    
    # RECEBIMENTO DO STATUS (1 byte) - Continua para Listagem/Download
    status_dados = b''
    while len(status_dados) < 1:
        chunk = tcp_socket.recv(1 - len(status_dados))
        if not chunk:
            raise EOFError("Conexão encerrada antes de receber o status.")
        status_dados += chunk
        
    status = int.from_bytes(status_dados, 'big')
    
    # LÓGICA DE RESPOSTA
    
    if solicitacao_str == LISTAGEM:
        if status == 2: # 2 = Servidor responde com JSON (Listagem)
            # ... (Lógica de Listagem existente) ...
            print(" Recebendo dados JSON...")
            
            tam_json_dados = b''
            while len(tam_json_dados) < 4:
                chunk = tcp_socket.recv(4 - len(tam_json_dados))
                if not chunk:
                    raise EOFError("Conexão encerrada antes de receber o tamanho do JSON.")
                tam_json_dados += chunk
            tam_json = int.from_bytes(tam_json_dados, 'big')
            
            json_dados = b''
            while len(json_dados) < tam_json:
                data = tcp_socket.recv(min(BUFFER_SIZE, tam_json - len(json_dados)))
                if not data:
                    break
                json_dados += data
            
            if len(json_dados) == tam_json:
                json_str = json_dados.decode('utf-8')
                dados = json.loads(json_str)
                
                print("\n LISTAGEM DE ARQUIVOS :")
                print("-" * 40)
                
                lista_de_dicionarios = dados.get('arquivos_disponiveis', [])
                
                print(json.dumps(lista_de_dicionarios, indent=4))
                print("-" * 40)
                print(f"Total de Arquivos: **{dados.get('total', 0)}**")
            else:
                print(f" Recebimento do JSON incompleto. Esperado: {tam_json}, Recebido: {len(json_dados)}.")

        else:
            print(f" Status inesperado para listagem: {status}")

    else:
        # DOWNLOAD DE ARQUIVO ---
        if status == 0:
            print(f" O servidor informou que o arquivo '{solicitacao_str}' não foi encontrado.")
        elif status == 1: # 1 = Servidor responde com arquivo (Download)
            print(" Arquivo encontrado. Recebendo metadados...")
            
            # RECEBIMENTO DO TAMANHO DO ARQUIVO (4 bytes)
            tam_arquivo_dados = b''
            while len(tam_arquivo_dados) < 4:
                chunk = tcp_socket.recv(4 - len(tam_arquivo_dados))
                if not chunk:
                    raise EOFError("Conexão encerrada antes de receber o tamanho do arquivo.")
                tam_arquivo_dados += chunk
            tam_arquivo = int.from_bytes(tam_arquivo_dados, 'big')
            print(f" Tamanho total do arquivo a receber: {tam_arquivo} bytes.")

            # RECEBIMENTO DO CONTEÚDO DO ARQUIVO
            bytes_recebidos = 0
            with open("RECEBIDO_" + solicitacao_str, 'wb') as f:
                while bytes_recebidos < tam_arquivo:
                    data = tcp_socket.recv(min(BUFFER_SIZE, tam_arquivo - bytes_recebidos))
                    if not data:
                        break
                    f.write(data)
                    bytes_recebidos += len(data)
            
            if bytes_recebidos == tam_arquivo:
                print(f" Download de '{solicitacao_str}' completo. Total de {bytes_recebidos} bytes salvos.")
            else:
                print(f" Download incompleto. Esperado: {tam_arquivo}, Recebido: {bytes_recebidos}.")
            
        else:
            print(f" Status desconhecido recebido: {status}")

except ConnectionRefusedError:
    print(f" Erro: Conexão recusada. Certifique-se de que o servidor está em execução em {HOST}:{PORT}.")
except EOFError as e:
    print(f" Erro de protocolo/conexão: {e}")
except Exception as e:
    print(f" Ocorreu um erro: {e}")
finally:
    tcp_socket.close()
    print(" Conexão encerrada.")