import struct, json, requests

GEMINI_API_KEY = 

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
    # Alterado para v1beta que costuma ser mais permissiva com modelos novos
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    
    # Payload estruturado rigorosamente conforme a documentação
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
        
        # Log de depuração (opcional, remova depois)
        if r.status_code != 200:
            return f"Erro API ({r.status_code}): {res_json.get('error', {}).get('message', 'Erro desconhecido')}"

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

    if cmd == "/agentes":
        if not agentes: return "Nenhum agente online."
        return "Agentes online:\n" + "\n".join(agentes.keys())

    if len(partes) < 2: return f"Uso: {cmd} <IP>"
    ip = partes[1]
    if ip not in agentes: return f"Agente {ip} não encontrado."
    sock = agentes[ip]

    if cmd == "/procs":
        data = solicitar_agente(sock, 'G')
        if not data: return "Falha ao obter processos."
        lista = [f"{p['pid']}: {p['nome']}" for p in data[:15]]
        return "Lista de Processos:\n" + "\n".join(lista)

    elif cmd == "/topcpu":
        data = solicitar_agente(sock, 'C')
        if not data: return "Erro no Top CPU."
        return "Top 5 CPU:\n" + "\n".join([f"PID {p['pid']}: {p['perc']}%" for p in data])

    elif cmd == "/hardw":
        d = solicitar_agente(sock, 'H')
        if not d: return "Erro no Hardware."
        return f"Hardware {ip}:\nCores: {d['cpu_count']}\nRAM: {d['mem_total_mb']} MB\nDisco: {d['disk_total_gb']} GB"

    elif cmd == "/eval":
        h = solicitar_agente(sock, 'H')
        c = solicitar_agente(sock, 'C')
        m = solicitar_agente(sock, 'M')
        prompt = f"Analise esta máquina: Hardware {h}, CPU {c}, Memória {m}. Ela está saudável? Responda em português, técnico e curto."
        return f"Avaliação Gemini:\n{chamada_gemini(prompt)}"

    return "Comando desconhecido."