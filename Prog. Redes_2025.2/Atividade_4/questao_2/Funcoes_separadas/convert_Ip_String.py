def ip_to_str(ip_bytes):
    
    if sys.byteorder == 'little':
        return ".".join(map(str, ip_bytes))
    else:
        # A ordem dos bytes já está correta
        return ".".join(map(str, ip_bytes))