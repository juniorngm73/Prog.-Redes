import os

RAID_CONFIG = {
    'num_discos': 0,
    'tam_disco': 0,
    'tam_bloco': 0,
    'pasta': '',
    # Índice do disco removido (incluindo o disco de paridade). -1 significa nenhum removido.
    'removed_disk_index': -1
}

def _remove_dir_recursive(path):
    """
    Remove recursivamente um diretório e todo o seu conteúdo usando as funções do módulo os.
    """
    if not os.path.exists(path):
        return

    # Itera sobre todos os arquivos e subdiretórios no caminho
    for entry in os.listdir(path):
        entry_path = os.path.join(path, entry)
        if os.path.isdir(entry_path):
            # Se for um subdiretório, chama recursivamente
            _remove_dir_recursive(entry_path)
        else:
            # Se for um arquivo, remove
            os.remove(entry_path)

    # Finalmente, remove o diretório vazio
    os.rmdir(path)


def _load_raid_config(pasta):
    """Carrega as configurações do RAID a partir de um arquivo de configuração."""
    config_file = os.path.join(pasta, 'raid_config.txt')
    if not os.path.exists(config_file):
        print(f"Erro: Arquivo de configuração não encontrado em '{config_file}'.")
        return False

    try:
        with open(config_file, 'r') as f:
            lines = f.readlines()
            # Espera 3 linhas: num_discos, tam_disco, tam_bloco
            RAID_CONFIG['num_discos'] = int(lines[0].strip())
            RAID_CONFIG['tam_disco'] = int(lines[1].strip())
            RAID_CONFIG['tam_bloco'] = int(lines[2].strip())
            RAID_CONFIG['pasta'] = pasta
            RAID_CONFIG['removed_disk_index'] = -1  # Reseta o estado do disco removido ao carregar
            print(
                f"Configuração RAID carregada: {RAID_CONFIG['num_discos']} discos, {RAID_CONFIG['tam_disco']} bytes, Bloco {RAID_CONFIG['tam_bloco']} bytes.")
            return True
    except Exception as e:
        print(f"Erro ao ler arquivo de configuração: {e}")
        return False


def _save_raid_config():
    """Salva as configurações do RAID em um arquivo de configuração."""
    pasta = RAID_CONFIG['pasta']
    config_file = os.path.join(pasta, 'raid_config.txt')
    try:
        with open(config_file, 'w') as f:
            f.write(str(RAID_CONFIG['num_discos']) + '\n')
            f.write(str(RAID_CONFIG['tam_disco']) + '\n')
            f.write(str(RAID_CONFIG['tam_bloco']) + '\n')
        print(f"Configuração salva em '{config_file}'.")
    except Exception as e:
        print(f"Erro ao salvar arquivo de configuração: {e}")


def _open_disk_file(disco_index, mode):
    """Abre o arquivo do disco, tratando o disco removido."""
    pasta = RAID_CONFIG['pasta']
    filename = os.path.join(pasta, f"disco{disco_index}.bin")

    # Simula a falha de acesso se o disco estiver removido
    if RAID_CONFIG['removed_disk_index'] == disco_index:
        return None  # Retorna None para simular a falha de E/S

    # Tenta abrir o arquivo normalmente
    try:
        return open(filename, mode)
    except FileNotFoundError:
        # Isto não deve acontecer após a inicialização, mas é uma proteção
        return None
    except Exception as e:
        print(f"Erro ao abrir disco{disco_index}.bin: {e}")
        return None


def _calculate_parity_block(block_num, tam_bloco, num_discos):
    """
    Calcula o bloco de paridade para um dado número de bloco.

    Lê o bloco 'block_num' de todos os discos de dados e calcula o XOR.
    """
    num_dados = num_discos - 1
    current_parity = bytearray(tam_bloco)

    for i in range(num_dados):
        f_disk = _open_disk_file(i, 'rb')
        if f_disk is None:

            continue

        try:
            f_disk.seek(block_num * tam_bloco)
            data_block = f_disk.read(tam_bloco)

            for j in range(len(data_block)):
                current_parity[j] ^= data_block[j]
        finally:
            if f_disk:
                f_disk.close()

    return bytes(current_parity)


def _update_parity_optimized(disk_index, block_num, tam_bloco, old_data, new_data):
    """
    Atualiza o bloco de paridade usando a técnica 'XOR Write' (P_new = P_old XOR D_old XOR D_new).

    """
    pasta = RAID_CONFIG['pasta']
    num_discos = RAID_CONFIG['num_discos']
    tam_disco = RAID_CONFIG['tam_disco']
    parity_disk_index = num_discos - 1

    # 1. Obter o bloco de paridade antigo (P_old)
    f_parity = _open_disk_file(parity_disk_index, 'r+b')
    if f_parity is None:
        print("Aviso: Disco de paridade indisponível. A escrita no disco removido não atualizará a paridade.")
        return  # Não é possível atualizar a paridade

    try:
        f_parity.seek(block_num * tam_bloco)
        p_old = bytearray(f_parity.read(tam_bloco))

        # 2. Calcular a nova paridade (P_new = P_old XOR D_old XOR D_new)
        p_new = bytearray(tam_bloco)
        for i in range(tam_bloco):
            # old_data[i] XOR new_data[i] XOR p_old[i]
            p_new[i] = old_data[i] ^ new_data[i] ^ p_old[i]

        # 3. Reescrever o bloco de paridade
        f_parity.seek(block_num * tam_bloco)
        f_parity.write(p_new)
        print(f"Paridade atualizada no disco {parity_disk_index}, bloco {block_num}.")

    finally:
        if f_parity:
            f_parity.close()


# --- Funções do Menu (Implementação Principal) ---

def inicializaRAID(num_discos, tam_disco, tam_bloco, pasta="raid4_files"):
    """
    Inicializa o RAID 4 criando os arquivos dos discos e o arquivo de configuração.
    """
    if num_discos < 3:
        print("Erro: O RAID 4 requer pelo menos 3 discos (2 de dados + 1 de paridade).")
        return

    if tam_disco % tam_bloco != 0:
        print("Erro: O tamanho do disco deve ser múltiplo do tamanho do bloco.")
        return

    if os.path.exists(pasta):
        print(f"A pasta '{pasta}' já existe. Removendo conteúdo existente...")
        _remove_dir_recursive(pasta)

    os.makedirs(pasta)

    # Salva a configuração no global e no arquivo
    RAID_CONFIG.update({
        'num_discos': num_discos,
        'tam_disco': tam_disco,
        'tam_bloco': tam_bloco,
        'pasta': pasta,
        'removed_disk_index': -1
    })
    _save_raid_config()

    num_dados = num_discos - 1
    print(f"Criando {num_dados} discos de dados e 1 disco de paridade em '{pasta}'...")

    try:
        # 1. Cria e zera todos os discos
        for i in range(num_discos):
            nome_arquivo = os.path.join(pasta, f"disco{i}.bin")
            with open(nome_arquivo, 'wb') as arquivo:
                # Preenche o disco com zeros.
                # Como os discos de dados são zeros, a paridade inicial também será zeros (XOR de zeros).
                arquivo.write(b'\x00' * tam_disco)
            print(f"Disco {i} criado: {nome_arquivo}")

        print("\nRAID 4 inicializado com sucesso!")
        print(f"Capacidade Lógica Total: {num_dados * tam_disco} bytes.")

    except Exception as e:
        print(f"Erro ao inicializar RAID: {e}")


def obtemRAID(pasta):
    """
    Busca os arquivos do RAID e carrega a configuração.
    """
    if not os.path.exists(pasta):
        print(f"Erro: A pasta '{pasta}' não foi encontrada.")
        return False

    return _load_raid_config(pasta)


def escreveRAID(dados, posicao):
    """
    Grava um conjunto de dados no RAID, atualizando a paridade.

    Implementa a lógica de striping (RAID 4).
    """
    if RAID_CONFIG['num_discos'] == 0:
        print("Erro: RAID não inicializado ou obtido.")
        return False

    num_discos = RAID_CONFIG['num_discos']
    tam_disco = RAID_CONFIG['tam_disco']
    tam_bloco = RAID_CONFIG['tam_bloco']
    num_dados = num_discos - 1
    tam_logico = num_dados * tam_disco
    tam_dados = len(dados)

    if posicao < 0 or posicao + tam_dados > tam_logico:
        print(f"Erro: Posição ({posicao}) ou tamanho dos dados ({tam_dados}) inválidos.")
        print(f"Limite lógico do RAID: 0 a {tam_logico - 1}")
        return False

    dados_buffer = bytearray(dados)
    bytes_escritos = 0

    print(f"\nIniciando escrita de {tam_dados} bytes na posição lógica {posicao}...")

    while bytes_escritos < tam_dados:
        pos_atual_logica = posicao + bytes_escritos

        # --- Endereçamento Lógico -> Físico (RAID 4 Striping) ---
        lbn = pos_atual_logica // tam_bloco
        offset_no_bloco = pos_atual_logica % tam_bloco

        # Qual disco de DADOS (0 a num_dados-1)
        disk_index = lbn % num_dados
        # Qual bloco físico nesse disco (Posição vertical)
        pbn = lbn // num_dados

        # Posição física do bloco no arquivo
        pos_bloco_no_disco = pbn * tam_bloco
        pos_escrita_fisica = pos_bloco_no_disco + offset_no_bloco

        # Determina quantos bytes escrever neste disco/bloco/operação
        bytes_livres_no_bloco = tam_bloco - offset_no_bloco
        bytes_restantes = tam_dados - bytes_escritos
        bytes_a_escrever = min(bytes_livres_no_bloco, bytes_restantes)

        # --- Leitura/Escrita e Atualização de Paridade (XOR Write) ---

        # 1. Ler o bloco de dados antigo (D_old)
        f_disk = _open_disk_file(disk_index, 'r+b')

        # Ler o bloco completo do disco de dados para o XOR Write
        d_old = bytearray(tam_bloco)

        if f_disk is not None:
            # Disco de dados ativo: ler D_old
            f_disk.seek(pos_bloco_no_disco)
            d_old = bytearray(f_disk.read(tam_bloco))

            # Garantir que d_old tem o tamanho correto (preenchendo com zeros se o disco for novo/vazio)
            if len(d_old) < tam_bloco:
                d_old.extend(b'\x00' * (tam_bloco - len(d_old)))

            # Criar D_new, que é o d_old com os novos dados
            d_new = bytearray(d_old)
            for i in range(bytes_a_escrever):
                d_new[offset_no_bloco + i] = dados_buffer[bytes_escritos + i]

            # 2. Escrever os novos dados (D_new) no disco
            f_disk.seek(pos_bloco_no_disco)
            f_disk.write(d_new)
            f_disk.close()

            print(f"Escrito {bytes_a_escrever} bytes em disco {disk_index}, bloco {pbn}, offset {offset_no_bloco}")

            # 3. Atualizar Paridade usando a otimização XOR Write
            _update_parity_optimized(disk_index, pbn, tam_bloco, d_old, d_new)

        else:
            # Disco de dados removido (SIMULAÇÃO DE FALHA)
            print(
                f"AVISO: Disco de dados {disk_index} removido. A escrita será efetuada apenas na paridade (para futura reconstrução).")


            f_parity = _open_disk_file(num_discos - 1, 'r+b')
            if f_parity:
                try:
                    f_parity.seek(pos_bloco_no_disco)
                    p_old = bytearray(f_parity.read(tam_bloco))
                    if len(p_old) < tam_bloco:
                        p_old.extend(b'\x00' * (tam_bloco - len(p_old)))

                    p_new = bytearray(p_old)


                    for i in range(bytes_a_escrever):
                        data_byte = dados_buffer[bytes_escritos + i]
                        # D_antigo_no_bloco_falho[i] = 0 (simplesmente forçamos a paridade a "aceitar" a nova data)
                        p_new[offset_no_bloco + i] = p_old[offset_no_bloco + i] ^ data_byte

                    f_parity.seek(pos_bloco_no_disco)
                    f_parity.write(p_new)
                    print(
                        f"Paridade atualizada no disco {num_discos - 1} para compensar escrita em disco falho {disk_index}.")

                finally:
                    f_parity.close()

        # Avança os contadores para a próxima iteração
        bytes_escritos += bytes_a_escrever


def leRAID(posicao, tam_leitura):
    """
    Lê dados do RAID. Se o disco necessário estiver removido, reconstrói os dados
    usando a paridade e os discos remanescentes.
    """
    if RAID_CONFIG['num_discos'] == 0:
        print("Erro: RAID não inicializado ou obtido.")
        return b''

    num_discos = RAID_CONFIG['num_discos']
    tam_disco = RAID_CONFIG['tam_disco']
    tam_bloco = RAID_CONFIG['tam_bloco']
    num_dados = num_discos - 1
    tam_logico = num_dados * tam_disco

    if posicao < 0 or posicao + tam_leitura > tam_logico:
        print(f"Erro: Posição ({posicao}) ou tamanho da leitura ({tam_leitura}) inválidos.")
        print(f"Limite lógico do RAID: 0 a {tam_logico - 1}")
        return b''

    dados_lidos = bytearray()
    bytes_lidos = 0

    print(f"\nIniciando leitura de {tam_leitura} bytes na posição lógica {posicao}...")

    while bytes_lidos < tam_leitura:
        pos_atual_logica = posicao + bytes_lidos

        # --- Endereçamento Lógico -> Físico (RAID 4 Striping) ---
        lbn = pos_atual_logica // tam_bloco  # Logical Block Number
        offset_no_bloco = pos_atual_logica % tam_bloco

        # Qual disco de DADOS (0 a num_dados-1)
        disk_index = lbn % num_dados
        # Qual bloco físico nesse disco (Posição vertical)
        pbn = lbn // num_dados

        pos_bloco_no_disco = pbn * tam_bloco

        # Determina quantos bytes ler nesta iteração
        bytes_restantes_no_bloco = tam_bloco - offset_no_bloco
        bytes_restantes_total = tam_leitura - bytes_lidos
        bytes_a_ler = min(bytes_restantes_no_bloco, bytes_restantes_total)

        data_block = bytearray(tam_bloco)

        f_disk = _open_disk_file(disk_index, 'rb')

        if f_disk is not None:
            # 1. Disco de Dados OK: Leitura direta
            f_disk.seek(pos_bloco_no_disco)
            data_block = bytearray(f_disk.read(tam_bloco))
            f_disk.close()
            print(f"Leitura direta: disco {disk_index}, bloco {pbn}.")

        elif disk_index == RAID_CONFIG['removed_disk_index']:
            # 2. Disco de Dados Falho: Reconstrução (D_falho = P XOR D_restantes)

            # A paridade está no último disco
            parity_disk_index = num_discos - 1

            # Começa a reconstrução com o bloco de paridade
            f_parity = _open_disk_file(parity_disk_index, 'rb')
            if f_parity is None:
                print("ERRO CRÍTICO: Não é possível ler disco falho nem o disco de paridade. Falha Dupla.")
                return b''

            try:
                f_parity.seek(pos_bloco_no_disco)
                data_block = bytearray(f_parity.read(tam_bloco))  # data_block = P
                f_parity.close()
            except Exception as e:
                print(f"Erro ao ler paridade para reconstrução: {e}")
                return b''

            # XOR com todos os outros discos de dados
            for i in range(num_dados):
                if i != disk_index:  # Pula o disco falho (que é o que queremos reconstruir)
                    f_other_disk = _open_disk_file(i, 'rb')
                    if f_other_disk is None:
                        # Outro disco de dados falhou, mas o sistema só suporta uma falha (RAID 4/5)
                        print(f"ERRO CRÍTICO: Falha no disco {i} durante a reconstrução. Falha Dupla.")
                        return b''

                    try:
                        f_other_disk.seek(pos_bloco_no_disco)
                        other_data = f_other_disk.read(tam_bloco)

                        # Aplica XOR (data_block = P XOR D_restante_1 XOR D_restante_2...)
                        for j in range(len(other_data)):
                            data_block[j] ^= other_data[j]
                    finally:
                        if f_other_disk:
                            f_other_disk.close()

            print(f"RECONSTRUÇÃO: Dados reconstruídos para disco {disk_index}, bloco {pbn}.")

        else:
            # Posição de leitura caiu em um disco de paridade removido (tecnicamente) ou outro erro
            # No RAID 4/5, a leitura deve sempre cair em um disco de DADOS (0 a num_dados-1)
            print(f"ERRO DE LÓGICA: Leitura tentada em disco de índice {disk_index}.")
            return b''

        # Adiciona o segmento lido/reconstruído ao resultado
        dados_lidos.extend(data_block[offset_no_bloco:offset_no_bloco + bytes_a_ler])
        bytes_lidos += bytes_a_ler

    return bytes(dados_lidos)


def removeDiscoRAID(disco_index):
    """
    Simula a falha de um disco, definindo seu índice no estado global.
    """
    if RAID_CONFIG['num_discos'] == 0:
        print("Erro: RAID não inicializado ou obtido.")
        return

    if disco_index < 0 or disco_index >= RAID_CONFIG['num_discos']:
        print(f"Erro: Índice do disco inválido. Use de 0 a {RAID_CONFIG['num_discos'] - 1}.")
        return

    if RAID_CONFIG['removed_disk_index'] != -1:
        print(f"Erro: Já existe um disco removido (disco {RAID_CONFIG['removed_disk_index']}).")
        return

    # Renomeia o arquivo para simular a indisponibilidade, mas o mantém para reconstrução
    pasta = RAID_CONFIG['pasta']
    original_name = os.path.join(pasta, f"disco{disco_index}.bin")
    failed_name = os.path.join(pasta, f"disco{disco_index}.FAILED")

    try:
        os.rename(original_name, failed_name)
        RAID_CONFIG['removed_disk_index'] = disco_index
        if disco_index == RAID_CONFIG['num_discos'] - 1:
            print(
                f"SUCESSO: Disco de PARIDADE ({disco_index}) removido/falho. O RAID continua funcional, mas sem tolerância a falhas.")
        else:
            print(f"SUCESSO: Disco de DADOS ({disco_index}) removido/falho. O RAID está em modo de degradação.")

    except FileNotFoundError:
        print(f"Erro: Arquivo {original_name} não encontrado.")
    except Exception as e:
        print(f"Erro ao simular remoção do disco: {e}")


def constroiDiscoRAID():
    """
    Reconstrói o disco falho usando os discos remanescentes e o disco de paridade.
    """
    if RAID_CONFIG['num_discos'] == 0:
        print("Erro: RAID não inicializado ou obtido.")
        return

    removed_index = RAID_CONFIG['removed_disk_index']

    if removed_index == -1:
        print("Nenhum disco removido para reconstruir.")
        return

    num_discos = RAID_CONFIG['num_discos']
    tam_disco = RAID_CONFIG['tam_disco']
    tam_bloco = RAID_CONFIG['tam_bloco']
    num_blocos = tam_disco // tam_bloco

    pasta = RAID_CONFIG['pasta']
    original_name = os.path.join(pasta, f"disco{removed_index}.bin")
    failed_name = os.path.join(pasta, f"disco{removed_index}.FAILED")

    print(f"\nIniciando reconstrução do disco {removed_index}...")


    if os.path.exists(failed_name):
        try:
            os.rename(failed_name, original_name)
        except Exception as e:
            print(f"Erro ao renomear disco falho de volta: {e}")
            return
    else:

        try:
            with open(original_name, 'wb') as arquivo:
                arquivo.write(b'\x00' * tam_disco)
        except Exception as e:
            print(f"Erro ao criar novo arquivo de disco: {e}")
            return


    f_new_disk = open(original_name, 'r+b')

    try:
        for pbn in range(num_blocos):
            # O bloco reconstruído começa com o bloco de paridade
            reconstructed_block = bytearray(tam_bloco)

            # --- Lógica de Reconstrução ---

            # 2a. Carrega o bloco de paridade
            parity_disk_index = num_discos - 1
            f_parity = _open_disk_file(parity_disk_index, 'rb')
            if f_parity is None:
                # O disco de paridade também falhou, o que é uma falha dupla
                print("ERRO CRÍTICO: Disco de paridade indisponível. Reconstrução Impossível.")
                f_new_disk.close()
                return

            try:
                f_parity.seek(pbn * tam_bloco)
                parity_data = f_parity.read(tam_bloco)
                reconstructed_block.extend(parity_data)

                # Ajusta o tamanho caso o disco de paridade seja menor que tam_bloco (último bloco)
                reconstructed_block = bytearray(reconstructed_block[:tam_bloco])

                # XOR com os dados de paridade (P)
                for j in range(len(parity_data)):
                    reconstructed_block[j] = parity_data[j]
            finally:
                if f_parity:
                    f_parity.close()

            # 2b. XOR com os discos de dados remanescentes
            for i in range(num_discos - 1):  # Itera apenas sobre discos de DADOS
                if i != removed_index:  # Pula o disco que está sendo reconstruído
                    f_other_disk = _open_disk_file(i, 'rb')
                    if f_other_disk is None:
                        # Outro disco falhou!
                        print(f"ERRO CRÍTICO: Falha no disco {i} durante a reconstrução. Falha Dupla.")
                        f_new_disk.close()
                        return

                    try:
                        f_other_disk.seek(pbn * tam_bloco)
                        other_data = f_other_disk.read(tam_bloco)

                        # Aplica XOR (R = P XOR D_restante_1 XOR D_restante_2...)
                        for j in range(len(other_data)):
                            reconstructed_block[j] ^= other_data[j]
                    finally:
                        if f_other_disk:
                            f_other_disk.close()

            # 2c. Escreve o bloco reconstruído no novo disco
            f_new_disk.seek(pbn * tam_bloco)
            f_new_disk.write(reconstructed_block)

            if (pbn + 1) % 100 == 0:
                print(f"  ... Bloco {pbn} reconstruído ({pbn * 100 // num_blocos}%)")

        RAID_CONFIG['removed_disk_index'] = -1  # Limpa o estado de disco removido
        print(f"SUCESSO: Disco {removed_index} reconstruído completamente.")

    except Exception as e:
        print(f"Erro durante a reconstrução: {e}")
    finally:
        f_new_disk.close()


def menu_raid():
    """
    Função principal que apresenta o menu ao usuário.
    """
    print("\n--- Simulador RAID 4 ---")

    while True:
        status = "OK" if RAID_CONFIG['num_discos'] > 0 else "INATIVO"
        removed_status = f"FALHO (Disco {RAID_CONFIG['removed_disk_index']})" if RAID_CONFIG[
                                                                                     'removed_disk_index'] != -1 else "NENHUM"

        print(f"\n--- Menu RAID (Status: {status} | Falha: {removed_status}) ---")
        if RAID_CONFIG['num_discos'] > 0:
            print(
                f"  Config: {RAID_CONFIG['num_discos']} Discos, {RAID_CONFIG['tam_bloco']} bytes/bloco, Pasta: {RAID_CONFIG['pasta']}")

        print("1. Inicializar RAID")
        print("2. Obter RAID Existente")
        print("3. Escrever Dados no RAID")
        print("4. Ler Dados do RAID")
        print("5. Remover Disco (Simular Falha)")
        print("6. Reconstruir Disco")
        print("7. Sair")

        choice = input("Escolha uma opção: ")

        try:
            if choice == '1':
                nd = int(input("Número de discos (>= 3): "))
                td = int(input("Tamanho de cada disco (bytes): "))
                tb = int(input("Tamanho do bloco (bytes): "))
                pasta = input("Nome da pasta para os arquivos: ")
                inicializaRAID(nd, td, tb, pasta)

            elif choice == '2':
                pasta = input("Nome da pasta do RAID existente: ")
                obtemRAID(pasta)

            elif choice == '3':
                if RAID_CONFIG['num_discos'] == 0:
                    print("Por favor, inicialize ou obtenha o RAID primeiro.")
                    continue

                data_str = input("Dados a serem gravados (texto simples): ")
                dados = data_str.encode('utf-8')
                posicao = int(input("Posição de início (em bytes): "))
                escreveRAID(dados, posicao)

            elif choice == '4':
                if RAID_CONFIG['num_discos'] == 0:
                    print("Por favor, inicialize ou obtenha o RAID primeiro.")
                    continue

                posicao = int(input("Posição de início da leitura (em bytes): "))
                tam_leitura = int(input("Quantidade de bytes para ler: "))

                dados = leRAID(posicao, tam_leitura)
                if dados:
                    print(f"\nDados lidos ({len(dados)} bytes): {dados}")
                    try:
                        print(f"Interpretação como texto: {dados.decode('utf-8')}")
                    except UnicodeDecodeError:
                        print("Não foi possível decodificar como UTF-8 (contém bytes nulos ou binários).")
                else:
                    print("Nenhum dado lido (verifique os limites ou falhas críticas).")

            elif choice == '5':
                if RAID_CONFIG['num_discos'] == 0:
                    print("Por favor, inicialize ou obtenha o RAID primeiro.")
                    continue

                idx = int(input(f"Índice do disco a remover (0 a {RAID_CONFIG['num_discos'] - 1}): "))
                removeDiscoRAID(idx)

            elif choice == '6':
                constroiDiscoRAID()

            elif choice == '7':
                print("Saindo do simulador.")
                break

            else:
                print("Opção inválida. Tente novamente.")

        except ValueError:
            print("Entrada inválida. Certifique-se de inserir números onde necessário.")
        except Exception as e:
            print(f"Ocorreu um erro: {e}")


# Execução do menu
if __name__ == "__main__":
    menu_raid()
