import requests
from bs4 import BeautifulSoup
import json

def encontra_portas(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    portas = []
    for row in soup.find_all('tr'):
        cols = row.find_all('td')
        if len(cols) >= 3:
            porta = (cols[0].text.strip())
            protocolo = cols[1].text.strip()
            descricao = cols[2].text.strip()
            portas.append({'porta': porta, 'protocolo': protocolo, 'descricao': descricao})

    return portas

def salvar_dados(dados, formato='json', arquivo='portas.json'):

    if formato == 'json':
        with open(arquivo, 'w') as jsonfile:
            json.dump(dados, jsonfile, indent=4)


url = "https://pt.wikipedia.org/wiki/Lista_de_portas_dos_protocolos_TCP_e_UDP"
portas = encontra_portas(url)
salvar_dados(portas, formato='json', arquivo='portas.json')
