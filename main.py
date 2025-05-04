import sys
import yaml

from fila import Fila

# Gerador de Números Pseudo-Aleatórios: Congruência Linear
# Xn+1c= (aXn+c) mod m
A = 1255
C = 4164
M = 1048576576

previous = 5000

filas = []

nroDeFilas = 1
escalonador = []
filaClientes = []

TEMPO_GLOBAL = 0
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
        return (filas[0].ChegadaFinal() - filas[0].ChegadaInicio()) * nextRandon() + filas[0].ChegadaInicio()
    return (filas[1].AtendimentoFinal() - filas[1].AtendimentoInicio()) * nextRandon() + filas[1].AtendimentoInicio()


# Chegada de um cliente
def chegada(evento):
    global ultimo_tempo_global
    
    if filas[0].Status() <= filas[0].Capacity():
        tempoFilaX = filas[0].ArrayDeTempos()
        tempoFilaX[filas[0].Status()] = tempoFilaX[filas[0].Status()] + (TEMPO_GLOBAL - ultimo_tempo_global)

    ultimo_tempo_global = TEMPO_GLOBAL

    if filas[0].Status() < filas[0].Capacity():
        # Aumenta em 1 cliente a fila Q1
        filas[0].In()
        if filas[0].Status() <= filas[0].Servers():
            # Agenda o atendimento do cliente
            escalonador.append(Evento("Passagem", TEMPO_GLOBAL + sorteio(evento)))
        else:
            filas[0].Loss()

    # Agenda a chegada do cliente
    escalonador.append(Evento("Chegada", TEMPO_GLOBAL + sorteio(evento)))
    # Ordena o escalonador de acordo com o tempo
    escalonador.sort(key=lambda x: x.tempo)


# Atendimento de um cliente
def saida(evento):
    global ultimo_tempo_global

    if filas[1].Status() <= filas[1].Capacity():
        tempoFilaY = filas[1].ArrayDeTempos()
        tempoFilaY[filas[1].Status()] = tempoFilaY[filas[1].Status()] + (TEMPO_GLOBAL - ultimo_tempo_global)

    ultimo_tempo_global = TEMPO_GLOBAL
    
    filas[1].Out()
    if filas[1].Status() >= filas[1].Servers():
        # Agenda o atendimento do cliente
        escalonador.append(Evento("Saida", TEMPO_GLOBAL + sorteio(evento)))
    
    # Ordena o escalonador de acordo com o tempo
    escalonador.sort(key=lambda x: x.tempo)


# Passagem para outra fila
def passagem(evento):
    global ultimo_tempo_global

    # Acumula tempo
    #if filas[1].Status() <= filas[1].Capacity():
    #    tempoFilaY = filas[1].ArrayDeTempos()
    #    tempoFilaY[filas[1].Status()] = tempoFilaY[filas[1].Status()] + (TEMPO_GLOBAL - ultimo_tempo_global)

    #ultimo_tempo_global = TEMPO_GLOBAL
    filas[0].Out()
    if filas[0].Status() >= filas[0].Servers():
        escalonador.append(Evento("Passagem", TEMPO_GLOBAL + sorteio(evento)))
    
    if filas[1].Status() < filas[1].Capacity():
        filas[1].In()
        if filas[1].Status() <= filas[1].Servers():
            escalonador.append(Evento("Saida", TEMPO_GLOBAL + sorteio(evento)))
    else:
        filas[1].Loss()    


def leituraArquivo(arquivo):
    global filas, TEMPO_CHEGADA
    with open(arquivo, 'r') as f:
        dados = yaml.safe_load(f)

    secaoFilasYml = dados['queues']
    secaoArrivalsYml = dados.get('arrivals', {})
    
    for id, config in secaoFilasYml.items():
        min_arrival = min_arrival = config.get('minArrival')
        max_arrival = max_arrival = config.get('maxArrival')

        fila = Fila(
            IdentificadorFila = id,
            S = config['servers'],
            K = config['capacity'],
            CHEGADA_ENTRE_INICIAL = min_arrival,
            CHEGADA_ENTRE_FINAL = max_arrival,
            SAIDA_ENTRE_INICIAL = config['minService'],
            SAIDA_ENTRE_FINAL = config['maxService']
        )
        filas.append(fila)

    if secaoArrivalsYml:
        _, valor = next(iter(secaoArrivalsYml.items()))
        TEMPO_CHEGADA = valor


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

    for i in range(len(filas)):
        print(filas[i])
    
    # Criterio de Parada
    count = 100

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
        else:
            passagem(evento)

    print("Tempo Global do Sistema:", TEMPO_GLOBAL)
    # print("Clientes perdidos: ", clientesPerdidos, "\n")
    # print("Simulação (Estado - Tempo - Probabilidade)")

    # for i in range(K+1):      
    #     print(f"{i}: {times[i]} ({round((times[i] / TEMPO_GLOBAL) * 100, 2)}%)\n ")
    
if __name__=="__main__":
    main()
