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
    

def parse_pcap(pcap_filepath):                                                 # Lê o arquivo .pcap e executa a análise solicitada.

    print(f"\nIniciando análise do arquivo PCAP: {pcap_filepath}...")
    
    stats = {
        'start_time': None,
        'end_time': None,
        'max_tcp_size': 0,
        'truncated_count': 0,
        'udp_sizes': [],
        'ip_traffic': collections.defaultdict(int),
        'ip_interactions': set(),
        'interface_ip': None,                                              # O IP da interface é o IP mais frequente (ou primeiro IP de origem)
        'total_packets': 0
    }
    
                                                                              
    ipv4_packet_headers = []                                                # Pacotes IPv4 capturados para exibição de cabeçalhos
    
    try:
        with open(pcap_filepath, 'rb') as f:
            global_header_format = 'IHHIIII' 
            global_header_size = struct.calcsize(global_header_format)
            global_header = f.read(global_header_size)

            if len(global_header) < global_header_size:
                 raise EOFError("Arquivo PCAP muito curto (cabeçalho global faltando).")

            magic_number = struct.unpack(global_header_format, global_header)[0]

            if magic_number == 0xd4c3b2a1:
                endianness = '<' # little-endian
            elif magic_number == 0xa1b2c3d4:
                endianness = '>' # big-endian
            else:
                raise ValueError("Número mágico PCAP inválido (formato não reconhecido).")
            
            # 2. Leitura dos Pacotes
            # Cabeçalho do Pacote (16 bytes): ts_sec: 4, ts_usec: 4, incl_len: 4, orig_len: 4
            packet_header_format = f'{endianness}IIII'
            packet_header_size = struct.calcsize(packet_header_format)
            
            while True:
                packet_header = f.read(packet_header_size)
                if len(packet_header) < packet_header_size:
                    break # Fim do arquivo

                ts_sec, ts_usec, incl_len, orig_len = struct.unpack(packet_header_format, packet_header)
                
                # Leitura do bloco de dados do pacote
                packet_data = f.read(incl_len)
                if len(packet_data) < incl_len:
                    break # Arquivo truncado no meio dos dados

                stats['total_packets'] += 1

                # a. Início/Término da Captura
                timestamp = ts_sec + ts_usec / 1000000.0
                dt = datetime.datetime.fromtimestamp(timestamp)
                if stats['start_time'] is None:
                    stats['start_time'] = dt
                stats['end_time'] = dt

                # b. Pacotes Truncados
                if incl_len < orig_len:
                    stats['truncated_count'] += 1

                # 3. Análise do Pacote (Assumindo Ethernet: 14 bytes)
                ETHERNET_HEADER_SIZE = 14
                
                # Verifica se há dados suficientes para o cabeçalho Ethernet e IPv4 mínimo
                if incl_len < ETHERNET_HEADER_SIZE + 20:
                    continue # Pacote muito pequeno, ignora

                # Pula o cabeçalho Ethernet
                ip_data = packet_data[ETHERNET_HEADER_SIZE:]
   
                IPV4_HEADER_FORMAT = f'{endianness}BBHHHBBH4s4s'
                IPV4_HEADER_SIZE = struct.calcsize(IPV4_HEADER_FORMAT)
                
                if len(ip_data) < IPV4_HEADER_SIZE:
                    continue # Não é um pacote IPv4 completo

                ipv4_header_tuple = struct.unpack(IPV4_HEADER_FORMAT, ip_data[:IPV4_HEADER_SIZE])

                # Extração dos campos importantes do cabeçalho IPv4
                version_ihl = ipv4_header_tuple[0]
                version = (version_ihl >> 4) & 0xF
                ihl = version_ihl & 0xF # Internet Header Length (em unidades de 4 bytes)
                ip_header_len_bytes = ihl * 4
                
                total_length = ipv4_header_tuple[2] # Tamanho total (incluindo cabeçalhos IP e superiores + dados)
                protocol = ipv4_header_tuple[6]
                src_ip_bytes = ipv4_header_tuple[8]
                dst_ip_bytes = ipv4_header_tuple[9]
                
                src_ip = ip_to_str(src_ip_bytes)
                dst_ip = ip_to_str(dst_ip_bytes)

                # Salvar a primeira amostra do cabeçalho IPv4
                if not ipv4_packet_headers:
                    # Estrutura do cabeçalho IPv4 para exibição
                    ipv4_packet_headers.append({
                        'Versão': version,
                        'IHL (Comprimento do Cabeçalho)': f'{ihl} ({ip_header_len_bytes} bytes)',
                        'DSCP/ECN (Type of Service)': ipv4_header_tuple[1],
                        'Comprimento Total': total_length,
                        'Identificação': ipv4_header_tuple[3],
                        'Flags/Offset': ipv4_header_tuple[4],
                        'TTL': ipv4_header_tuple[5],
                        'Protocolo': f'{protocol} ({"TCP" if protocol == IP_TCP else "UDP" if protocol == IP_UDP else "Outro"})',
                        'Checksum do Cabeçalho': ipv4_header_tuple[7],
                        'Endereço IP de Origem': src_ip,
                        'Endereço IP de Destino': dst_ip,
                    })

                # O tamanho real dos dados capturados (payload + cabeçalho do protocolo) é 'total_length - ip_header_len_bytes'
                protocol_data_len = total_length - ip_header_len_bytes
                
                # Normaliza o par de IPs para contagem (ex: A->B é o mesmo que B->A para o tráfego total)
                ip_pair = tuple(sorted((src_ip, dst_ip)))
                stats['ip_traffic'][ip_pair] += total_length # Contar tráfego em bytes
                
                # Registra as interações de IPs
                stats['ip_interactions'].add(src_ip)
                stats['ip_interactions'].add(dst_ip)
                
                # 5. Análise do Protocolo de Transporte
                transport_data = ip_data[ip_header_len_bytes:]
                
                if protocol == IP_TCP:
                    # TCP Header: 20 bytes (mínimo)
                    TCP_HEADER_SIZE = 20
                    if len(transport_data) >= TCP_HEADER_SIZE:
                        # O tamanho do pacote TCP é o tamanho total (IP Total Length)
                        stats['max_tcp_size'] = max(stats['max_tcp_size'], total_length)

                elif protocol == IP_UDP:
                    # UDP Header: 8 bytes
                    UDP_HEADER_SIZE = 8
                    if len(transport_data) >= UDP_HEADER_SIZE:
                        # Comprimento do pacote UDP é extraído do cabeçalho UDP (não necessário)
                        # O tamanho do payload UDP é total_length - IP Header Len - UDP Header Len
                        udp_payload_size = protocol_data_len - UDP_HEADER_SIZE
                        stats['udp_sizes'].append(udp_payload_size)
                        
                       
            # Contagem de frequência individual dos IPs
            ip_counts = collections.defaultdict(int)
            for (ip1, ip2), size in stats['ip_traffic'].items():
                ip_counts[ip1] += size
                ip_counts[ip2] += size
            
            if ip_counts:
                # O IP da interface capturada é o que tem o maior volume de tráfego
                stats['interface_ip'] = max(ip_counts, key=ip_counts.get)
                
                # Contar interações: todos os outros IPs com os quais ele interagiu
                interaction_count = 0
                for (ip1, ip2) in stats['ip_traffic']:
                    if ip1 == stats['interface_ip'] and ip2 != stats['interface_ip']:
                        # Interagiu com ip2
                        interaction_count += 1
                    elif ip2 == stats['interface_ip'] and ip1 != stats['interface_ip']:
                        # Interagiu com ip1
                        interaction_count += 1
                stats['interaction_count'] = interaction_count

            # f. Qual o par de IP com maior tráfego entre eles?
            if stats['ip_traffic']:
                max_pair = max(stats['ip_traffic'], key=stats['ip_traffic'].get)
                max_traffic = stats['ip_traffic'][max_pair]
                stats['max_ip_pair'] = (max_pair, max_traffic)
            else:
                stats['max_ip_pair'] = (("N/A", "N/A"), 0)
            
            # d. Tamanho médio dos pacotes UDP
            if stats['udp_sizes']:
                stats['avg_udp_size'] = sum(stats['udp_sizes']) / len(stats['udp_sizes'])
            else:
                stats['avg_udp_size'] = 0


            return stats, ipv4_packet_headers

    except FileNotFoundError:
        print(f"Erro: Arquivo PCAP não encontrado em {pcap_filepath}")
        return None, None
    
    except ValueError as e:
        print(f"Erro de formato PCAP: {e}")
        return None, None
    
    except Exception as e:
        print(f"Ocorreu um erro inesperado durante a análise do PCAP: {e}")
        return None, None