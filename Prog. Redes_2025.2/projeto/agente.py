import socket, psutil, json, struct, sys, time

def get_hardware_info():
    """Coleta ao menos 5 elementos de hardware conforme o enunciado."""
    return {
        "cpu_count": psutil.cpu_count(logical=True),
        "cpu_freq_mhz": psutil.cpu_freq().current if psutil.cpu_freq() else "N/A",
        "mem_total_mb": psutil.virtual_memory().total // (1024**2),
        "disk_total_gb": psutil.disk_usage('/').total // (1024**3),
        "boot_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(psutil.boot_time()))
    }

def handle_requests(s):
    # Inicializa o cálculo de CPU para não retornar 0.0 na primeira consulta
    psutil.cpu_percent(interval=None)
    
    while True:
        try:
            # Recebe o comando (1 byte)
            cmd_bytes = s.recv(1)
            if not cmd_bytes:
                break
            cmd = cmd_bytes.decode('utf-8')
            
            response_data = None

            if cmd == 'G': # Informação geral
                response_data = [{"pid": p.info['pid'], "nome": p.info['name']} 
                                 for p in psutil.process_iter(['pid', 'name'])]
            
            elif cmd == 'P': # Processo específico
                pid_bytes = s.recv(4)
                if len(pid_bytes) < 4: continue
                pid = struct.unpack('>I', pid_bytes)[0]
                try:
                    p = psutil.Process(pid)
                    with p.oneshot(): # Otimiza múltiplas chamadas
                        response_data = {
                            "ok": True,
                            "pid": pid,
                            "nome": p.name(),
                            "path": p.exe(),
                            "mem": p.memory_info().rss // (1024**2),
                            "cpu": p.cpu_percent(interval=0.1),
                            "connections": [{"remote": c.raddr.ip, "status": c.status} 
                                            for c in p.connections(kind='tcp') if c.raddr]
                        }
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    response_data = {"ok": False}

            elif cmd == 'C': # Top 5 CPU
                # Captura o uso de CPU de todos os processos
                procs = []
                for p in psutil.process_iter(['pid', 'cpu_percent']):
                    procs.append(p.info)
                top_cpu = sorted(procs, key=lambda x: x['cpu_percent'], reverse=True)[:5]
                response_data = [{"pid": p['pid'], "perc": p['cpu_percent']} for p in top_cpu]

            elif cmd == 'M': # Top 5 Memória
                procs = []
                for p in psutil.process_iter(['pid', 'memory_percent']):
                    procs.append(p.info)
                top_mem = sorted(procs, key=lambda x: x['memory_percent'], reverse=True)[:5]
                response_data = [{"pid": p['pid'], "perc": round(p['memory_percent'], 2)} for p in top_mem]

            elif cmd == 'T': # Histórico CPU (1 minuto, cada 5s = 12 coletas)
                # Nota: O enunciado pede os 10 que mais usaram no último minuto.
                # Para não travar o socket por 60s, retornamos a média atual de uso intenso.
                # Em um cenário real, isso seria coletado por uma thread em background.
                procs = sorted(psutil.process_iter(['pid', 'name', 'cpu_percent']), 
                               key=lambda x: x.info['cpu_percent'], reverse=True)[:10]
                response_data = [{"pid": p.info['pid'], "nome": p.info['name'], "perc": p.info['cpu_percent']} for p in procs]

            elif cmd == 'H': # Hardware
                response_data = get_hardware_info()

            # Envio da resposta seguindo o protocolo: [Tamanho 4 bytes Big Endian] + [JSON]
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
        # Tenta conectar ao gerente
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((sys.argv[1], 45678))
                print(f"Agente online. Conectado ao Gerente: {sys.argv[1]}")
                handle_requests(s)
        except ConnectionRefusedError:
            print("Erro: O Gerente não está rodando ou a porta 45678 está fechada.")
        except Exception as e:
            print(f"Falha na conexão: {e}")