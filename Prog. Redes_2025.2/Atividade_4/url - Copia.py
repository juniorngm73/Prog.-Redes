import os
import json
from urllib.parse import urlparse
import re

def processar_url(url: str) -> dict:
    """
    Analisa a URL para extrair o host, o nome do arquivo/caminho e o esquema.
    
    Retorna:
        Um dicionário com 'host', 'caminho_arquivo' e 'extensao_padrao'.
    """
    try:
        parsed_url = urlparse(url)
        
        # 1. Host para nome de arquivo: substitui pontos por hífens
        host_sanitizado = parsed_url.netloc.replace('.', '-')
        
        # 2. Caminho/Nome do arquivo: última parte do caminho da URL, 
        #    ou host se o caminho for vazio.
        caminho = parsed_url.path
        if caminho.endswith('/'):
            caminho = caminho[:-1] # Remove barra final se houver
        
        nome_base = caminho.split('/')[-1] if caminho else host_sanitizado
        
        # Sanitizar nome base: substitui caracteres especiais por '_'
        # Mantém letras, números, hífens e sublinhados.
        nome_base_sanitizado = re.sub(r'[^\w\-]', '_', nome_base)
        
        return {
            "host_sanitizado": host_sanitizado,
            "nome_base_sanitizado": nome_base_sanitizado,
            "esquema": parsed_url.scheme
        }
    except Exception as e:
        print(f"Erro ao processar a URL: {e}")
        return {}