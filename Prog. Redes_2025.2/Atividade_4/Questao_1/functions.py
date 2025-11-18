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



def requisicao_ped(url):
    
    print(f"\nTentando acessar a URL: {url}")

    try:
        response = requests.get(url, timeout=10, stream=True) 
        response.raise_for_status()
        print("Requisição bem-sucedida.")
        return response
    except requests.exceptions.RequestException as e:
        print(f" Erro na requisição para {url}: {e}")
        return None
    


def salvar_conteudo(response, info_url):

    if response is None:
        return
    content_type = response.headers.get('Content-Type', '')

     # 1. Informa o diretório e extensão
    if 'text/html' in content_type: 
        diretorio = 'content_html'
        extensao = '.html'
        nome_arquivo = info_url["host_ajustado"] 

    elif 'image/jpeg' in content_type:
        diretorio = 'content_jpg'
        extensao = '.jpg'
        nome_arquivo = info_url["nome_base_ajustado"]

    elif 'image/png' in content_type:
        diretorio = 'content_png'
        extensao = '.png'
        nome_arquivo = info_url["nome_base_ajustado"]

    else:
        partes_tipo = content_type.split('/')
        if len(partes_tipo) == 2:
            extensao = f'.{partes_tipo[1].split(";")[0]}' 
        else:
            extensao = '' # Sem extensão se for muito genérico
        diretorio = 'content_outros'
        nome_arquivo = info_url["nome_base_ajustado"]

    # 2. Insere o caminho completo
    
    nome_completo_arquivo = nome_arquivo + extensao
    caminho_completo = os.path.join(diretorio, nome_completo_arquivo)
    
    try:
        if not criar_diretorio(diretorio):
            return

        with open(caminho_completo, 'wb') as f: # 'wb' para escrita binária
            for chunk in response.iter_content(chunk_size=8192):
                if chunk: # filtra chunks vazios
                    f.write(chunk)
            
        print(f"Conteúdo ({content_type}) salvo em: {caminho_completo}")

    except Exception as e:
        print(f" Erro ao salvar o conteúdo: {e}")