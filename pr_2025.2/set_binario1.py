# SETAR OS N BITS MAIS A DIREITA P/1

x = 86
nb = int(input("quantos bits a direita setar"))
x = x | ((0b1 << nb) -1)

print(x)