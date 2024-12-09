import funções

def validar_ip(ip):

    def validar_masc(mascara_inicial, mascara_final):

        def bin_to_ip(binario):

            def calcular_subrede_json(ip, mascara_inicial, mascara_final):


                while True:
                    ip = input('Digite um endereço IP: ')
                    if validar_ip(ip):
                        break
                    else:
                        print("O endereço IP é inválido, tente novamente.")


if __name__ == "__main__":
    mascara_inicial = int(input("Máscara Inicial: "))
    mascara_final = int(input("Máscara Final: "))
    mascara_octetos = funções.validar_masc(mascara_inicial, mascara_final)
    funções.calcular_subrede_json(funções.ip, mascara_inicial, mascara_final)
    resultado_json = funções.calcular_subrede_json(funções.ip, mascara_inicial, mascara_final)
    print(resultado_json)