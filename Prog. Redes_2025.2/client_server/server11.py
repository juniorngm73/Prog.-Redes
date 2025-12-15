import socket, os, json

HOST = ''
PORT = 20000
BUFFER_SIZE = 4096
LISTAGEM = 'Listar_Arquivos'
UPLOAD_CMD = 'Upload_Arquivo' # Novo comando para upload

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f' Servidor TCP escutando em {HOST}:{PORT}...')
except Exception as e:
    print(f" Erro ao iniciar o servidor: {e}")
    exit()

def get_lista_arquivos_json():
    # ... (Função de Listagem existente) ...
    arquivos_info = []

    for f in os.listdir('.'):

        if os.path.isfile(f) and f not in ('servidor.py', 'cliente.py'): # Excluindo os próprios scripts
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
            # ... (Lógica de Listagem existente) ...
            print(" Comando de listagem recebido. Enviando lista em JSON.")
            con.send(b'\x02') # Status 2 = Enviando JSON

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

        elif solicitacao_str.startswith(UPLOAD_CMD + ':'): # LÓGICA DE UPLOAD
            _, nome_arquivo_servidor = solicitacao_str.split(':', 1)
            print(f" Comando de upload recebido. Arquivo alvo: '{nome_arquivo_servidor}'")
            
            con.send(b'\x03') # Status 3 = Pronto para receber metadados de upload
            
            try:
                # RECEBIMENTO DO TAMANHO DO ARQUIVO (4 bytes)
                tam_arquivo_dados = b''
                while len(tam_arquivo_dados) < 4:
                    chunk = con.recv(4 - len(tam_arquivo_dados))
                    if not chunk:
                        raise EOFError("Conexão encerrada antes de receber o tamanho do arquivo.")
                    tam_arquivo_dados += chunk
                tam_arquivo = int.from_bytes(tam_arquivo_dados, 'big')
                print(f" Tamanho total do arquivo a receber: {tam_arquivo} bytes.")

                # RECEBIMENTO DO CONTEÚDO DO ARQUIVO
                bytes_recebidos = 0
                with open(nome_arquivo_servidor, 'wb') as f: # Salva com o nome original
                    while bytes_recebidos < tam_arquivo:
                        data = con.recv(min(BUFFER_SIZE, tam_arquivo - bytes_recebidos))
                        if not data:
                            break
                        f.write(data)
                        bytes_recebidos += len(data)
                
                if bytes_recebidos == tam_arquivo:
                    print(f" Upload de '{nome_arquivo_servidor}' completo. Total de {bytes_recebidos} bytes salvos.")
                    con.send(b'\x04') # Status 4 = Sucesso no Upload
                else:
                    print(f" Upload incompleto. Esperado: {tam_arquivo}, Recebido: {bytes_recebidos}.")
                    con.send(b'\x05') # Status 5 = Falha no Upload
                    # Tenta remover arquivo incompleto
                    try:
                        os.remove(nome_arquivo_servidor)
                    except OSError:
                        pass
                        
            except Exception as e:
                print(f" Erro durante o recebimento do arquivo de upload: {e}")
                con.send(b'\x05') # Status 5 = Falha no Upload
                # Tenta remover arquivo incompleto
                try:
                    os.remove(nome_arquivo_servidor)
                except OSError:
                    pass

        else:
            # DOWNLOAD DE ARQUIVO (Lógica existente)
            nome_arquivo = solicitacao_str
            if not os.path.exists(nome_arquivo) or not os.path.isfile(nome_arquivo):
                print(f" Arquivo '{nome_arquivo}' não encontrado.")
                con.send(b'\x00') # Status 0 = Arquivo não encontrado
            else:
                print(f" Arquivo '{nome_arquivo}' encontrado. Iniciando envio.")
                con.send(b'\x01') # Status 1 = Enviando arquivo
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
                        if not chunk:
                            break
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