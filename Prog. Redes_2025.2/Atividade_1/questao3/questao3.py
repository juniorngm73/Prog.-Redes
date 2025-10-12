def maior_soma():
    
    # 1. Carregar o triângulo do arquivo
    try:
        with open('triangulo.txt', 'r') as arquivo:
            conteudo = arquivo.read()
    except FileNotFoundError:
        return "Erro: O arquivo 'triangulo.txt' não foi encontrado."

    # Converter o conteúdo do arquivo em uma lista de listas de inteiros
    triangulo = []
    for linha in conteudo.strip().split('\n'):
        numeros = [int(n) for n in linha.split()]
        triangulo.append(numeros)

    # 2. Iterar de baixo para cima
    # O loop vai da penúltima linha (índice len(triangulo) - 2) até a primeira (índice 0)
    for i in range(len(triangulo) - 2, -1, -1):
        # 3. Para cada número na linha atual
        for j in range(len(triangulo[i])):
            # Calcula a soma máxima e atualiza o valor no triângulo
            soma_maxima = triangulo[i][j] + max(triangulo[i+1][j], triangulo[i+1][j+1])
            triangulo[i][j] = soma_maxima

    
    return triangulo[0][0]


soma_maxima_caminho = maior_soma()
print(f"A soma máxima do caminho é: {soma_maxima_caminho}")