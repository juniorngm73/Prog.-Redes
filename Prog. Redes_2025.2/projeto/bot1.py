import requests

# Função para Obter o Chat_id

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
    except requests.exceptions.RequestException as e:
        print(f"Error getting updates: {e}")
        return None
    except (KeyError, TypeError) as e:
        print(f"Error parsing updates: {e}. Raw data: {data}")
        return None

# Função para enviar mensagem

def send_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    try:
        response = requests.post(url, data)
        response.raise_for_status()
        print("Message sent successfully!")

    except requests.exceptions.RequestException as e:
        print(f"Error sending message: {e}")



msg = ('Olá, Seja Bem Vindo ao Juniorngm_Bot/Tamires_Bot !\n\n'
                           ' Comandos Possíveis:\n\n'
                           '/agentes --> Apresenta os IPs das máquinas em que existem agentes de monitoramento instalados.\n'
                           '/procs --> Recebe um IP (seguindo o comando, separado por espaço ) e lista o número de processos, o pid e o nome dos processos executando nessa máquina.\n'
                           '/proc --> Recebe um IP e um PID (seguindo o comando, separados por espaço) e lista informações sobre o processo na máquina, como: o pid, o nome o uso de memória (em MB) e o uso da CPU (em percentual);.\n'
                           '/topcpu --> Recebe um IP e lista os cinco processos que mais estão usando a CPU na máquina, bem como os percentuais.\n'
                           '/topmem --> Recebe um IP (seguindo o comando, separado por espaço) e lista os cinco processos que mais estão usando memória na máquina (bem como o valor usado).\n'
                           '/histcpu --> Recebe um IP e lista os dez processos que mais usaram a CPU no último minuto, sendo uma coleta a cada 5 segundos;.\n'
                           '/hardw --> Recebe um IP e mostra informações sobre o hardware da máquina.\n'
                           '/eval --> Recebe um IP e devolve o resultado de análise da situação da máquina por uma LLM (gemini, por exemplo). Nesse procedimento, envie as informações similares àquelas obtidas em /topmem, /topcpu e /hardw e solicite a avaliação à LLM – a resposta dela deve ser devolvida ao usuário. USAR REQUESTS PARA EFETUAR ESSA OPERAÇÃO JUNTO A UMA LLM.\n'
                        )
                          



# Função para responder às mensagens
def responder(token, chat_id, mensagem):
    if "/agentes" in mensagem:
        resposta = "Apresenta os IPs das máquinas em que existem agentes de monitoramento instalados."
    elif "/procs" in mensagem:
        ip = mensagem.split(":")[1]
        resposta = f"Recebe um IP (seguindo o comando, separado por espaço ) e lista o número de processos, o pid e o nome dos processos executando nessa máquina. {ip}."
    elif "/proc" in mensagem:
        resposta = "Recebe um IP e um PID (seguindo o comando, separados por espaço) e lista informações sobre o processo na máquina, como: o pid, o nome o uso de memória (em MB) e o uso da CPU (em percentual)"
    elif "/topcpu" in mensagem:
        ip = mensagem.split(":")[1]
        resposta = f"Recebe um IP e lista os cinco processos que mais estão usando a CPU na máquina, bem como os percentuais {ip}."
    elif "/topmen" in mensagem:
        resposta = "Recebe um IP (seguindo o comando, separado por espaço) e lista os cinco processos que mais estão usando memória na máquina (bem como o valor usado)"
    elif "/histcpu" in mensagem:
        ip = mensagem.split(":")[1]
        resposta = f" Recebe um IP e lista os dez processos que mais usaram a CPU no último minuto, sendo uma coleta a cada 5 segundos {ip}."
    elif "/hardw" in mensagem:
        resposta = "Recebe um IP e mostra informações sobre o hardware da máquina {ip}"
    elif "/eval" in mensagem:
        ip = mensagem.split(":")[1]
        resposta = f" Recebe um IP e devolve o resultado de análise da situação da máquina por uma LLM (gemini, por exemplo). Nesse procedimento, envie as informações similares àquelas obtidas em /topmem, /topcpu e /hardw e solicite a avaliação à LLM – a resposta dela deve ser devolvida ao usuário. USAR REQUESTS PARA EFETUAR ESSA OPERAÇÃO JUNTO A UMA LLM.{ip}."
    else:
        resposta = msg

    send_message(token, chat_id, resposta)

# Loop principal para receber e responder mensagens
def main():
    token = ''
    url = f"https://api.telegram.org/bot{token}/"

    while True:
        updates = requests.get(url + "getUpdates").json()

        if updates['result']:
            for update in updates['result']:
                if 'message' in update and 'text' in update['message']:
                    mensagem = update['message']['text']
                    chat_id = update['message']['chat']['id']

                    responder(token, chat_id, mensagem)

                    # Atualiza o offset para não receber as mesmas mensagens novamente
                    update_id = update['update_id']
                    requests.get(url + f"getUpdates?offset={update_id + 1}")


if __name__ == "__main__":
    main()