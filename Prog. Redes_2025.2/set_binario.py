# SETAR UM BIT EM UM INTEIRO

x = 0b1010110
x = x-1
print(f'o valor de x é {x:b}')
print(x)
x = x|8
print(x)
x = x | 0b1000
b = int(input('qual bit a setar'))
x = x|(1<<b)
print(x)



'''setar o bit na posição b de um numero
    corresponde a fazer um | (ou) do numero 
    com 1 deslocada b vezes para a esquerda'''