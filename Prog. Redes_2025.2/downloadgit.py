import requests
import base64

usuario = 'juniorngm73'
repositorio = 'Treinamento'
arquivo_repo = 'docker.txt'

url = f"https://api.github.com/repos/{usuario}/{repositorio}/contents/{arquivo_repo}"

response = requests.get(url)                                                          #Requisição HTTP GET para a API (retorna JSON)

if response.status_code == 200:
    data = response.json()
    conteudo_base64 = data.get('content')                                             # O conteúdo está na chave 'content' e codificado em Base64
    
    if conteudo_base64:
        conteudo_binario = base64.b64decode(conteudo_base64)                          # Decodifica o Base64 para bytes binários

        with open(arquivo_repo, 'wb') as file:                                        # Salva os bytes decodificados
            file.write(conteudo_binario)
            print(f"Sucesso! O arquivo foi baixado e salvo como: {arquivo_repo} ")
    else:
        print("Erro interno na resposta da API (sem conteúdo Base64).")               # caso de o JSON sem a chave 'content'.
        

elif response.status_code == 404:                                                     # Erro 404 (Não Encontrado)
    print(f" Erro 404:  O arquivo {arquivo_repo} não foi encontrado no repositório. Verifique o nome do arquivo e o caminho.")