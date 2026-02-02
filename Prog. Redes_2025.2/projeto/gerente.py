import socket
import threading
import requests
import time
from funcoes_bot import processar_comando

# Dicionário global para rastrear agentes ativos { IP: socket }
agentes_ativos = {}

# CONFIGURAÇÕES - Preencha com seus dados
TOKEN_TELEGRAM = ''

def bot_loop():
    """Loop para buscar atualizações do Telegram a cada 1s (conforme pedido)"""
    last_update_id = 0
    print("[BOT] Sistema de monitoramento via Telegram iniciado.")
    
    while True:
        try:
            # timeout=10 ajuda a não sobrecarregar a rede, mas o sleep(1) no final garante o requisito
            url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/getUpdates?offset={last_update_id + 1}&timeout=5"
            response = requests.get(url, timeout=10)
            r = response.json()

            if r.get("ok") and r.get("result"):
                for update in r["result"]:
                    last_update_id = update["update_id"]
                    
                    if "message" in update and "text" in update["message"]:
                        chat_id = update["message"]["chat"]["id"]
                        texto = update["message"]["text"]
                        
                        print(f"[BOT] Comando recebido: {texto}")
                        
                        # Processamento do comando
                        try:
                            resposta = processar_comando(texto, agentes_ativos)
                        except Exception as e:
                            resposta = f"Erro interno ao processar comando: {e}"
                        
                        # Envio da resposta ao usuário
                        requests.post(
                            f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage", 
                            json={"chat_id": chat_id, "text": str(resposta)},
                            timeout=5
                        )
        except Exception as e:
            print(f"[ERRO BOT] Falha na comunicação com Telegram: {e}")
        
        time.sleep(1) # Requisito: buscar pedidos a cada 1s

def handle_agente(conn, addr):
    """Thread dedicada para cada agente conectado"""
    ip_cliente = addr[0]
    print(f"[REDE] Nova conexão: Agente em {addr}")
    
    # Adiciona ao dicionário de agentes ativos
    agentes_ativos[ip_cliente] = conn
    
    try:
        # Mantém a thread viva enquanto o socket estiver aberto
        # O recv(1, MSG_PEEK) verifica se a conexão caiu sem remover dados do buffer
        while True:
            # Sockets em modo bloqueante esperam aqui
            data = conn.recv(1, socket.MSG_PEEK)
            if not data:
                break 
            time.sleep(2) # Verifica integridade a cada 2s
    except (ConnectionResetError, BrokenPipeError, socket.error):
        print(f"[REDE] Conexão perdida abruptamente com {ip_cliente}")
    finally:
        print(f"[REDE] Removendo agente: {ip_cliente}")
        if ip_cliente in agentes_ativos:
            del agentes_ativos[ip_cliente]
        conn.close()

def main():
    # Inicia o bot em uma thread separada
    thread_bot = threading.Thread(target=bot_loop, daemon=True)
    thread_bot.start()
    
    # Configuração do Socket Servidor para os Agentes
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Permite reutilizar a porta caso o programa seja reiniciado rapidamente
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('0.0.0.0', 45678))
        server.listen(10)
        print(f"[GERENTE] Ouvindo agentes na porta 45678...")
        
        while True:
            conn, addr = server.accept()
            # Cria uma thread para manter a conexão com o agente
            # Conforme o enunciado: "Deve manter uma thread aberta com cada agente"
            thread_agente = threading.Thread(target=handle_agente, args=(conn, addr), daemon=True)
            thread_agente.start()
            
    except Exception as e:
        print(f"[ERRO CRÍTICO] Falha no servidor TCP: {e}")
    finally:
        server.close()

if __name__ == "__main__":
    main()