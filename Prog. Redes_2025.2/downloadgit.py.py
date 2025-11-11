import requests
import base64

usuario = 'juniorngm73'
repositorio = 'Prog.-Redes/Prog. Redes_2025.2'
arquivo_repo = 'uploadgit'
url_api = f"https://api.github.com/repos/{usuario}/{repositorio}/contents/{arquivo_repo}"

try:
    # 1. Faz a requisição HTTP GET para a API (retorna JSON)
    response = requests.get(url_api)

    if response.status_code == 200:
        data = response.json()

        # O conteúdo está na chave 'content' e codificado em Base64
        conteudo_base64 = data.get('content')

        if conteudo_base64:
            # Remove quebras de linha que o GitHub às vezes adiciona ao Base64
            conteudo_base64 = conteudo_base64.replace('\n', '')

            # 2. Decodifica o Base64 para bytes binários
            conteudo_binario = base64.b64decode(conteudo_base64)

            # 3. Salva os bytes decodificados
            with open(arquivo_repo, 'wb') as file:
                file.write(conteudo_binario)

            print(f"Sucesso! O arquivo foi baixado (via API + Base64) e salvo como: **{arquivo_repo}**")
        else:
             print("Erro: O JSON da API não contém a chave 'content'.")

    elif response.status_code == 404:
        print(f"Erro 404: Arquivo '{arquivo_repo}' não encontrado na API do GitHub.")
    else:
        print(f"Erro ao acessar a API. Código de status: {response.status_code}")

except requests.exceptions.RequestException as e:
    print(f"Erro de conexão: {e}")