import requests

# Função para Obter o Chat_id (útil para logs ou inicialização)
def get_chat_id(token):
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data['result']:
            for update in reversed(data['result']):
                if 'message' in update and 'chat' in update['message']:
                    return update['message']['chat']['id']
        return None
    except Exception as e:
        print(f"Erro ao obter chat_id: {e}")
        return None

# Função para enviar mensagem via POST
def send_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    try:
        response = requests.post(url, data)
        response.raise_for_status()
        print("Mensagem enviada com sucesso!")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar mensagem: {e}")

# Menu Início
msg_inicial = (
    'Olá, Seja Bem-Vindo ao Natanael/Tamires_Bot!\n\n'
    'Comandos Disponíveis (Use espaço para separar os argumentos):\n\n'
    '/agentes -> Lista IPs com agentes.\n'
    '/procs [IP] -> Lista processos na máquina.\n'
    '/proc [IP] [PID] -> Info detalhada de um processo.\n'
    '/topcpu [IP] -> Top 5 processos (CPU).\n'
    '/topmem [IP] -> Top 5 processos (Memória).\n'
    '/histcpu [IP] -> Histórico de CPU (último minuto).\n'
    '/hardw [IP] -> Informações de Hardware.\n'
    '/eval [IP] -> Análise crítica via LLM.'
)

# Função principal de resposta com split por espaços
def responder(token, chat_id, mensagem):
    # Divide a mensagem por espaços (ex: "/procs 192.168.0.1" vira ["/procs", "192.168.0.1"])
    partes = mensagem.split()
    
    if not partes:
        return

    comando = partes[0].lower()

    if comando == "/agentes":
        resposta = "Buscando IPs das máquinas com agentes instalados..."
        
    elif comando == "/procs":
        if len(partes) > 1:
            ip = partes[1]
            resposta = f"Listando processos, PIDs e nomes da máquina no IP: {ip}."
        else:
            resposta = "Erro: Informe o IP. Exemplo: /procs 192.168.1.10"

    elif comando == "/proc":
        if len(partes) > 2:
            ip, pid = partes[1], partes[2]
            resposta = f"Analisando processo {pid} no IP {ip}: Memória (MB) e CPU (%)."
        else:
            resposta = "Erro: Informe o IP e o PID. Exemplo: /proc 192.168.1.10 4500"

    elif comando == "/topcpu":
        if len(partes) > 1:
            ip = partes[1]
            resposta = f"Coletando os 5 processos que mais usam CPU no IP: {ip}."
        else:
            resposta = "Erro: Informe o IP. Exemplo: /topcpu 192.168.1.10"

    elif comando == "/topmem":
        if len(partes) > 1:
            ip = partes[1]
            resposta = f"Coletando os 5 processos que mais usam memória no IP: {ip}."
        else:
            resposta = "Erro: Informe o IP. Exemplo: /topmem 192.168.1.10"

    elif comando == "/histcpu":
        if len(partes) > 1:
            ip = partes[1]
            resposta = f"Gerando histórico de CPU (último minuto) para o IP: {ip}."
        else:
            resposta = "Erro: Informe o IP. Exemplo: /histcpu 192.168.1.10"

    elif comando == "/hardw":
        if len(partes) > 1:
            ip = partes[1]
            resposta = f"Obtendo especificações de Hardware para o IP: {ip}."
        else:
            resposta = "Erro: Informe o IP. Exemplo: /hardw 192.168.1.10"

    elif comando == "/eval":
        if len(partes) > 1:
            ip = partes[1]
            resposta = f"Solicitando análise de IA (LLM) para o status da máquina {ip}..."
        else:
            resposta = "Erro: Informe o IP. Exemplo: /eval 192.168.1.10"

    else:
        resposta = msg_inicial

    send_message(token, chat_id, resposta)

# Loop Principal
def main():
    token = ''
    url = f"https://api.telegram.org/bot{token}/"
    offset = 0

    print("Bot iniciado...")

    while True:
        try:
            # Uso do offset para evitar ler a mesma mensagem várias vezes
            resp = requests.get(url + f"getUpdates?offset={offset}", timeout=10).json()

            if resp.get('result'):
                for update in resp['result']:
                    if 'message' in update and 'text' in update['message']:
                        msg_recebida = update['message']['text']
                        chat_id = update['message']['chat']['id']
                        
                        responder(token, chat_id, msg_recebida)
                        
                        # Atualiza o offset para a próxima mensagem
                        offset = update['update_id'] + 1
        except Exception as e:
            print(f"Erro no loop principal: {e}")

if __name__ == "__main__":
    main()