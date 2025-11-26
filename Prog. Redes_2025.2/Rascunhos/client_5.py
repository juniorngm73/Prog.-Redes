import socket
import struct
import sys

HOST = 'localhost' # IP do servidor
PORT = 50000       # Porta do servidor
SERVER_ADDRESS = (HOST, PORT)

# Formato: 1 byte (Unsigned Char) para o tamanho do nome
FORMATO_TAMANHO_NOME = '!B' 
TAMANHO_DO_CABECALHO = struct.calcsize(FORMATO_TAMANHO_NOME) # 1 byte

# Criando o socket UDP
socketCliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print(f"Cliente UDP iniciado. Enviando tamanho do nome em {TAMANHO_DO_CABECALHO} byte.")

while True:
    try:
        # --- 1. PREPARANDO O ENVIO ---
        
        nome_arquivo = input('Digite o nome do arquivo (máx. 255 caracteres, ou "exit" para sair): ')
        
        if nome_arquivo.lower() == "exit":
            break
            
        # Converte o nome do arquivo para bytes
        nome_arquivo_bytes = nome_arquivo.encode('utf-8')
        
        # Obtém o tamanho como um inteiro (NECESSÁRIO para empacotar)
        tam_nome = len(nome_arquivo_bytes) 
        
        # Restrição de 1 byte: o nome não pode ter mais de 255 bytes.
        if tam_nome > 255:
             print("Erro: O nome do arquivo excede o limite de 255 bytes.")
             continue
             
        # Converte o inteiro 'tam_nome' em 1 byte binário usando to_bytes() (via struct.pack)
        tamanho_nome_binario = struct.pack(FORMATO_TAMANHO_NOME, tam_nome)
        
        # Concatena o datagrama: [1 byte de tamanho] + [Nome do Arquivo]
        mensagem_envio = tamanho_nome_binario + nome_arquivo_bytes
        
        print(f"Enviando {tam_nome} bytes de nome. Total: {len(mensagem_envio)} bytes.")

        # --- 2. ENVIANDO O DATAGRAMA ---
        socketCliente.sendto(mensagem_envio, SERVER_ADDRESS)

        # --- 3. RECEBENDO A RESPOSTA DO SERVIDOR ---
        dados_recebidos, servidor = socketCliente.recvfrom(1024) 
        
        # Decodifica a resposta
        resposta = dados_recebidos.decode('utf-8')
        print(f'\n<< Resposta do Servidor ({servidor[0]}:{servidor[1]}):\n>> {resposta}')
        
        if "não encontrado" in resposta.lower() or "encerrando" in resposta.lower():
             print("\nConexão encerrada pelo Servidor.")
             break
        
    except struct.error as e:
        print(f"Erro ao empacotar/desempacotar dados: {e}")
        continue
    except socket.error as e:
        print(f"Erro no socket: {e}")
        break
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        break

print("\nEncerrando o Cliente.")
socketCliente.close()