import requests
import base64
import json
import os
import sys

def upload_github(usuario, repositorio, arquivo_envio, arq_repositorio, token, branch='main'):

    url = f"https://api.github.com/repos/{usuario}/{repositorio}/contents/{arq_repositorio}"

    # 2. Ler e codificar o conteúdo do arquivo
    try:
        
        with open(arquivo_envio, 'rb') as f:
            content_bytes = f.read()
        
        # Codificar em Base64
        encoded_content = base64.b64encode(content_bytes).decode('utf-8')
    except FileNotFoundError:
        print(f"Erro: Arquivo local não encontrado em '{arquivo_envio}'")
        return None
    except IsADirectoryError:
        print(f"Erro: O caminho local '{arquivo_envio}' é um diretório. Você deve especificar um arquivo.")
        return None

    # 3. Cabeçalhos de Autenticação
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # 4. Verificar se o arquivo já existe para obter o SHA (necessário para atualização)
    sha = None
    try:
        response_get = requests.get(url, headers=headers)
        
        if response_get.status_code == 200:
            data = response_get.json()
            # Verifica se a resposta é um dicionário antes de usar .get('sha')
            if isinstance(data, dict):
                sha = data.get('sha')
                print(f"Arquivo '{arq_repositorio}' encontrado. O SHA é {sha}. Será atualizado.")
            else:
                 # Trata o caso do retorno ser uma lista (erro de caminho para diretório)
                 print(f"Erro ao verificar arquivo: O GitHub retornou uma lista. Verifique se o caminho '{arq_repositorio}' está correto e termina com o nome do arquivo.")
                 return None
                 
        elif response_get.status_code == 404:
            print(f"Arquivo '{arq_repositorio}' não encontrado. Será criado.")
        else:
            print(f"Erro ao verificar o arquivo (Status: {response_get.status_code}): {response_get.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão ao verificar o arquivo: {e}")
        return None

    # 5. Montar o corpo da requisição PUT
    commit_mensagem = f"Atualização arquivo: {arq_repositorio}" if sha else f"Criação arquivo: {arq_repositorio}"

    data = {
        "message": commit_mensagem, 
        "content": encoded_content,
        "branch": branch
    }

    # Adicionar o SHA se for uma atualização
    if sha:
        data["sha"] = sha

    # 6. Enviar a requisição PUT
    try:
        response_put = requests.put(url, headers=headers, data=json.dumps(data))
        response_put.raise_for_status()  # Lança exceção para códigos de status 4xx/5xx

        print(f"Sucesso! Status: {response_put.status_code}")
        return response_put.json()

    except requests.exceptions.HTTPError as e:
        print(f"\n❌ Erro HTTP ao enviar arquivo: {e}")
        print(f"Resposta: {response_put.text}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Erro de conexão ao enviar arquivo: {e}")
        return None




# Informações do GitHub
GITHUB_USERNAME = "juniorngm73"
REPO_NAME = "Prog.-Redes"
# ATENÇÃO: SUBSTITUA PELO SEU TOKEN REAL E VÁLIDO COM PERMISSÃO 'repo'.
GITHUB_TOKEN = " " 

# Informações do Arquivo

LOCAL_FILE_DIR = "C:\\Users\\novo\\Documents\\GitHub\\Prog.-Redes\\Prog. Redes_2025.2"

LOCAL_FILE_NAME = "bitcoin.txt" 

LOCAL_FILE_PATH = os.path.join(LOCAL_FILE_DIR, LOCAL_FILE_NAME)

#  Caminho de destino no repositório (Pasta/NomeDoArquivo.ext)

GITHUB_DEST_PATH = f"Prog. Redes_2025.2/{LOCAL_FILE_NAME}" 

# --- Setup de Exemplo (Cria um arquivo local para teste) ---

# Garante que o diretório exista
os.makedirs(LOCAL_FILE_DIR, exist_ok=True) 

# Se o ARQUIVO não existe, cria ele com um conteúdo de teste
if not os.path.exists(LOCAL_FILE_PATH): 
    # Abre no modo 'w' (escrita de texto) para criar o conteúdo
    with open(LOCAL_FILE_PATH, 'w') as f:
        f.write("# Arquivo de Teste de Upload\nprint('Este arquivo foi enviado via script Python!')")
    print(f"Arquivo de teste '{LOCAL_FILE_PATH}' criado localmente.")
# -----------------------------------------------------------


# --- Execução Principal ---
if GITHUB_TOKEN == " ":
    print("\n[ERRO] ⚠️ Por favor, insira o seu  Token de Acesso Pessoal.")
    sys.exit(1)
else:
    print(f"\nTentando enviar '{LOCAL_FILE_PATH}' para '{REPO_NAME}/{GITHUB_DEST_PATH}'...")
    
    result = upload_github(
        usuario=GITHUB_USERNAME,
        repositorio=REPO_NAME,
        arquivo_envio=LOCAL_FILE_PATH,
        arq_repositorio=GITHUB_DEST_PATH,
        token=GITHUB_TOKEN
    )

    print("-" * 50)
    if result:
        print("\n✅ Arquivo enviado com sucesso!")
        print(f"URL de visualização: {result.get('content', {}).get('html_url')}")
    else:
        print("\n❌ Falha no envio do arquivo.")