import requests
import base64
import json
import os


def upload_github(usuario, repositorio, arquivo_envio, arq_repositorio, token, branch='main'):
    """
    Envia (cria ou atualiza) um arquivo para um repositório no GitHub.

    usuario: Nome de usuário do GitHub (proprietário do repositório).
    repositorio: Nome do repositório.
    arquivo_envio: Caminho local para o arquivo a ser enviado.
    arq_repositorio: Caminho desejado para o arquivo no repositório (incluindo o nome do arquivo).
    token: Token de Acesso Pessoal do GitHub com permissões 'repo'.
    branch: Nome do branch (padrão 'main').
    return: Resposta JSON da API ou None em caso de falha.
    """

    # 1. URL da API
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

    # 3. Cabeçalhos de Autenticação (Atenção: 'Authorization' está escrito corretamente em Inglês)
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # 4. Verificar se o arquivo já existe para obter o SHA (necessário para atualização)
    sha = None
    try:
        response_get = requests.get(url, headers=headers)
        if response_get.status_code == 200:
            # Arquivo existe, obter o SHA para atualização
            sha = response_get.json().get('sha')
            print(f"Arquivo '{arq_repositorio}' encontrado. O SHA é {sha}. Será atualizado.")
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
        "message": commit_mensagem, # Atenção: 'message' é o campo correto na API
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
        print(f"Erro HTTP ao enviar arquivo: {e}")
        print(f"Resposta: {response_put.text}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão ao enviar arquivo: {e}")
        return None


# -------------------------------------------------------------
# --- Exemplo de Uso (Dados corrigidos e testados) ---
# -------------------------------------------------------------

# Informações do GitHub
GITHUB_USERNAME = "juniorngm73"
REPO_NAME = "Prog.-Redes"
# ATENÇÃO: COLOQUE SEU TOKEN REAL AQUI! O valor abaixo é um placeholder para o teste.
GITHUB_TOKEN = " " 

# Informações do Arquivo
# Caminho local exato do arquivo
LOCAL_FILE_PATH = "C:\\Users\\novo\\Documents\\JUNIOR\\TECNOLOGIA REDES COMPUTADORES\\Ano 2024\\SEMESTRE 2\\PROG REDES\\Projeto_Bot\\Entrega1\\client.py" 
# Caminho de destino no repositório (PASTA/NOME_DO_ARQUIVO.ext)
# O caminho deve ser relativo à raiz do repositório, não uma URL completa.
GITHUB_DEST_PATH = "Prog. Redes_2025.2/client.py" 

# --- Setup de Exemplo (Cria um arquivo local para teste) ---
# Certifica-se de que o diretório existe para evitar erros de criação de arquivo
os.makedirs(os.path.dirname(LOCAL_FILE_PATH), exist_ok=True)
if not os.path.exists(LOCAL_FILE_PATH):
    with open(LOCAL_FILE_PATH, 'w') as f:
        f.write("Este é o conteúdo do arquivo a ser enviado.\nLinha de teste.")
    print(f"Arquivo de teste '{LOCAL_FILE_PATH}' criado localmente.")
# -----------------------------------------------------------


# --- Execução corrigida ---
# A condição de verificação foi corrigida para usar um placeholder genérico.
# ATENÇÃO: Se o seu token REAL for "SEU_TOKEN_AQUI", isso vai falhar.
if GITHUB_TOKEN == "SEU_TOKEN_AQUI":
    print("\n[ERRO] ⚠️ Por favor, substitua 'SEU_TOKEN_AQUI' pelo seu Token de Acesso Pessoal (PAT) real.")
else:
    print(f"\nTentando enviar '{LOCAL_FILE_PATH}' para '{REPO_NAME}/{GITHUB_DEST_PATH}'...")
    
    # 📌 Nome da função corrigido para 'upload_github'
    result = upload_github(
        usuario=GITHUB_USERNAME,
        repositorio=REPO_NAME,
        arquivo_envio=LOCAL_FILE_PATH,
        arq_repositorio=GITHUB_DEST_PATH,
        token=GITHUB_TOKEN
    )

    if result:
        print("\n✅ Arquivo enviado com sucesso!")
        print(f"URL do conteúdo: {result.get('content', {}).get('html_url')}")
    else:
        print("\n❌ Falha no envio do arquivo.")