import struct, json, requests

GEMINI_API_KEY = ''

def solicitar_agente(sock, comando, params=None):
    try:
        sock.sendall(comando.encode('utf-8'))
        if comando == 'P' and params:
            sock.sendall(struct.pack('>I', int(params)))
        
        size_bytes = sock.recv(4)
        if not size_bytes or len(size_bytes) < 4: return None
        size = struct.unpack('>I', size_bytes)[0]
        
        data = b""
        while len(data) < size:
            packet = sock.recv(size - len(data))
            if not packet: break
            data += packet
        return json.loads(data.decode('utf-8'))
    except: return None

def chamada_gemini(prompt):
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }
    
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=15)
        res_json = r.json()
        
        if r.status_code != 200:
            msg_erro = res_json.get('error', {}).get('message', 'Erro desconhecido')
            return f"Erro API ({r.status_code}): {msg_erro}"

        if 'candidates' in res_json and len(res_json['candidates']) > 0:
            return res_json['candidates'][0]['content']['parts'][0]['text']
        else:
            return "O modelo não retornou uma resposta válida."
            
    except Exception as e:
        return f"Erro ao consultar a LLM: {e}"

def processar_comando(texto, agentes):
    partes = texto.split()
    if not partes: return "Comando vazio."
    cmd = partes[0].lower()

    # Comando /start
    if cmd == "/start":
        return ("**Comandos disponíveis:**\n\n"
                "/start - Lista de comandos\n"
                "/agentes - Lista os agentes online\n"
                "/procs <IP> - Lista processos ativos\n"
                "/proc <IP> <PID> - Detalhes de um processo\n"
                "/topcpu <IP> - Top 5 processos por CPU\n"
                "/topmem <IP> - Top 5 processos por Memória\n"
                "/hardw <IP> - Informações de Hardware\n"
                "/histcpu <IP> - Amostra de histórico de CPU\n"
                "/eval <IP> - Avaliação de saúde via Gemini AI")

    # Comando /agentes
    if cmd == "/agentes":
        if not agentes: return "Nenhum agente conectado no momento."
        
        lista_ips = ""
        for ip_chave in agentes.keys():
            lista_ips += ip_chave + "\n"
        return " Agentes online:\n" + lista_ips

    # Comandos que Solicitam IP 
    if len(partes) < 2:
        return f"Uso: {cmd} <IP>"
    
    ip = partes[1]
    if ip not in agentes:
        return f"O agente com IP {ip} não está na lista de ativos."
    
    sock = agentes[ip]

    # /procs
    if cmd == "/procs":
        data = solicitar_agente(sock, 'G')
        if not data: return "Falha ao obter processos."
        
        lista_formatada = []
        
        for p in data[:15]:
            lista_formatada.append(f"{p['pid']}: {p['nome']}")
        
        return "Lista de Processos:\n" + "\n".join(lista_formatada) + f"\n... (Total: {len(data)})"

    # /proc
    elif cmd == "/proc":
        if len(partes) < 3: return "Uso: /proc <IP> <PID>"
        data = solicitar_agente(sock, 'P', partes[2])
        if not data or not data.get("ok"): return "Processo não encontrado no agente."
        return (f" Detalhes PID {data['pid']}:\n"
                f"Nome: {data['nome']}\nCPU: {data['cpu']}%\n"
                f"Mem: {data['mem']} MB\nCaminho: {data['path']}")

    # /topcpu
    elif cmd == "/topcpu":
        data = solicitar_agente(sock, 'C')
        if not data: return "Erro ao obter Top CPU."
        
        linhas = []
        for p in data:
            
            valor = p.get('perc', p.get('cpu_percent'))
            linhas.append(f"PID {p['pid']}: {valor}%")
        
        return " Top 5 CPU:\n" + "\n".join(linhas)

    # /topmem
    elif cmd == "/topmem":
        data = solicitar_agente(sock, 'M')
        if not data: return "Erro ao obter Top Memória."
        
        linhas = []
        for p in data:
            valor = p.get('perc', p.get('memory_percent'))
            linhas.append(f"PID {p['pid']}: {valor}%")
            
        return " Top 5 Memória:\n" + "\n".join(linhas)

    # /hardw
    elif cmd == "/hardw":
        data = solicitar_agente(sock, 'H')
        if not data: return "Erro ao obter Hardware."
        return (f" Hardware em {ip}:\n"
                f"Cores: {data['cpu_count']}\nRAM: {data['mem_total_mb']} MB\n"
                f"Disco: {data['disk_total_gb']} GB Livres\nOS: {data['boot_time']}")

    # /histcpu
    elif cmd == "/histcpu":
        data = solicitar_agente(sock, 'G')
        if not data: return "Erro ao obter dados."
        
        amostra = []
        for p in data[:10]:
            amostra.append(p['nome'])
            
        return " Histórico (Última amostra):\n" + "\n".join(amostra)

    # /eval
    elif cmd == "/eval":
        h = solicitar_agente(sock, 'H')
        c = solicitar_agente(sock, 'C')
        m = solicitar_agente(sock, 'M')
        if not h: return "Erro: Falha ao coletar dados do agente para o Gemini."
        
        prompt = f"Analise o estado desta máquina: Hardware {h}, Top CPU {c}, Top Memória {m}. Ela está saudável? Responda em português de forma técnica e curta."
        return f" Avaliação Gemini:\n{chamada_gemini(prompt)}"

    return "Comando desconhecido."