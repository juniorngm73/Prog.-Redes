import re
from urllib.parse import urlparse

def processar_url(url):
    """
    Analisa a URL para extrair o host, o nome do arquivo/caminho e o esquema.
    """
    try:
        parsed_url = urlparse(url)
        
        # 1. ajuste: substitui pontos por hífens
        host_ajustado = parsed_url.netloc.replace('.', '-')
        
        # 2. Caminho/Nome do arquivo: última parte do caminho.
        caminho = parsed_url.path
        if caminho.endswith('/'):
            caminho = caminho[:-1] 
        
        # Usa a última parte do caminho, ou o host ajustado se o caminho for vazio
        nome_base = caminho.split('/')[-1] if caminho else host_ajustado
        
        # 3. ajustar nome base: substitui caracteres especiais por '_'
        
        parte_final_url = nome_base + parsed_url.query + parsed_url.fragment

        # Substitui caracteres que não são letras, números, hífens ou sublinhados por '_'
        nome_base_ajustado = re.sub(r'[^\w\-]', '_', parte_final_url)
        
        return {
            "host_ajustado": host_ajustado,
            "nome_base_ajustado": nome_base_ajustado,
            "esquema": parsed_url.scheme
        }
    except Exception as e:
        print(f"Erro ao processar a URL: {e}")
        return {}

# --- Teste de Unidade 1 ---
print("--- Testando processar_url ---")
url_exemplo = "http://www.detran.rn.gov.br/"
resultado = processar_url(url_exemplo)

print(f"URL Original: {url_exemplo}")
print(f"Host (Header): {resultado.get('host_ajustado')}")
print(f"Nome Base (Content): {resultado.get('nome_base_ajustado')}")
print(f"Esquema: {resultado.get('esquema')}")