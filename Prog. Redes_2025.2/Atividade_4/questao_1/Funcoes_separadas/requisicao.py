import os, json, re, requests
from urllib.parse import urlparse


def requisicao(url):
    
    print(f"\nTentando acessar a URL: {url}")

    try:
        response = requests.get(url, timeout=10, stream=True) 
        response.raise_for_status()
        print("Requisição bem-sucedida.")
        return response
    except requests.exceptions.RequestException as e:
        print(f" Erro na requisição para {url}: {e}")
        return None