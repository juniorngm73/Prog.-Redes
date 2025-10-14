def inteiropos():

    x = 1


    while True:
        num_digitos_x = len(str(x))
        if len(str(6 * x)) > num_digitos_x:
            x = 10 ** num_digitos_x
            continue

        digitos_x = sorted(str(x))

        encontrado = True

        for i in range(2, 7):
            multiplo = i * x

            # Se os dígitos do múltiplo não forem os mesmos, a condição falha
            if sorted(str(multiplo)) != digitos_x:
                encontrado = False
                break

        # Se a condição for verdadeira para todos os múltiplos, x é a resposta
        if encontrado:
            return x

        x += 1



resultado = inteiropos()
print(f"O menor inteiro positivo x é: {resultado}")