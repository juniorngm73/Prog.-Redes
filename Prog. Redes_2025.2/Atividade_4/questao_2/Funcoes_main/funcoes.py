import requests, zipfile, os, sys, re
import struct, datetime, collections

# Constantes para Protocolos
IP_TCP = 6 
IP_UDP = 17

def baixar_arquivo(url):
    """
    Tenta baixar um arquivo ZIP de uma URL e salva-o no diretório atual.
    Retorna o nome do arquivo baixado em caso de sucesso, ou None em caso de erro.
    """
    print(f"Tentando baixar arquivo de: {url}...")
    try:
        # Extrai o nome do arquivo da URL
        arquivo = url.split('/')[-1]
        
        # Requisição GET com timeout
        response = requests.get(url, stream=True, timeout=30)
        
        # Exceção para Códigos Status (4xx ou 5xx)
        response.raise_for_status()

        # Salva o arquivo no diretório atual
        with open(arquivo, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        print(f"Download concluído: {arquivo}")
        return arquivo

    except requests.exceptions.RequestException as e:
        print(f"Erro ao baixar o arquivo: {e}")
        return None
    except Exception as e:
        print(f"Ocorreu um erro inesperado durante o download: {e}")
        return None
    

def extrair_zip(filepath):
    """
    Descompacta o arquivo ZIP. A senha é gerada com base na data extraída do nome do arquivo.
    Retorna o nome do arquivo .pcap descompactado, ou None em caso de erro.
    """
    base_name = os.path.basename(filepath)
    
    # Validação crucial: o arquivo baixado DEVE ser um zip.
    if not filepath.lower().endswith(('.zip', '.gz', '.tgz', '.rar')): # Embora a questão indique .zip
         if not zipfile.is_zipfile(filepath):
             print(f"Erro: O arquivo '{base_name}' não parece ser um arquivo zip válido.")
             return None
    
    try:
        # Tenta extrair a data do nome do arquivo (YYYYMMDD)
        date_str = ""
        # 1. Tenta buscar um padrão YYYY-MM-DD ou YYYYMMDD em qualquer parte do nome
        match = re.search(r'(\d{4}[_-]?\d{2}[_-]?\d{2})', base_name)
        if match:
            date_str = match.group(1)
        
        if not date_str:
            raise ValueError("Não foi possível extrair a data do nome do arquivo para gerar a senha.")
            
        # Limpar a data e garantir o formato YYYYMMDD
        date_cleaned = "".join(filter(str.isdigit, date_str))
        if len(date_cleaned) < 8:
            raise ValueError(f"Data extraída inválida ou incompleta: {date_cleaned}")
        
        year = date_cleaned[:4]
        month = date_cleaned[4:6]
        day = date_cleaned[6:8]
        
        # Geração da senha: infected_AAAAMMDD
        password = f"infected_{year}{month}{day}".encode('utf-8')
        print(f"Tentando descompactar com a senha: infected_{year}{month}{day}")

        # Descompactação
        with zipfile.ZipFile(filepath, 'r') as zf:
            zf.extractall(pwd=password)
            
            # Localiza o nome do arquivo .pcap dentro do zip
            pcap_files = [name for name in zf.namelist() if name.endswith('.pcap')]
            if not pcap_files:
                 raise FileNotFoundError("O arquivo .zip não contém um arquivo .pcap.")
                 
            pcap_filename = pcap_files[0]
            print(f"Arquivo descompactado com sucesso: {pcap_filename}")
            return pcap_filename

    except ValueError as e:
        print(f"Erro na extração da data/senha: {e}")
        return None
    except zipfile.BadZipFile:
        print("Erro: O arquivo não é um zip válido ou a senha está incorreta.")
        return None
    except Exception as e:
        print(f"Ocorreu um erro inesperado durante a descompactação: {e}")
        return None
    

def ip_to_str(ip_bytes):
    """
    Converte 4 bytes em uma string de endereço IPv4.
    """
    return ".".join(map(str, ip_bytes))


def parse_pcap(pcap_filepath):
    """
    Lê o arquivo .pcap, extrai os cabeçalhos IPv4 e coleta as estatísticas solicitadas.
    Retorna um dicionário de estatísticas e uma lista de headers IPv4.
    """
    print(f"\nIniciando análise do arquivo PCAP: {pcap_filepath}...")
    
    stats = {
        'start_time': None,
        'end_time': None,
        'max_tcp_size': 0,
        'truncated_count': 0,
        'udp_payload_sizes': [],
        'ip_traffic': collections.defaultdict(int),
        'ip_interactions_set': set(),
        'interface_ip': None,
        'total_packets': 0,
        'interaction_count': 0,
        'max_ip_pair': (("N/A", "N/A"), 0)
    }
    
    ipv4_packet_headers = [] 
    
    try:
        with open(pcap_filepath, 'rb') as f:
            # 1. Leitura do Cabeçalho Global do PCAP
            global_header_format = 'IHHIIII' 
            global_header_size = struct.calcsize(global_header_format)
            global_header = f.read(global_header_size)

            if len(global_header) < global_header_size:
                raise EOFError("Arquivo PCAP muito curto (cabeçalho global faltando).")

            magic_number, _, _, _, _, _, link_type = struct.unpack(global_header_format, global_header)

            # Determina a Endianness do arquivo
            if magic_number == 0xd4c3b2a1:
                endianness = '<' # little-endian
            elif magic_number == 0xa1b2c3d4:
                endianness = '>' # big-endian
            else:
                raise ValueError("Número mágico PCAP inválido (formato não reconhecido).")
            
            
            # 2. Leitura dos Pacotes
            packet_header_format = f'{endianness}IIII' # ts_sec, ts_usec, incl_len, orig_len
            packet_header_size = struct.calcsize(packet_header_format)
            
            while True:
                packet_header = f.read(packet_header_size)
                if len(packet_header) < packet_header_size:
                    break 
                
                ts_sec, ts_usec, incl_len, orig_len = struct.unpack(packet_header_format, packet_header)
                
                # Leitura do bloco de dados do pacote
                packet_data = f.read(incl_len)
                if len(packet_data) < incl_len:
                    break 

                stats['total_packets'] += 1

                # a) Início/Término da Captura
                timestamp = ts_sec + ts_usec / 1000000.0
                dt = datetime.datetime.fromtimestamp(timestamp)
                if stats['start_time'] is None:
                    stats['start_time'] = dt
                stats['end_time'] = dt

                # d) Pacotes Truncados
                if incl_len < orig_len:
                    stats['truncated_count'] += 1

                # --- 3. Determinação do Offset (Link Layer Header Size) ---
                current_offset = 0 # Offset padrão (para Link Type 101/Raw IP)
                
                if link_type == 1: 
                    # Ethernet (padrão 14 bytes)
                    
                    # Verifica se o pacote é grande o suficiente para o cabeçalho Ethernet + EtherType
                    if incl_len >= 14:
                        # O campo EtherType está nos bytes 12 e 13. 
                        # Precisa ser 0x0800 (IPv4) ou 0x8100 (VLAN) ou 0x86DD (IPv6)
                        
                        # Extrai EtherType como um short não assinado (H) na Endianness correta
                        # O EtherType está em `packet_data[12:14]`
                        ether_type = struct.unpack(f'{endianness}H', packet_data[12:14])[0]
                        
                        # Tipos importantes:
                        ETHERTYPE_IPV4 = 0x0800
                        ETHERTYPE_VLAN = 0x8100 
                        
                        if ether_type == ETHERTYPE_IPV4:
                            current_offset = 14 # Ethernet padrão (6 Dest + 6 Src + 2 EtherType)
                            
                        elif ether_type == ETHERTYPE_VLAN:
                            # Com VLAN, o campo EtherType real está 4 bytes adiante (offset 16)
                            # E o cabeçalho de enlace total passa a ser 18 bytes
                            current_offset = 18
                            # NOTA: Não precisamos checar se o novo EtherType (em packet_data[16:18]) é IPv4, 
                            # pois o filtro só deve procurar por IPv4 no próximo passo
                        
                        elif ether_type == 0x86DD:
                            # IPv6, será ignorado na próxima etapa
                            current_offset = 14 
                            
                        else:
                            # Outro EtherType (ex: ARP 0x0806), será ignorado.
                            current_offset = 14

                    else:
                        # Pacote muito pequeno, não pode ser IP, vamos ignorar.
                        continue
                
                elif link_type == 101: 
                    # Raw IP
                    current_offset = 0
                    print("Aviso: Tipo de Encapsulamento 'Raw IP' (101) detectado. Usando 0 bytes de offset.")
                
                else:
                    # Link Type não padrão, voltando para o padrão Ethernet por segurança.
                    current_offset = 14
                    
                
                # 4. Análise do Cabeçalho IPv4
                # Pula o cabeçalho de enlace (Ethernet ou outro)
                ip_data = packet_data[current_offset:]
                
                IPV4_HEADER_FORMAT = f'{endianness}BBHHHBBH4s4s'
                IPV4_HEADER_MIN_SIZE = 20 
                
                if len(ip_data) < IPV4_HEADER_MIN_SIZE:
                    continue 

                try:
                    ipv4_header_tuple = struct.unpack(IPV4_HEADER_FORMAT, ip_data[:IPV4_HEADER_MIN_SIZE])
                except struct.error:
                     # Isso geralmente acontece se não for um pacote IPv4 (ex: ARP, IPv6) ou o offset está errado
                     continue


                version_ihl = ipv4_header_tuple[0]
                version = (version_ihl >> 4) & 0xF
                ihl = version_ihl & 0xF 
                ip_header_len_bytes = ihl * 4
                
                # Pacote é IPv4?
                if version != 4:
                     continue 
                
                # O comprimento do cabeçalho IP deve ser pelo menos o mínimo (20 bytes)
                if ip_header_len_bytes < IPV4_HEADER_MIN_SIZE:
                    continue

                total_length = ipv4_header_tuple[2] 
                protocol = ipv4_header_tuple[6]
                src_ip_bytes = ipv4_header_tuple[8]
                dst_ip_bytes = ipv4_header_tuple[9]
                
                src_ip = ip_to_str(src_ip_bytes)
                dst_ip = ip_to_str(dst_ip_bytes)

                
                # Salva a amostra do cabeçalho IPv4 (Apenas o primeiro)
                if not ipv4_packet_headers:
                    ipv4_packet_headers.append({
                        'Versão': version,
                        'IHL (Comprimento do Cabeçalho)': f'{ihl} ({ip_header_len_bytes} bytes)',
                        'DSCP/ECN (Type of Service)': ipv4_header_tuple[1],
                        'Comprimento Total': total_length,
                        'Identificação': ipv4_header_tuple[3],
                        'Flags': (ipv4_header_tuple[4] >> 13) & 0x7,
                        'Fragment Offset': ipv4_header_tuple[4] & 0x1FFF,
                        'TTL': ipv4_header_tuple[5],
                        'Protocolo': f'{protocol} ({"TCP" if protocol == IP_TCP else "UDP" if protocol == IP_UDP else "Outro"})',
                        'Checksum do Cabeçalho': hex(ipv4_header_tuple[7]),
                        'Endereço IP de Origem': src_ip,
                        'Endereço IP de Destino': dst_ip,
                    })

                # c) Par de IP com maior tráfego
                ip_pair = tuple(sorted((src_ip, dst_ip)))
                stats['ip_traffic'][ip_pair] += total_length 

                # f) Contagem de interações IP
                stats['ip_interactions_set'].add(src_ip)
                stats['ip_interactions_set'].add(dst_ip)
                
                # 4. Análise do Protocolo de Transporte (TCP/UDP)
                transport_data = ip_data[ip_header_len_bytes:]
                protocol_data_len = total_length - ip_header_len_bytes
                
                if protocol == IP_TCP:
                    # b) Tamanho do maior TCP pacote capturado
                    stats['max_tcp_size'] = max(stats['max_tcp_size'], total_length) 

                elif protocol == IP_UDP:
                    # e) Tamanho médio dos pacotes UDP (payload)
                    UDP_HEADER_SIZE = 8
                    if len(transport_data) >= UDP_HEADER_SIZE:
                        udp_payload_size = protocol_data_len - UDP_HEADER_SIZE
                        if udp_payload_size >= 0:
                            stats['udp_payload_sizes'].append(udp_payload_size)

        # 5. Cálculos Finais após a leitura de todos os pacotes
        
        # Par de IP com maior tráfego entre eles
        if stats['ip_traffic']:
            max_pair, max_traffic = max(stats['ip_traffic'].items(), key=lambda item: item[1])
            stats['max_ip_pair'] = (max_pair, max_traffic)
        
        # Tamanho médio dos pacotes UDP
        if stats['udp_payload_sizes']:
            stats['avg_udp_size'] = sum(stats['udp_payload_sizes']) / len(stats['udp_payload_sizes'])
        
        # Determinar o IP da interface: o que tem o maior volume de tráfego total (bidirecional)
        ip_counts = collections.defaultdict(int)
        for (ip1, ip2), size in stats['ip_traffic'].items():
            ip_counts[ip1] += size
            ip_counts[ip2] += size
        
        if ip_counts:
            stats['interface_ip'] = max(ip_counts, key=ip_counts.get)
            
            # Contar interações: todos os outros IPs com os quais o IP da interface interagiu
            interacting_ips = stats['ip_interactions_set'].difference({stats['interface_ip']})
            stats['interaction_count'] = len(interacting_ips)
        
        # --- AVISO se nenhum pacote IPv4 foi processado ---
        if not ipv4_packet_headers:
            print("\nAVISO CRÍTICO: NENHUM pacote IPv4 válido foi processado. Verifique o Link Type e os Offsets.")
            
        return stats, ipv4_packet_headers

    except FileNotFoundError:
        print(f"Erro: Arquivo PCAP não encontrado em {pcap_filepath}")
        return None, None
    except ValueError as e:
        print(f"Erro de formato PCAP: {e}")
        print(f"Detalhes do Erro: {e}") 
        return None, None
    except EOFError as e:
        print(f"Erro de leitura do arquivo PCAP: {e}")
        print(f"Detalhes do Erro: {e}") 
        return None, None
    except Exception as e:
        print(f"Ocorreu um erro inesperado durante a análise do PCAP: {e}")
        print(f"Detalhes do Erro: {e}") 
        return None, None