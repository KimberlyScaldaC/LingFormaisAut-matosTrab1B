from collections import defaultdict, deque


def ler_afnd(caminho_arquivo):
    # Lê o arquivo do AFND e extrai informações
    with open(caminho_arquivo, 'r') as arquivo:
        linhas = arquivo.readlines()

    # Extrai os estados, estado inicial e estados finais
    estados = linhas[0].strip().split(
    )  # Linha 0: estados separados por espaço
    estado_inicial = linhas[1].strip()  # Linha 1: estado inicial
    estados_finais = set(linhas[2].strip().split())  # Linha 2: estados finais

    # Cria um dicionário de transições usando defaultdict
    transicoes = defaultdict(lambda: defaultdict(set))
    # Popula o dicionário de transições com base nas linhas restantes
    for linha in linhas[3:]:
        atual, simbolo, proximo_estado = linha.strip().split()
        if simbolo in {'0', '1', 'h'}:  # Verifica se o símbolo é válido
            transicoes[atual][simbolo].add(proximo_estado)

    return estados, estado_inicial, estados_finais, transicoes


def fechamento_epsilon(estados, transicoes):
    # Calcula o fechamento épsilon para um conjunto de estados
    fechamento = set(estados)
    pilha = list(estados)  # Usa uma pilha para explorar estados
    while pilha:
        estado = pilha.pop()
        # Adiciona estados acessíveis via transição épsilon
        for proximo_estado in transicoes[estado]['h']:
            if proximo_estado not in fechamento:
                fechamento.add(proximo_estado)
                pilha.append(proximo_estado)
    return frozenset(
        fechamento)  # Retorna como um frozenset para garantir unicidade


def mover(estados, simbolo, transicoes):
    # Calcula os próximos estados após uma transição com um símbolo específico
    resultado = set()
    for estado in estados:
        resultado.update(transicoes[estado][simbolo])
    return frozenset(resultado)  # Retorna como um frozenset


def converter_afnd_para_afd(estados, estado_inicial, estados_finais,
                            transicoes):
    # Calcula o fechamento épsilon do estado inicial
    fechamento_inicial = fechamento_epsilon([estado_inicial], transicoes)
    # Fila para explorar estados não marcados
    estados_nao_marcados = deque([fechamento_inicial])
    mapa_estados = {
        fechamento_inicial: f'q{formatar_conjunto_estados(fechamento_inicial)}'
    }
    # Dicionário para armazenar transições do AFD
    transicoes_afd = {}
    # Conjunto para armazenar estados finais do AFD
    estados_finais_afd = set()

    while estados_nao_marcados:
        # Remove o próximo estado da fila
        atual = estados_nao_marcados.popleft()
        rotulo_atual = mapa_estados[atual]
        # Marca o estado como final se algum dos seus estados é final no AFND
        if any(estado in estados_finais for estado in atual):
            estados_finais_afd.add(rotulo_atual)

        for simbolo in '01':  # Processa apenas os símbolos 0 e 1
            proximos_estados = mover(atual, simbolo, transicoes)
            fechamento_proximo = fechamento_epsilon(proximos_estados,
                                                    transicoes)
            if fechamento_proximo:
                # Se o próximo conjunto de estados não está no mapeamento, adiciona-o
                if fechamento_proximo not in mapa_estados:
                    rotulo_proximo = f'q{formatar_conjunto_estados(fechamento_proximo)}'
                    mapa_estados[fechamento_proximo] = rotulo_proximo
                    estados_nao_marcados.append(fechamento_proximo)
                # Adiciona a transição ao dicionário do AFD
                transicoes_afd[(rotulo_atual,
                                simbolo)] = mapa_estados[fechamento_proximo]

    return transicoes_afd, estados_finais_afd, mapa_estados


def formatar_conjunto_estados(conjunto_estados):
    """ Formata o conjunto de estados para criar o nome do estado no AFD. """
    if len(conjunto_estados) == 1:
        # Se o conjunto tem apenas um estado, usa o formato normal qX
        return next(iter(conjunto_estados)).replace('q', '')
    else:
        # Se o conjunto tem múltiplos estados, concatena os números dos estados
        return ''.join(
            sorted(estado.replace('q', '') for estado in conjunto_estados))


def escrever_afd(caminho_arquivo, transicoes_afd, estados_finais_afd,
                 mapa_estados, estado_inicial, transicoes):
    # Ordena os estados do AFD
    estados = sorted(mapa_estados.values())
    # Determina o estado inicial do AFD
    estado_inicial_afd = mapa_estados[frozenset(
        fechamento_epsilon([estado_inicial], transicoes))]

    # Abre o arquivo para escrita
    with open(caminho_arquivo, 'w') as arquivo:
        linhas = []

        # Adiciona a lista de estados
        linhas.append(" ".join(estados))
        # Adiciona o estado inicial
        linhas.append(estado_inicial_afd)
        # Adiciona os estados finais
        linhas.append(" ".join(sorted(estados_finais_afd)))

        # Adiciona as transições do AFD
        for (origem, simbolo), destino in transicoes_afd.items():
            linhas.append(f"{origem} {simbolo} {destino}")

        # Escreve todas as linhas
        arquivo.write("\n".join(linhas))


def reconhecer_palavras(caminho_arquivo, transicoes_afd, estado_inicial_afd,
                        estados_finais_afd):
    # Lê as palavras e verifica se são aceitas pelo AFD
    resultados = []
    with open(caminho_arquivo, 'r') as arquivo:
        palavras = arquivo.readlines()

    for palavra in palavras:
        estado_atual = estado_inicial_afd
        for simbolo in palavra.strip():
            if (estado_atual, simbolo) in transicoes_afd:
                # Move para o próximo estado
                estado_atual = transicoes_afd[(estado_atual, simbolo)]
            else:
                # Transição não válida
                estado_atual = None
                break

        # Verifica se o estado atual é um estado final
        resultado = "aceita" if estado_atual in estados_finais_afd else "não aceita"
        # Ajusta o espaçamento
        resultados.append(f"{palavra.strip():<10} {resultado}")

    return resultados


def main():
    # Caminhos dos arquivos
    caminho_afnd = 'afnd.txt'
    caminho_afd = 'afd.txt'
    caminho_palavras = 'palavras.txt'
    caminho_resultados = 'resultados.txt'

    # Lê o AFND do arquivo
    estados, estado_inicial, estados_finais, transicoes = ler_afnd(
        caminho_afnd)

    # Converte o AFND para AFD
    transicoes_afd, estados_finais_afd, mapa_estados = converter_afnd_para_afd(
        estados, estado_inicial, estados_finais, transicoes)

    # Escreve o AFD no arquivo
    escrever_afd(caminho_afd, transicoes_afd, estados_finais_afd, mapa_estados,
                 estado_inicial, transicoes)

    # Prepara para reconhecer palavras
    estado_inicial_afd = mapa_estados[frozenset(
        fechamento_epsilon([estado_inicial], transicoes))]
    resultados = reconhecer_palavras(caminho_palavras, transicoes_afd,
                                     estado_inicial_afd, estados_finais_afd)

    # Escreve os resultados das palavras reconhecidas
    with open(caminho_resultados, 'w') as arquivo:
        arquivo.write("\n".join(resultados))


if __name__ == "__main__":
    main()
