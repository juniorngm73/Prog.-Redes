import os, json, requests, re
from urllib.parse import urlparse


# =================================================================
# Dependência 1: Função criar_diretorio (Copiada do funcoes.py)
# =================================================================
def criar_diretorio(diretorio: str) -> bool:
    """Verifica se um diretório existe e o cria se necessário."""
    try:
        if not os.path.exists(diretorio):
            os.makedirs(diretorio)
            print(f"Diretório '{diretorio}' criado com sucesso.")
        return True
    except OSError as e:
        print(f"Erro ao criar o diretório '{diretorio}': {e}")
        return False

# =================================================================
# Dependência 2: Função processar_url (Copiada do funcoes.py)
# =================================================================
def processar_url(url: str) -> dict:
    """Analisa a URL para extrair o host e o nome base ajustados."""
    try:
        parsed_url = urlparse(url)
        host_ajustado = parsed_url.netloc.replace('.', '-')
        caminho = parsed_url.path
        if caminho.endswith('/'): caminho = caminho[:-1] 
        nome_base = caminho.split('/')[-1] if caminho else host_ajustado
        parte_final_url = nome_base + parsed_url.query + parsed_url.fragment
        nome_base_ajustado = re.sub(r'[^\w\-]', '_', parte_final_url)
        
        return {
            "host_ajustado": host_ajustado,
            "nome_base_ajustado": nome_base_ajustado,
            "esquema": parsed_url.scheme
        }
    except Exception as e:
        print(f"Erro ao processar a URL: {e}")
        return {}


# =================================================================
# Função a ser testada: salvar_header
# =================================================================
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

# =================================================================
# Teste de Unidade 3 (Bloco de Execução)
# =================================================================
print("\n--- Testando salvar_header com requisição real (Autônomo) ---")

# 1. Faz uma requisição para obter headers reais
try:
    response = requests.get("https://www.ifrn.edu.br", timeout=5)
    
    # 2. Define o diretório e nome do arquivo
    info = processar_url("https://www.ifrn.edu.br")
    
    # O diretório de output deve ser o diretório base 'headers'
    # Vamos criar um diretório temporário para este teste
    DIRETORIO_TESTE = os.path.join(os.getcwd(), "headers_teste_temp") 
    
    # Obtém o host ajustado para o nome do arquivo
    nome_arq = info.get('host_ajustado') 
    
    # 3. Chama a função de salvamento
    salvar_header(DIRETORIO_TESTE, nome_arq, response.headers) 
    
    print("\nTeste concluído com sucesso. Verifique a pasta 'headers_teste_temp'.")
    
except requests.exceptions.RequestException as e:
    print(f"Teste 3 falhou (Erro de Requisição): {e}. Verifique sua conexão.")
except NameError as e:
    print(f"Erro: {e}. Certifique-se de que todas as funções auxiliares foram coladas acima.")