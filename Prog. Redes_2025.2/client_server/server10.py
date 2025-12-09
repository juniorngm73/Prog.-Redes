import socket, os, json


HOST = '' 
PORT = 60000
BUFFER_SIZE = 4096
LISTAGEM = 'Listar_Arquivos'

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    server_socket.bind((HOST, PORT)) 
    server_socket.listen(5) 
    print(f' Servidor TCP escutando em {HOST}:{PORT}...')
except Exception as e:
    print(f" Erro ao iniciar o servidor: {e}")
    exit()

def get_lista_arquivos_json():
    """Retorna uma string JSON contendo a lista de arquivos e seus tamanhos."""
    
    arquivos_info = []
    
    # Itera sobre todos os itens no diretório
    for f in os.listdir('.'):
        # Verifica se é um arquivo e não é o script do servidor
        if os.path.isfile(f) and f != 'servidor.py':
            try:
                # Obtém o tamanho do arquivo em bytes
                tamanho = os.path.getsize(f)
                arquivos_info.append({
                    "nome": f,
                    "tamanho_bytes": tamanho
                })
            except Exception as e:
                # Ignora arquivos que não podem ter o tamanho lido
                print(f"Erro ao obter tamanho de {f}: {e}")
                
    # Constrói o objeto Python que será transformado em JSON
    dados_json = {
        "status": "sucesso",
        "arquivos_disponiveis": arquivos_info,
        "total": len(arquivos_info)
    }

    # Converte o objeto Python para uma string JSON
    # O JSON terá esta estrutura (simplificada): 
    # {"arquivos_disponiveis": [{"nome": "file.txt", "tamanho_bytes": 1234}, ...]}
    return json.dumps(dados_json, indent=4) # Usando indent para melhor visualização no debug/servidor

while True:
    con = None 
    try:
        con, cliente = server_socket.accept() 
        print('\n\n-- Conectado por:', cliente)

        # 1. RECEBIMENTO DO TAMANHO DA SOLICITAÇÃO (1 byte)
        tam_solicitacao_dados = b''
        while len(tam_solicitacao_dados) < 1:
            chunk = con.recv(1 - len(tam_solicitacao_dados))
            if not chunk:
                raise EOFError("Conexão encerrada prematuramente ao ler o tamanho da solicitação.")
            tam_solicitacao_dados += chunk
            
        tam_solicitacao = int.from_bytes(tam_solicitacao_dados, 'big')
        
        # 2. RECEBIMENTO DA SOLICITAÇÃO
        dados_solicitacao = b''
        while len(dados_solicitacao) < tam_solicitacao:
            chunk = con.recv(tam_solicitacao - len(dados_solicitacao))
            if not chunk:
                raise EOFError("Conexão encerrada prematuramente ao ler a solicitação.")
            dados_solicitacao += chunk

        solicitacao_str = dados_solicitacao.decode('utf-8')
        print(f" Solicitação recebida: '{solicitacao_str}'")

        # 3. VERIFICAÇÃO DO TIPO DE SOLICITAÇÃO E RESPOSTA
        
        if solicitacao_str == LISTAGEM:
            ## --- LÓGICA DE LISTAGEM EM JSON ---
            print(" Comando de listagem recebido. Enviando lista em JSON.")
            con.send(b'\x02') # Envia status 2 (para LISTAGEM)
            
            # Obtém a string JSON
            json_str = get_lista_arquivos_json()
            json_bytes = json_str.encode('utf-8')
            tam_json = len(json_bytes)

            # 4. ENVIO DO TAMANHO DO JSON (4 bytes)
            tam_dados = tam_json.to_bytes(4, 'big')
            con.send(tam_dados)
            print(f" Tamanho do JSON: {tam_json} bytes.")
            
            # 5. ENVIO DO CONTEÚDO JSON
            con.sendall(json_bytes)
            
            print(f" JSON de listagem enviado. Total de {len(json_bytes)} bytes.")

        else:
            ## --- LÓGICA DE DOWNLOAD DE ARQUIVO ---
            nome_arquivo = solicitacao_str
            if not os.path.exists(nome_arquivo) or not os.path.isfile(nome_arquivo):
                print(f" Arquivo '{nome_arquivo}' não encontrado.")
                con.send(b'\x00') # Envia status 0
            else:
                print(f" Arquivo '{nome_arquivo}' encontrado. Iniciando envio.")
                con.send(b'\x01') # Envia status 1
                tam_arquivo = os.path.getsize(nome_arquivo)
                
                # 4. ENVIO DO TAMANHO DO ARQUIVO (4 bytes)
                tam_dados = tam_arquivo.to_bytes(4, 'big')
                con.send(tam_dados)
                print(f" Tamanho do arquivo: {tam_arquivo} bytes.")
                
                # 5. ENVIO DO CONTEÚDO DO ARQUIVO
                with open(nome_arquivo, 'rb') as f:
                    bytes_enviados = 0
                    while bytes_enviados < tam_arquivo:
                        chunk = f.read(BUFFER_SIZE) 
                        con.send(chunk)
                        bytes_enviados += len(chunk)
                
                print(f" Transferência de '{nome_arquivo}' completa. Total de {bytes_enviados} bytes enviados.")

    except EOFError as e:
        print(f" Conexão com {cliente} perdida: {e}")
    except Exception as e:
        print(f" Ocorreu um erro na comunicação com {cliente}: {e}")
    finally:
        if con:
            con.close() 
            print(f" Conexão com {cliente} encerrada.")