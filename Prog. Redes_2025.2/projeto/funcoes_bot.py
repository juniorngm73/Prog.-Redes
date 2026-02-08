import struct, json, requests

GEMINI_API_KEY = ''

def solicitar_agente(sock, comando, params=None):
    try:
        # Envia o caractere do comando (1 byte)
        sock.sendall(comando.encode('utf-8'))
        
        # Se for o comando 'P', envia o PID (4 bytes Big Endian)
        if comando == 'P' and params:
            sock.sendall(struct.pack('>I', int(params)))
        
        # Recebe o tamanho da resposta (4 bytes Big Endian)
        size_bytes = sock.recv(4)
        if not size_bytes or len(size_bytes) < 4: 
            return None
            
        size = struct.unpack('>I', size_bytes)[0]
        
        # Buffer para garantir o recebimento do JSON completo
        data = b""
        while len(data) < size:
            packet = sock.recv(size - len(data))
            if not packet: break
            data += packet
            
        return json.loads(data.decode('utf-8'))
    except Exception as e:
        print(f"Erro na comunicação: {e}")
        return None

def chamada_gemini(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=10)
        return r.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "Erro ao consultar a LLM via API."

def processar_comando(texto, agentes):
    partes = texto.split()
    if not partes: return "Comando vazio."
    
    cmd = partes[0].lower()

    # listagem dos IPs registrados no Gerente
    if cmd == "/agentes":
        if not agentes: return "Nenhum agente conectado no momento."
        
        lista_ips = []
        for ip_key in agentes.keys():
            lista_ips.append(ip_key)
        return " Agentes online:\n" + "\n".join(lista_ips)

    # Comandos que exigem IP
    if len(partes) < 2:
        return f"Uso: {cmd} <IP>"
    
    ip = partes[1]
    if ip not in agentes:
        return f"O agente com IP {ip} não está na lista de ativos."
    
    sock = agentes[ip]

    if cmd == "/procs":
        data = solicitar_agente(sock, 'G')
        if not data: return "Falha ao obter processos."
        
        lista_formatada = []
        contador = 0
        for p in data:
            if contador < 15:
                lista_formatada.append(f"{p['pid']}: {p['nome']}")
                contador += 1
        
        return " Lista de Processos:\n" + "\n".join(lista_formatada) + f"\n... (Total: {len(data)})"

    elif cmd == "/proc":
        if len(partes) < 3: return "Uso: /proc <IP> <PID>"
        data = solicitar_agente(sock, 'P', partes[2])
        if not data or not data.get("ok"): return "Processo não encontrado no agente."
        return (f" Detalhes PID {data['pid']}:\n"
                f"Nome: {data['nome']}\nCPU: {data['cpu']}%\n"
                f"Mem: {data['mem']} MB\nCaminho: {data['path']}")

    elif cmd == "/topcpu":
        data = solicitar_agente(sock, 'C')
        if not data: return "Erro ao obter Top CPU."
        
        lista_cpu = []
        for p in data:
            lista_cpu.append(f"PID {p['pid']}: {p['perc']}%")
        return " Top 5 CPU:\n" + "\n".join(lista_cpu)

    elif cmd == "/topmem":
        data = solicitar_agente(sock, 'M')
        if not data: return "Erro ao obter Top Memória."
        
        lista_mem = []
        for p in data:
            lista_mem.append(f"PID {p['pid']}: {p['perc']}%")
        return " Top 5 Memória:\n" + "\n".join(lista_mem)

    elif cmd == "/hardw":
        data = solicitar_agente(sock, 'H')
        if not data: return "Erro ao obter Hardware."
        return (f" Hardware em {ip}:\n"
                f"Cores: {data['cpu_count']}\nRAM: {data['mem_total_mb']} MB\n"
                f"Disco: {data['disk_total_gb']} GB Livres\nOS: {data['boot_time']}")

    elif cmd == "/histcpu":
        data = solicitar_agente(sock, 'G')
        if not data: return "Erro ao coletar dados."
        
        lista_hist = []
        contador = 0
        for p in data:
            if contador < 10:
                lista_hist.append(p['nome'])
                contador += 1
        return " Histórico (Última amostra):\n" + "\n".join(lista_hist)

    elif cmd == "/eval":
        h = solicitar_agente(sock, 'H')
        c = solicitar_agente(sock, 'C')
        m = solicitar_agente(sock, 'M')
        prompt = f"Analise o estado desta máquina: Hardware {h}, Top CPU {c}, Top Memória {m}. Ela está saudável? Responda em português de forma técnica e curta."
        return f" Avaliação Gemini:\n{chamada_gemini(prompt)}"

    return "Comando desconhecido."