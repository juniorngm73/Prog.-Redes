import funções
import json

def validar_ip(ip):

    def validar_masc(mascara_inicial, mascara_final):

        def bin_to_ip(binario):

            def calcular_subrede(ip, mascara_inicial, mascara_final):


                while True:
                    ip = input('Digite um endereço IP: ')
                    valido = validar_ip(ip)
                    dados = {'ip': ip, 'valido': valido}

                    json_string = json.dumps(dados, ident = 4)
                    print(json_string)

                    break



if __name__ == "__main__":
    mascara_inicial = int(input("Máscara Inicial: "))
    mascara_final = int(input("Máscara Final: "))
    mascara_octetos = funções.validar_masc(mascara_inicial, mascara_final)
    funções.calcular_subrede(funções.ip, mascara_inicial, mascara_final)
