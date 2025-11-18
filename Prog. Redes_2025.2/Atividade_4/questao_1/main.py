import sys 

try:
    from functions import ( processar_url, requisicao_ped, salvar_header, salvar_conteudo )

except ImportError:
    print(" Erro: O arquivo 'functios.py' não foi encontrado ou possui erros.")
    sys.exit(1)


def main():
        
    # 1. Solicita a URL do usuário
    url_input = input("Por favor, insira a URL para download: ").strip()

    if not url_input:
        print("URL não fornecida. Encerrando o programa.")
        return

    
    if not url_input.startswith(('http://', 'https://')):
        url_input = 'https://' + url_input
        print(f"Assumindo 'https://': {url_input}")


    # 2. Processa a URL  extrair o host, nome base, etc.
    print("\n--- 1. Processando URL para nomenclatura ---")
    info_url = processar_url(url_input)
    
    if not info_url or not info_url.get("host_ajustado"):
        print(" Não foi possível processar a URL. Verifique o formato ou se é válida.")
        return
    
    host_ajustado = info_url["host_ajustado"]
    

    # 3. Requisição HTTP
    print("\n--- 2. Fazendo Requisição ---")
    response = requisicao_ped(url_input)
    
    if response is None:
        
        print("Download encerrado devido a falha na requisição.")
        return


    # 4. Salva o Header 
    print("\n--- 3. Salvando Header ---")
    diretorio_header = 'headers'
    nome_arquivo_header = host_ajustado 
    
    salvar_header(diretorio_header, nome_arquivo_header, response.headers)


    # 5. Salva o Conteúdo 
    print("\n--- 4. Salvando Conteúdo ---")
    salvar_conteudo(response, info_url)
    
    
    print("\n Processo concluído com sucesso!")


# Chamada
if __name__ == "__main__":
    main()