import os

def criar_diretorio(diretorio):
    """
    Verifica se um diretório existe e o cria se necessário.
    """
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

# --- Teste de Unidade 2 ---
print("\n--- Testando criar_diretorio ---")
dir_teste = "pasta_teste_domingo"
criar_diretorio(dir_teste)
