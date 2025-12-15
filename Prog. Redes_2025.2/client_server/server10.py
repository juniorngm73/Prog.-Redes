import socket, os, json


HOST = '' 
PORT = 20000
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
        
    arquivos_info = []
    
    for f in os.listdir('.'):
        
        if os.path.isfile(f) and f != 'servidor.py':
            try:
                tamanho = os.path.getsize(f)
                arquivos_info.append({
                    "nome": f,
                    "tamanho_bytes": tamanho
                })
            except Exception as e:
                print(f"Erro ao obter tamanho de {f}: {e}")
                
    dados_json = {
        "status": "sucesso",
        "arquivos_disponiveis": arquivos_info,
        "total": len(arquivos_info)
    }

    return json.dumps(dados_json, indent=4) 

while True:
    con = None 
    try:
        con, cliente = server_socket.accept() 
        print('\n\n-- Conectado por:', cliente)

        # TAMANHO DA SOLICITAÇÃO (1 byte)
        tam_solicitacao_dados = b''
        while len(tam_solicitacao_dados) < 1:
            chunk = con.recv(1 - len(tam_solicitacao_dados))
            if not chunk:
                raise EOFError("Conexão encerrada prematuramente ao ler o tamanho da solicitação.")
            tam_solicitacao_dados += chunk
        tam_solicitacao = int.from_bytes(tam_solicitacao_dados, 'big')
        
        # RECEBIMENTO DA SOLICITAÇÃO
        dados_solicitacao = b''
        while len(dados_solicitacao) < tam_solicitacao:
            chunk = con.recv(tam_solicitacao - len(dados_solicitacao))
            if not chunk:
                raise EOFError("Conexão encerrada prematuramente ao ler a solicitação.")
            dados_solicitacao += chunk

        solicitacao_str = dados_solicitacao.decode('utf-8')
        print(f" Solicitação recebida: '{solicitacao_str}'")

        # VERIFICAÇÃO DO TIPO DE SOLICITAÇÃO E RESPOSTA
        
        if solicitacao_str == LISTAGEM:
            print(" Comando de listagem recebido. Enviando lista em JSON.")
            con.send(b'\x02') 
                       
            json_str = get_lista_arquivos_json()
            json_bytes = json_str.encode('utf-8')
            tam_json = len(json_bytes)

            # ENVIO DO TAMANHO DO JSON (4 bytes)
            tam_dados = tam_json.to_bytes(4, 'big')
            con.send(tam_dados)
            print(f" Tamanho do JSON: {tam_json} bytes.")
            
            # ENVIO DO CONTEÚDO JSON
            con.sendall(json_bytes)
            print(f" JSON de listagem enviado. Total de {len(json_bytes)} bytes.")

        else:
            # DOWNLOAD DE ARQUIVO
            nome_arquivo = solicitacao_str
            if not os.path.exists(nome_arquivo) or not os.path.isfile(nome_arquivo):
                print(f" Arquivo '{nome_arquivo}' não encontrado.")
                con.send(b'\x00') 
            else:
                print(f" Arquivo '{nome_arquivo}' encontrado. Iniciando envio.")
                con.send(b'\x01') 
                tam_arquivo = os.path.getsize(nome_arquivo)
                
                # ENVIO DO TAMANHO DO ARQUIVO (4 bytes)
                tam_dados = tam_arquivo.to_bytes(4, 'big')
                con.send(tam_dados)
                print(f" Tamanho do arquivo: {tam_arquivo} bytes.")
                
                # ENVIO DO CONTEÚDO DO ARQUIVO
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