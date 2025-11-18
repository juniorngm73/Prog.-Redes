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