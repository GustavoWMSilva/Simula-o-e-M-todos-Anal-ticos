import sys
import yaml

# Gerador de Números Pseudo-Aleatórios: Congruência Linear
# Xn+1c= (aXn+c) mod m
A = 1255
C = 4164
M = 1048576576

previous = 5000

# G/G/S/K
S = 1 # Número de servidores
K = 5 # Capacidade de clientes da fila  

# Tempo de chegada de novos clientes
CHEGADA_ENTRE_INICIAL = 2
CHEGADA_ENTRE_FINAL = 5

# Tempo para atendimento dos clientes
SAIDA_ENTRE_INICIAL = 3
SAIDA_ENTRE_FINAL = 5

tamFila = 0
nroDeFilas = 1
escalonador = []
filaClientes = []
times = [0] * (K+1)
clientesPerdidos = 0

TEMPO_GLOBAL = 0

# Estado Inicial
TEMPO_CHEGADA = 2
ultimo_tempo_global = 0

class Evento():
    def __init__(self, tipoEvento, tempo):
        self.tipoEvento = tipoEvento
        self.tempo = tempo

    def __str__(self):
        return f"Evento: {self.tipoEvento}\nTempo: {self.tempo}\n"

def nextRandon():
    global previous
    previous = (A*previous + C) % M
    return previous / M

# Fórmula de conversão
def sorteio(evento):
    if evento.tipoEvento == "Chegada":
        return (CHEGADA_ENTRE_FINAL - CHEGADA_ENTRE_INICIAL) * nextRandon() + CHEGADA_ENTRE_INICIAL
    return (SAIDA_ENTRE_FINAL - SAIDA_ENTRE_INICIAL) * nextRandon() + SAIDA_ENTRE_INICIAL

# Chegada de um cliente
def chegada(evento):
    global clientesPerdidos
    global tamFila
    global ultimo_tempo_global
    
    if tamFila <= K:
        times[tamFila] = times[tamFila] + (TEMPO_GLOBAL - ultimo_tempo_global)

    ultimo_tempo_global = TEMPO_GLOBAL

    if tamFila < K:
        tamFila = tamFila + 1
        if tamFila <= S:
            # Agenda o atendimento do cliente
            escalonador.append(Evento("Saida", TEMPO_GLOBAL + sorteio(evento)))
        else:
            clientesPerdidos += 1

    # Agenda a chegada do cliente
    escalonador.append(Evento("Chegada", TEMPO_GLOBAL + sorteio(evento)))
    # Ordena o escalonador de acordo com o tempo
    escalonador.sort(key=lambda x: x.tempo)


# Atendimento de um cliente
def saida(evento):
    global ultimo_tempo_global
    global tamFila

    if tamFila <= K:
        times[tamFila] = times[tamFila] + (TEMPO_GLOBAL - ultimo_tempo_global)

    ultimo_tempo_global = TEMPO_GLOBAL
    
    tamFila -= 1
    if tamFila >= S:
        # Agenda o atendimento do cliente
        escalonador.append(Evento("Saida", TEMPO_GLOBAL + sorteio(evento)))
    
    # Ordena o escalonador de acordo com o tempo
    escalonador.sort(key=lambda x: x.tempo)


def leituraArquivo(arquivo):
    global S, K, CHEGADA_ENTRE_INICIAL, CHEGADA_ENTRE_FINAL, SAIDA_ENTRE_INICIAL, SAIDA_ENTRE_FINAL, TEMPO_CHEGADA
    with open(arquivo, 'r') as f:
        dados = yaml.safe_load(f)

    fila = dados['Q1']

    S = fila.get('servers') # Numero de servidores
    K = fila.get('capacity') # Capacidade da fila
    CHEGADA_ENTRE_INICIAL = fila.get('minArrival')
    CHEGADA_ENTRE_FINAL = fila.get('maxArrival')
    SAIDA_ENTRE_INICIAL = fila.get('minService')
    SAIDA_ENTRE_FINAL = fila.get('maxService')
    TEMPO_CHEGADA = fila.get('tempoChegada') # Tempo de chegada do primeiro cliente

    return S ,K ,CHEGADA_ENTRE_INICIAL ,CHEGADA_ENTRE_FINAL ,SAIDA_ENTRE_INICIAL ,SAIDA_ENTRE_FINAL ,TEMPO_CHEGADA


def main():
    global TEMPO_GLOBAL

    if len(sys.argv) != 2:
        print("Utilize o comando $ python3 main.py <caminho_arquivo>.yml")
        sys.exit(1)

    arquivo = sys.argv[1]
    try:
        leituraArquivo(arquivo)
    except Exception as e:
        print(f"Erro ao ler o arquivo .yml: {e}")
        sys.exit(1)

    # Criterio de Parada
    count = 100000

    # Primeiro cliente chegando...
    escalonador.append(Evento("Chegada", TEMPO_CHEGADA))

    while(count > 0):
        count = count - 1
        
        evento = escalonador.pop(0)
        TEMPO_GLOBAL = evento.tempo
        filaClientes.append(evento)
        
        if evento.tipoEvento == "Chegada":
            chegada(evento)
        elif evento.tipoEvento == "Saida":
            saida(evento)

    print("Tempo Global do Sistema:", TEMPO_GLOBAL)
    print("Clientes perdidos: ", clientesPerdidos, "\n")
    print("Simulação (Estado - Tempo - Probabilidade)")

    for i in range(K+1):      
        print(f"{i}: {times[i]} ({round((times[i] / TEMPO_GLOBAL) * 100, 2)}%)\n ")
    
if __name__=="__main__":
    main()
