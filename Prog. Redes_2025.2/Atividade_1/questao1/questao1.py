import math

def soma_fatorial():
    # Pré-calcula os fatoriais de 0 a 9 para acesso rápido
    fatoriais = [math.factorial(i) for i in range(10)]


    limite_superior = 2540161

    soma_total = 0

    for n in range(10, limite_superior):
        soma_fatoriais_digitos = 0
        temp_n = n

        # Calcula a soma dos fatoriais dos dígitos
        while temp_n > 0:
            digito = temp_n % 10
            soma_fatoriais_digitos += fatoriais[digito]
            temp_n //= 10

        # Verifica se o número é igual à soma dos fatoriais de seus dígitos
        if n == soma_fatoriais_digitos:
            soma_total += n

    return soma_total



resultado = soma_fatorial()
print(f"A soma de todos os números que são iguais à soma do fatorial de seus dígitos é: {resultado}")