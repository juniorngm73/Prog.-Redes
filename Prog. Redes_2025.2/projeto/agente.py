import socket, psutil, json, struct, sys, time

def info_hardware():
    try:
        freq = psutil.cpu_freq()
        return {
            "cpu_count": psutil.cpu_count(logical=True),
            "cpu_freq_mhz": freq.current if freq else "N/A",
            "mem_total_mb": psutil.virtual_memory().total // (1024**2),
            "disk_total_gb": psutil.disk_usage('/').total // (1024**3),
            "boot_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(psutil.boot_time()))
        }
    except: return {"erro": "Falha no hardware"}

def processar_requisicoes(s):
    psutil.cpu_percent(interval=None)
    while True:
        try:
            cmd_bytes = s.recv(1)
            if not cmd_bytes: break
            cmd = cmd_bytes.decode('utf-8')
            response_data = None

            if cmd == 'G': # Listar Processos
                lista = []
                for p in psutil.process_iter(['pid', 'name']):
                    try: lista.append({"pid": p.info['pid'], "nome": p.info['name']})
                    except: continue
                response_data = lista

            elif cmd == 'P': # Detalhes de Processo
                pid_bytes = s.recv(4)
                if len(pid_bytes) < 4: continue
                pid = struct.unpack('>I', pid_bytes)[0]
                try:
                    p = psutil.Process(pid)
                    with p.oneshot():
                        conns = [{"remote": c.raddr.ip, "status": c.status} for c in p.net_connections(kind='tcp') if c.raddr]
                        response_data = {
                            "ok": True, "pid": pid, "nome": p.name(),
                            "path": p.exe() if hasattr(p, 'exe') else "N/A",
                            "mem": p.memory_info().rss // (1024**2),
                            "cpu": p.cpu_percent(interval=0.1), "connections": conns
                        }
                except: response_data = {"ok": False}

            elif cmd == 'C': # Top 5 CPU
                procs = []
                for p in psutil.process_iter(['pid', 'cpu_percent']):
                    try: procs.append(p.info)
                    except: continue
                response_data = sorted(procs, key=lambda x: x['cpu_percent'], reverse=True)[:5]

            elif cmd == 'M': # Top 5 Memória
                procs = []
                for p in psutil.process_iter(['pid', 'memory_percent']):
                    try: procs.append(p.info)
                    except: continue
                response_data = [{"pid": i['pid'], "perc": round(i['memory_percent'], 2)} for i in sorted(procs, key=lambda x: x['memory_percent'], reverse=True)[:5]]

            elif cmd == 'H': # Hardware
                response_data = info_hardware()

            if response_data is not None:
                payload = json.dumps(response_data).encode('utf-8')
                s.sendall(struct.pack('>I', len(payload)))
                s.sendall(payload)
        except: break

if __name__ == "__main__":
    if len(sys.argv) < 2: print("Uso: python agente.py <IP_GERENTE>")
    else:
        while True:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((sys.argv[1], 45678))
                    print("Conectado.")
                    processar_requisicoes(s)
            except: time.sleep(5)