import os, json, re, requests
from urllib.parse import urlparse


def processar_url(url):   # Analisa a URL para extrair o host, o nome do arquivo/caminho e o esquema.
    
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
    


def criar_diretorio(diretorio):  # Verifica se um diretório existe e o cria se necessário.
    
    try:
        if not os.path.exists(diretorio):
            os.makedirs(diretorio)
            print(f"Diretório '{diretorio}' criado com sucesso.")
        else:
            print(f"Diretório '{diretorio}' já existe.")
        return True
    except OSError as e:
        print(f"Erro ao criar o diretório '{diretorio}': {e}")
        return False
    


def salvar_header(dir_output, nome_arq, headers): 
    # Salva os headers da requisição em um arquivo JSON no diretório especificado.
    
    caminho_completo = os.path.join(dir_output, nome_arq)
    
    # Adiciona a extensão .json ao nome do arquivo
    if not caminho_completo.endswith('.json'):
        caminho_completo += '.json'
        
    try:
        diretorio_final = os.path.dirname(caminho_completo)
        if not criar_diretorio(diretorio_final): 
            return

        with open(caminho_completo, 'w', encoding='utf-8') as f:
            # Converte os headers (dicionário) para JSON
            json.dump(dict(headers), f, ensure_ascii=False, indent=4)
        print(f"Headers salvos em: {caminho_completo}")

    except Exception as e:
        print(f"Erro ao salvar o header: {e}")