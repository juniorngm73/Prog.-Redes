def criptografar(arquivo_origem, senha, arquivo_destino):
    """Criptografa um arquivo usando a operação XOR e uma senha.

    Args:
        arquivo_origem (str): Nome do arquivo de origem.
        senha (str): Senha para criptografia.
        arquivo_destino (str): Nome do arquivo de destino.
    """

    try:
        # Abre os arquivos em modo binário
        with open(arquivo_origem, 'rb') as entrada, open(arquivo_destino, 'wb') as saida:
            # Verifica se o arquivo de destino já existe
            if saida.tell() != 0:
                raise FileExistsError("O arquivo de destino já existe.")

            # Itera sobre cada byte do arquivo de origem
            i = 0
            while True:
                byte = entrada.read(1)
                if not byte:
                    break  # Fim do arquivo
                char_senha = senha[i % len(senha)]
                saida.write(bytes([byte[0] ^ ord(char_senha)]))
                i += 1

    except FileNotFoundError:
        print("Arquivo de origem não encontrado.")
        while True:
            arquivo_origem = input("Digite o nome do arquivo de origem: ")
            try:
                # Abre os arquivos em modo binário
                with open(arquivo_origem, 'rb') as entrada, open(arquivo_destino, 'wb') as saida:
                    # Verifica se o arquivo de destino já existe
                    if saida.tell() != 0:
                        raise FileExistsError("O arquivo de destino já existe.")

                    # Itera sobre cada byte do arquivo de origem
                    i = 0
                    while True:
                        byte = entrada.read(1)
                        if not byte:
                            break  # Fim do arquivo
                        char_senha = senha[i % len(senha)]
                        saida.write(bytes([byte[0] ^ ord(char_senha)]))
                        i += 1
                    break



            except PermissionError:
                print("Permissão negada.")
            except FileExistsError as e:
                print(e)
            except Exception as e:
                print(f"Ocorreu um erro inesperado: {e}")


arquivo_origem = input("Digite o nome do arquivo de origem: ")
senha = input("Digite a palavra-passe: ")
arquivo_destino = input("Digite o nome do arquivo de destino: ")



criptografar(arquivo_origem, senha, arquivo_destino)