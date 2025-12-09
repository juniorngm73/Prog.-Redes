import socket, os, sys, json


HOST = '127.0.0.1' 
PORT = 60000 
BUFFER_SIZE = 4096
LISTAGEM = 'Listar_Arquivos'

tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    tcp_socket.connect((HOST, PORT)) 
    print(f" Conectado ao servidor {HOST}:{PORT}.")

    print("\nEscolha uma opção:")
    print(" 1 - Baixar um arquivo (informe o nome)")
    print(" 2 - Listar Arquivos ")
    

    # ESCOLHA DA OPÇÃO
    escolha = input('Digite 1 ou 2: ').strip()
    
    if escolha == '1':
        nome_arquivo_str = input('Digite o nome do arquivo para baixar: ').strip()
        if not nome_arquivo_str:
            print("Nome do arquivo inválido. Encerrando.")
            sys.exit()
        solicitacao_str = nome_arquivo_str
        
    elif escolha == '2':
        solicitacao_str = LISTAGEM
        print(" Solicitando Lista de Arquivos em JSON...")
        
    else:
        print("Opção inválida. Encerrando.")
        sys.exit()
        
    # Preparação para envio
    solicitacao_bytes = solicitacao_str.encode('utf-8')
    tam_solicitacao = len(solicitacao_bytes)

    if tam_solicitacao > 255:
        print("Solicitação muito longa. Máximo de 255 bytes.")
        sys.exit()

    # 2. ENVIO DO TAMANHO DA SOLICITAÇÃO (1 byte)
    tam_dados = tam_solicitacao.to_bytes(1, 'big')
    tcp_socket.send(tam_dados)
    
    # 3. ENVIO DA SOLICITAÇÃO
    tcp_socket.send(solicitacao_bytes)
    print(f" Enviado para o servidor: '{solicitacao_str}'")

    # 4. RECEBIMENTO DO STATUS (1 byte)
    status_dados = b''
    while len(status_dados) < 1:
        chunk = tcp_socket.recv(1 - len(status_dados))
        if not chunk:
            raise EOFError("Conexão encerrada antes de receber o status.")
        status_dados += chunk
        
    status = int.from_bytes(status_dados, 'big')
    
    # 5. LÓGICA DE RESPOSTA
    
    if solicitacao_str == LISTAGEM:
        ## --- LÓGICA DE LISTAGEM EM JSON (e exibição como lista de dicionários) ---
        if status == 2:
            print("  Recebendo dados JSON...")
            
            # RECEBIMENTO DO TAMANHO DO JSON (4 bytes)
            tam_json_dados = b''
            while len(tam_json_dados) < 4:
                chunk = tcp_socket.recv(4 - len(tam_json_dados))
                if not chunk:
                    raise EOFError("Conexão encerrada antes de receber o tamanho do JSON.")
                tam_json_dados += chunk
            tam_json = int.from_bytes(tam_json_dados, 'big')
            
            # RECEBIMENTO DO CONTEÚDO JSON
            json_dados = b''
            while len(json_dados) < tam_json:
                data = tcp_socket.recv(min(BUFFER_SIZE, tam_json - len(json_dados))) 
                if not data:
                    break 
                json_dados += data
            
            if len(json_dados) == tam_json:
                json_str = json_dados.decode('utf-8')
                # Converte o JSON em um objeto Python (dicionário)
                dados = json.loads(json_str) 
                
                print("\n LISTAGEM DE ARQUIVOS :")
                print("-" * 40)
                
                # O item que contém a lista de dicionários é 'arquivos_disponiveis'
                lista_de_dicionarios = dados.get('arquivos_disponiveis', [])
                
                # Usa 'json.dumps' para imprimir a lista de dicionários formatada e legível
                print(json.dumps(lista_de_dicionarios, indent=4))
                    
                print("-" * 40)
                print(f"Total de Arquivos: **{dados.get('total', 0)}**")
            else:
                print(f"  Recebimento do JSON incompleto. Esperado: {tam_json}, Recebido: {len(json_dados)}.")

        else:
             print(f" Status inesperado para listagem: {status}")

    else:
        ## --- LÓGICA DE DOWNLOAD DE ARQUIVO ---
        if status == 0:
            print(f"  O servidor informou que o arquivo '{solicitacao_str}' não foi encontrado.")
        elif status == 1:
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
                        break # Conexão fechada
                    f.write(data)
                    bytes_recebidos += len(data)
            
            if bytes_recebidos == tam_arquivo:
                print(f"  Download de '{solicitacao_str}' completo. Total de {bytes_recebidos} bytes salvos.")
            else:
                print(f"  Download incompleto. Esperado: {tam_arquivo}, Recebido: {bytes_recebidos}.")
            
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