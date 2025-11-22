def extrair_zip(filepath):
    
    base_name = os.path.basename(filepath)
        
    try:                                                                        # Extração da data do nome do arquivo (YYYY-MM-DD).
        date_parts = []
        for part in base_name.split('_'):
            if len(part) >= 10 and part[4] == '-' and part[7] == '-':
                date_parts.append(part)
        
        if not date_parts:
                                                                               # Tenta um formato de nome de arquivo mais simples.
            date_str_raw = base_name.split('.')[-2].split('-')[-3:] 
            if len(date_str_raw) == 3:
                 date_str = '-'.join(date_str_raw)
            else:
                                                                               # Tenta  extrair YYYYMMDD de qualquer parte do nome.
                 match = re.search(r'(\d{4}[_-]?\d{2}[_-]?\d{2})', base_name)
                 if match:
                      date_str = match.group(1).replace('_', '-').replace('.', '-').replace('--', '-')
                 else:
                      raise ValueError("Não foi possível extrair a data do nome do arquivo para gerar a senha.")
        else:
            date_str = date_parts[0].split('.')[0]
        
        
        date_cleaned = "".join(filter(str.isdigit, date_str))                 # Geração da senha: infected_AAAAMMDD
        if len(date_cleaned) < 8:
            raise ValueError(f"Data extraída inválida: {date_cleaned}")
        
      
        year = date_cleaned[:4]                                               # Garantir YYYYMMDD
        month = date_cleaned[4:6]
        day = date_cleaned[6:8]
        
        password = f"infected_{year}{month}{day}".encode('utf-8')
        print(f"Tentando descompactar com a senha: infected_{year}{month}{day}")

        
        with zipfile.ZipFile(filepath, 'r') as zf:                             # Descompactação
            
            zf.extractall(pwd=password)
            
            pcap_filename = [name for name in zf.namelist() if name.endswith('.pcap')][0]
            print(f"Arquivo descompactado com sucesso: {pcap_filename}")
            return pcap_filename

    except ValueError as e:
        print(f"Erro na extração da data/senha: {e}")
        return None
    
    except Exception as e:
        print(f"Ocorreu um erro inesperado durante a descompactação: {e}")
        return None