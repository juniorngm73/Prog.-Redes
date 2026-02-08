import socket, psutil, json, struct, sys, time

def info_hardware():
    freq = psutil.cpu_freq()
    if freq:
        freq_atual = freq.current
    else:
        freq_atual = "N/A"

    return {
        "cpu_count": psutil.cpu_count(logical=True),
        "cpu_freq_mhz": freq_atual,
        "mem_total_mb": psutil.virtual_memory().total // (1024**2),
        "disk_total_gb": psutil.disk_usage('/').total // (1024**3),
        "boot_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(psutil.boot_time()))
    }

def processar_requisicoes(s):
    psutil.cpu_percent(interval=None)
    
    while True:
        try:
            # Recebe o comando (1 byte)
            cmd_bytes = s.recv(1)
            if not cmd_bytes:
                break
            cmd = cmd_bytes.decode('utf-8')
            
            response_data = None

            if cmd == 'G': # Listar Processos
                lista_procs = []
                for p in psutil.process_iter(['pid', 'name']):
                    lista_procs.append({"pid": p.info['pid'], "nome": p.info['name']})
                response_data = lista_procs
            
            elif cmd == 'P': # Processo Específico
                pid_bytes = s.recv(4)
                if len(pid_bytes) < 4: continue
                pid = struct.unpack('>I', pid_bytes)[0]
                try:
                    p = psutil.Process(pid)
                    with p.oneshot():
                        
                        conns = []
                        for c in p.net_connections(kind='tcp'):
                            if c.raddr:
                                conns.append({"remote": c.raddr.ip, "status": c.status})
                        
                        response_data = {
                            "ok": True,
                            "pid": pid,
                            "nome": p.name(),
                            "path": p.exe(),
                            "mem": p.memory_info().rss // (1024**2),
                            "cpu": p.cpu_percent(interval=0.1),
                            "connections": conns
                        }
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    response_data = {"ok": False}

            elif cmd == 'C': # Top 5 CPU
                procs = []
                for p in psutil.process_iter(['pid', 'cpu_percent']):
                    procs.append(p.info)
                
                top_cpu = sorted(procs, key=lambda x: x['cpu_percent'], reverse=True)[:5]
                
                lista_top_cpu = []
                for item in top_cpu:
                    lista_top_cpu.append({"pid": item['pid'], "perc": item['cpu_percent']})
                response_data = lista_top_cpu

            elif cmd == 'M': # Top 5 Memória
                procs = []
                for p in psutil.process_iter(['pid', 'memory_percent']):
                    procs.append(p.info)
                
                top_mem = sorted(procs, key=lambda x: x['memory_percent'], reverse=True)[:5]
                
                lista_top_mem = []
                for item in top_mem:
                    lista_top_mem.append({"pid": item['pid'], "perc": round(item['memory_percent'], 2)})
                response_data = lista_top_mem

            elif cmd == 'H': # Hardware Informações
                response_data = info_hardware()

            # Envio da resposta [Tamanho 4 bytes] + [JSON]
            if response_data is not None:
                json_payload = json.dumps(response_data).encode('utf-8')
                s.sendall(struct.pack('>I', len(json_payload)))
                s.sendall(json_payload)

        except Exception as e:
            print(f"Erro no processamento: {e}")
            break

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python agente.py <IP_DO_GERENTE>")
    else:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((sys.argv[1], 45678))
                print(f"Agente conectado ao Gerente: {sys.argv[1]}")
                processar_requisicoes(s)
        except ConnectionRefusedError:
            print("Erro: Gerente não encontrado.")
        except Exception as e:
            print(f"Falha: {e}")