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
    def __init__(self, fila, tipoEvento, tempo, filaAnterior = None):
        self.tipoEvento = tipoEvento
        self.tempo = tempo
        self.fila = fila
        self.filaAnterior = filaAnterior

    def __str__(self):
        return f"Evento: {self.tipoEvento}\nTempo: {self.tempo}\n"
    
    def filaDoEvento(self):
        return self.fila
    
    def filaAnteriorDoEvento(self):
        return self.filaAnterior
    

def nextRandon():
    global previous
    previous = (A*previous + C) % M
    return previous / M


# Fórmula de conversão
def sorteio(evento):
    filaAlvo, _ = procuraFilaTarget(evento)

    if evento.tipoEvento == "Chegada":
        return (filaAlvo.ChegadaFinal() - filaAlvo.ChegadaInicio()) * nextRandon() + filaAlvo.ChegadaInicio() 
    if evento.tipoEvento == "Saida":
        return (filaAlvo.AtendimentoFinal() - filaAlvo.AtendimentoInicio()) * nextRandon() + filaAlvo.AtendimentoInicio()

    # tipoEvento == Passagem
    return (filaAlvo.AtendimentoFinal() - filaAlvo.AtendimentoInicio()) * nextRandon() + filaAlvo.AtendimentoInicio() 


def procuraFilaTarget(evento):
    filaEvento = evento.filaDoEvento()
    filaAntecedente = evento.filaAnteriorDoEvento()
    filaAnalisada = None

    for i in range(len(filas)):
        if filas[i].getIdentificadorFila() == filaEvento:
            filaAnalisada = filas[i]

    return filaAnalisada, filaAntecedente

# Chegada de um cliente
def chegada(evento):
    global ultimo_tempo_global

    filaAnalisada, _ = procuraFilaTarget(evento)

    # Acumula tempo    
    if filaAnalisada.Status() <= filaAnalisada.Capacity():
        for i in range(len(filas)):
            tempoFilaAux = filas[i].ArrayDeTempos()
            tempoFilaAux[filas[i].Status()] = tempoFilaAux[filas[i].Status()] + (TEMPO_GLOBAL - ultimo_tempo_global)

    ultimo_tempo_global = TEMPO_GLOBAL
    
    if filaAnalisada.Status() < filaAnalisada.Capacity():
        # Aumenta em 1 cliente a fila Q1
        filaAnalisada.In()
        if filaAnalisada.Status() <= filaAnalisada.Servers():
            if nextRandon() < filaAnalisada.filasTarget[0]['probability']:
                nextFila = filaAnalisada.filasTarget[0]['target']
                # Agenda a passagem do cliente
                escalonador.append(Evento(nextFila, "Passagem", TEMPO_GLOBAL + sorteio(evento), filaAnalisada))
            else:
                # Agenda o atendimento do cliente
                nextFila = filaAnalisada.filasTarget[1]['target']
                escalonador.append(Evento(nextFila, "Passagem", TEMPO_GLOBAL + sorteio(evento), filaAnalisada))
        else:
            filaAnalisada.Loss()
 
    # Agenda a chegada do cliente
    escalonador.append(Evento("Q1","Chegada", TEMPO_GLOBAL + sorteio(evento)))
    # Ordena o escalonador de acordo com o tempo
    escalonador.sort(key=lambda x: x.tempo)


# Atendimento de um cliente
def saida(evento):
    global ultimo_tempo_global

    filaAnalisada, _ = procuraFilaTarget(evento)

    # Acumula tempo
    if filaAnalisada.Status() <= filaAnalisada.Capacity():
        for i in range(len(filas)):
           tempoFilaAux = filas[i].ArrayDeTempos()
           tempoFilaAux[filas[i].Status()] = tempoFilaAux[filas[i].Status()] + (TEMPO_GLOBAL - ultimo_tempo_global)

    ultimo_tempo_global = TEMPO_GLOBAL
    
    filaAnalisada.Out()
    if filaAnalisada.Status() >= filaAnalisada.Servers():
        for i in range(len(filaAnalisada.filasTarget)):
            if nextRandon() < filaAnalisada.filasTarget[i]['probability']:
                # Passagem para outra fila
                escalonador.append(Evento(filaAnalisada.filasTarget[i]['target'], "Passagem", TEMPO_GLOBAL + sorteio(evento), filaAnalisada))
                break
            else:
                # Agenda a saída do cliente
                escalonador.append(Evento(evento.filaDoEvento(), "Saida", TEMPO_GLOBAL + sorteio(evento)))


    # Ordena o escalonador de acordo com o tempo
    escalonador.sort(key=lambda x: x.tempo)


# Passagem para outra fila
def passagem(evento):
    global ultimo_tempo_global

    filaAnalisada, filaAntecedente = procuraFilaTarget(evento)

    # Acumula tempo
    if filaAnalisada.Status() <= filaAnalisada.Capacity():
        for i in range(len(filas)):
           tempoFilaAux = filas[i].ArrayDeTempos()
           tempoFilaAux[filas[i].Status()] = tempoFilaAux[filas[i].Status()] + (TEMPO_GLOBAL - ultimo_tempo_global)

    ultimo_tempo_global = TEMPO_GLOBAL

    filaAntecedente.Out()
    if filaAntecedente.Status() >= filaAntecedente.Servers():
        for i in range(len(filaAnalisada.filasTarget)):
            if nextRandon() < filaAnalisada.filasTarget[i]['probability']:
                escalonador.append(Evento(filaAnalisada.filasTarget[i]['target'] ,"Passagem", TEMPO_GLOBAL + sorteio(evento), filaAnalisada))
                break
            else:
                escalonador.append(Evento(filaAnalisada.filasTarget[len(filaAnalisada.filasTarget)-1]['target'],"Passagem", TEMPO_GLOBAL + sorteio(evento), filaAnalisada))
    
    if filaAnalisada.Status() < filaAnalisada.Capacity():
        filaAnalisada.In()
        if filaAnalisada.Status() <= filaAnalisada.Servers():
            escalonador.append(Evento(filaAnalisada.getIdentificadorFila(), "Saida", TEMPO_GLOBAL + sorteio(evento)))
    else:
        filaAnalisada.Loss()


def leituraArquivo(arquivo):
    global filas, TEMPO_CHEGADA
    with open(arquivo, 'r') as f:
        dados = yaml.safe_load(f)

    secaoFilasYml = dados['queues']
    secaoNetworkYml = dados['network']
    secaoArrivalsYml = dados.get('arrivals', {})

    for id, config in secaoFilasYml.items():
        min_arrival = config.get('minArrival')
        max_arrival = config.get('maxArrival')

        capacidade = 10**3 if config.get('capacity') == -1 else config.get('capacity')

        network = []
        for connection in secaoNetworkYml:
            if connection['source'] == id:
                network.append({
                    'target': connection['target'],
                    'probability': connection['probability']
                })

        fila = Fila(
            IdentificadorFila=id,
            S=config['servers'],
            K=capacidade,
            CHEGADA_ENTRE_INICIAL=min_arrival,
            CHEGADA_ENTRE_FINAL=max_arrival,
            SAIDA_ENTRE_INICIAL=config['minService'],
            SAIDA_ENTRE_FINAL=config['maxService'],
            filasTarget=network
        )
        fila.setFilaTarget(network)
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

    # Criterio de Parada
    count = 100_000

    # Primeiro cliente chegando...
    escalonador.append(Evento("Q1", "Chegada", TEMPO_CHEGADA))

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


    data = []
    for i in range(0, len(filas)): 
        t = filas[i].ArrayDeTempos()
        for j in range(filas[i].Capacity()+1):    
            data.append([filas[i].ArrayDeTempos()[j], (filas[i].ArrayDeTempos()[j]/TEMPO_GLOBAL)*100])
	
    print("Simulação (Estado - Tempo - Probabilidade)")
    for i in range(len(filas)):
        print(f"Fila {i+1}:")
        print(f"Clientes Perdidos na Fila {i+1}: {filas[i].getLoss()}")
        print("Estado | Tempo | Probabilidade")
        total_tempo = 0
        t = filas[i].ArrayDeTempos()
        for j in range(filas[i].Capacity() + 1):
            print(f"{j}       {t[j]}       {round((t[j] / TEMPO_GLOBAL) * 100, 4)}%")
            total_tempo += t[j]
        print()
        total_probabilidade = 0
        for j in range(filas[i].Capacity() + 1):
            total_probabilidade += (t[j] / TEMPO_GLOBAL) * 100

if __name__=="__main__":
    main()
