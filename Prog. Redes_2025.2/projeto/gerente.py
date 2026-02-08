import socket, threading, requests, time, funcoes_bot

# Dicionário global para rastrear agentes ativos { IP: socket }
agentes_ativos = {}

TOKEN_TELEGRAM = ''

def bot_loop():
    # Atualizações do Telegram 
    atualizacao_id = 0
        
    try:
        url_limpeza = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/getUpdates"
        res = requests.get(url_limpeza, params={"timeout": 0}, timeout=10).json()
        if res.get("ok") and res.get("result"):
            atualizacao_id = res["result"][-1]["update_id"]
           # print(f"[BOT] {len(res['result'])} mensagens antigas ignoradas.")
    except Exception as e:
        print(f"[BOT] Erro na limpeza: {e}")
    
    print("[BOT] Sistema de monitoramento pronto e aguardando novos comandos.")
    
    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/getUpdates"
            params = {"offset": atualizacao_id + 1, "timeout": 10}
            
            response = requests.get(url, params=params, timeout=15)
            r = response.json()

            if r.get("ok") and r.get("result"):
                for update in r["result"]:
                    atualizacao_id = update["update_id"]
                    
                    if "message" in update and "text" in update["message"]:
                        chat_id = update["message"]["chat"]["id"]
                        texto = update["message"]["text"]
                        
                        # LOGS DE COMANDO RESTAURADOS
                        print(f"[BOT] Processando comando: '{texto}' de Chat ID: {chat_id}")
                        
                        resposta = funcoes_bot.processar_comando(texto, agentes_ativos)
                        
                        send_url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
                        send_payload = {"chat_id": chat_id, "text": str(resposta)}
                        requests.post(send_url, json=send_payload, timeout=10)
            
        except Exception as e:
            print(f"[ERRO BOT]: {e}")
            time.sleep(2)

def atender_agente(conn, addr):
    ip_cliente = addr[0]
    print(f"[REDE] Nova conexão: Agente em {addr}")
    agentes_ativos[ip_cliente] = conn
    
    try:
        while True:
            # Detecta se a conexão caiu
            if not conn.recv(1, socket.MSG_PEEK):
                break
            time.sleep(5) 
    except Exception:
        pass
    finally:
        print(f"[REDE] Removendo agente: {ip_cliente}")
        agentes_ativos.pop(ip_cliente, None)
        conn.close()

def main():
    thread_bot = threading.Thread(target=bot_loop, daemon=True)
    thread_bot.start()
    
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('0.0.0.0', 45678))
        server.listen(10)
        print(f"[GERENTE] Ouvindo agentes na porta 45678...")
        
        while True:
            conn, addr = server.accept()
            thread_agente = threading.Thread(target=atender_agente, args=(conn, addr), daemon=True)
            thread_agente.start()
            
    except Exception as e:
        print(f"[ERRO CRÍTICO] Falha no servidor TCP: {e}")
    finally:
        server.close()

if __name__ == "__main__":
    main()