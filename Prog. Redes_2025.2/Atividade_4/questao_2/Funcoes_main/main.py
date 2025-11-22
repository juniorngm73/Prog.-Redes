import os, sys, funcoes
import collections


def main():


    print("--- Analisador de Arquivos PCAP ---") 
   
    url = input("Digite a URL completa do arquivo .zip PCAP ")                 #  Solicita a URL ao usuário.
    if not url.strip():
        print("URL não fornecida. Encerrando.")
        return

    caminho_zip = None
    pcap_descompactado = None

    try:
        caminho_zip = funcoes.baixar_arquivo(url)
        if not caminho_zip:
            print("Não foi possível continuar devido a falha no download.")
            return

        pcap_descompactado = funcoes.extrair_zip(caminho_zip)
        if not pcap_descompactado:
            print("Não foi possível continuar devido a falha na descompactação.")
            return

        stats, ipv4_headers = funcoes.parse_pcap(pcap_descompactado)
        if stats and ipv4_headers:
            print("\n" + "="*50)
            print("        RESULTADOS DA ANÁLISE PCAP")
            print("="*50)
            print("\n[1] Campos do Cabeçalho IPv4 (Amostra do Primeiro Pacote):")
            sample_header = ipv4_headers[0]
            for campo, valor in sample_header.items():
                print(f"  - {campo.ljust(35)}: {valor}")
            print("-" * 50)

            
            start_time_str = stats['start_time'].strftime("%Y-%m-%d %H:%M:%S.%f") if stats['start_time'] else "N/A"  # Momento que inicia/termina a captura de pacotes.
            end_time_str = stats['end_time'].strftime("%Y-%m-%d %H:%M:%S.%f") if stats['end_time'] else "N/A"
            print(f"[2] Início da Captura           : {start_time_str}")
            print(f"[3] Término da Captura          : {end_time_str}")
            print(f"[4] Maior Pacote TCP (total IP) : {stats['max_tcp_size']} bytes")                                 # Tamanho do maior pacote TCP capturado.          
            print(f"[5] Pacotes Truncados           : {stats['truncated_count']} pacotes")                            # Pacotes que não foram salvos nas suas totalidades.

           
            avg_udp = f"{stats['avg_udp_size']:.2f} bytes (Payload)" if stats['avg_udp_size'] > 0 else "N/A (Nenhum pacote UDP encontrado)"    # Tamanho médio dos pacotes UDP capturados.
            print(f"[6] Tamanho Médio UDP           : {avg_udp}")

        
            pair, traffic = stats['max_ip_pair']                                                                        # Par de IP com maior tráfego entre eles.
            print(f"[7] Par de IPs com Maior Tráfego: {pair[0]} <-> {pair[1]} ({traffic} bytes)")

            
            interface_ip = stats['interface_ip'] if stats['interface_ip'] else "N/A"                                     # Com quantos outros IPs o IP da interface capturada interagiu.
            interaction_count = stats['interaction_count']
            
            print(f"[8] IP da Interface Capturada   : {interface_ip}")
            print(f"[9] Total de IPs Interagindo    : {interaction_count} outros IPs")
            print("="*50)

        else:
            print("\nAnálise PCAP falhou ou não retornou dados.")

    except Exception as e:
        print(f"\nERRO FATAL no fluxo principal: {e}")
    
    finally:
        if caminho_zip and os.path.exists(caminho_zip):                                                       # Remove os arquivos baixados e descompactados para limpeza.
            os.remove(caminho_zip)
            print(f"\nArquivo temporário removido: {caminho_zip}")
        if pcap_descompactado and os.path.exists(pcap_descompactado):
            os.remove(pcap_descompactado)
            print(f"Arquivo temporário removido: {pcap_descompactado}")


if __name__ == "__main__":
    main()