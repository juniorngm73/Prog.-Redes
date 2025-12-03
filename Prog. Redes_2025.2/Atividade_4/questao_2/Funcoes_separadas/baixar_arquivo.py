IP_TCP = 6                                                          # Constantes para Protocolos
IP_UDP = 17

def baixar_arquivo(url):
    
    print(f"Tentando baixar arquivo de: {url}...")
    try:
        
        arquivo = url.split('/')[-1]
        response = requests.get(url, stream=True, timeout=30)      # Requisição GET
        response.raise_for_status()                                # Exceção Códigos Status (4xx ou 5xx)

        with open(arquivo, 'wb') as f:                             # Salva o arquivo no diretório atual
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:                                          # Filtra chunks keep-alive
                    f.write(chunk)
        
        print(f"Download concluído: {arquivo}")
        return arquivo

    except requests.exceptions.RequestException as e:
        print(f"Erro ao baixar o arquivo: {e}")
        return None
    except Exception as e:
        print(f"Ocorreu um erro inesperado durante o download: {e}")
        return None