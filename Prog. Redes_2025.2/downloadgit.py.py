import requests
import base64

usuario = 'juniorngm73'
repositorio = 'Prog.-Redes'
arquivo_repo = 'set_binario1'
url =  f"https://api.github.com/repos/{usuario}/{repositorio}/contents/{arquivo_repo}"


try:
    # Faz a requisição HTTP GET
    response = requests.get(url)

    # Verifica se a requisição foi bem-sucedida (código de status 200)
    if response.status_code == 200:
        # Abre o arquivo local em modo de escrita binária ('wb')
        with open(arquivo_repo, 'wb') as file:
            # Escreve o conteúdo binário da resposta no arquivo
            file.write(response.content)

        print(f"Sucesso! O arquivo foi baixado e salvo como: **{arquivo_repo}**")
    elif response.status_code == 404:
        print(f"Erro 404: Arquivo não encontrado no URL. Verifique o caminho e o nome do arquivo.")
    else:
        print(f"Erro ao baixar o arquivo. Código de status: {response.status_code}")

except requests.exceptions.RequestException as e:
    # Captura erros de rede (como falha de conexão ou DNS)
    print(f"Erro de conexão: {e}")