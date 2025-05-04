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
    def __init__(self, fila, tipoEvento, tempo):
        self.tipoEvento = tipoEvento
        self.tempo = tempo
        self.fila = fila

    def __str__(self):
        return f"Evento: {self.tipoEvento}\nTempo: {self.tempo}\n"
    
    def filaDoEvento(self):
        return self.fila
    

def nextRandon():
    global previous
    previous = (A*previous + C) % M
    return previous / M


# Fórmula de conversão
def sorteio(evento):
    if evento.tipoEvento == "Chegada":
        return (filas[0].ChegadaFinal() - filas[0].ChegadaInicio()) * nextRandon() + filas[0].ChegadaInicio() 
    if evento.tipoEvento == "Saida":
        return (filas.AtendimentoFinal() - filas[1].AtendimentoInicio()) * nextRandon() + filas[1].AtendimentoInicio()

    # tipoEvento == Passagem
    return (filas[0].AtendimentoFinal() - filas[0].AtendimentoInicio()) * nextRandon() + filas[0].AtendimentoInicio() 


def procuraFilaTarget(evento):
    filaEvento = evento.filaDoEvento()
    filaAnalisada = None

    for i in range(len(filas)):
        if filas[i].getIdentificadorFila() == filaEvento:
            filaAnalisada = filas[i]

    # print(f"Fila evento: {filaEvento}")
    # print(f"Fila analisada: {filaAnalisada}")
    return filaAnalisada

# Chegada de um cliente
def chegada(evento):
    global ultimo_tempo_global

    filaAnalisada = procuraFilaTarget(evento)
    print(f"Fila analisada no inicio da chegada: {filaAnalisada}")

    # Acumula tempo    
    if filaAnalisada.Status() <= filaAnalisada.Capacity():
        for i in range(len(filas)):
            tempoFilaAux = filas[i].ArrayDeTempos()
            tempoFilaAux[filas[i].Status()] = tempoFilaAux[filas[i].Status()] + (TEMPO_GLOBAL - ultimo_tempo_global)

    ultimo_tempo_global = TEMPO_GLOBAL
    
    foi_passado = False

    print(f'fila analisada statuso: {filaAnalisada.Status()}')
    print(f'fila analisada capacity: {filaAnalisada.Capacity()}')
    print(f'fila analisada servers: {filaAnalisada.Servers()}')
    if filaAnalisada.Status() < filaAnalisada.Capacity():
        # Aumenta em 1 cliente a fila Q1
        filaAnalisada.In()
        if filaAnalisada.Status() <= filaAnalisada.Servers():

            # if nextRandon() < filaAnalisada.filasTarget[0]['probability']:
            #     filaT = filaAnalisada.filasTarget[0]['target']
            #     # Agenda o atendimento do cliente
            #     escalonador.append(Evento(filaT.getIdentificadorFila(), "Passagem", TEMPO_GLOBAL + sorteio(evento)))
            # else:
            #     # Agenda o atendimento do cliente
            #     filaT = filaAnalisada.filasTarget[1]['target']
            #     escalonador.append(filaT.getIdentificadorFila(), Evento("Passagem", TEMPO_GLOBAL + sorteio(evento)))
            for i in range(len(filaAnalisada.filasTarget)):
                if nextRandon() < filaAnalisada.filasTarget[i]['probability']:
                    # Passagem para outra fila
                    filaT = filaAnalisada.filasTarget[i]['target']
                    escalonador.append(Evento(filaT, "Passagem", TEMPO_GLOBAL + sorteio(evento)))
                    foi_passado = True
                    print(f'filaT: {filaT}')
                    print(f"Fila analisada no if logo após o achar o filaT: {filaAnalisada}")

                
            if not foi_passado:
                # Agenda o atendimento do cliente
                print("ERRROOOOOUUUUUUUU")
                # filaT = filaAnalisada.filasTarget[len(filaAnalisada.filasTarget)-1]['target']
                # escalonador.append(filaT.getIdentificadorFila(), Evento("Passagem", TEMPO_GLOBAL + sorteio(evento)))
        else:
            filaAnalisada.Loss()
    print(f"Fila analisada no fim dessa bagaça: {filaAnalisada}")
    print(f" fila analisada.filasTarget {filaAnalisada.getFilaTarget()}")
    print(f" tamanho da fila analisada.filasTarget {len(filaAnalisada.filasTarget)}")
    print(f'escalonador antes de apensar: {escalonador}')
    print(f'o que vai ser apensado: {filaAnalisada.getIdentificadorFila(),"Chegada", TEMPO_GLOBAL + sorteio(evento)}')
    # Agenda a chegada do cliente
    # return
    escalonador.append(Evento(filaAnalisada.getIdentificadorFila(),"Chegada", TEMPO_GLOBAL + sorteio(evento)))
    # Ordena o escalonador de acordo com o tempo
    escalonador.sort(key=lambda x: x.tempo)


# Atendimento de um cliente
def saida(evento):
    global ultimo_tempo_global

    filaAnalisada = procuraFilaTarget(evento)

    # if filaAnalisada.Status() <= filaAnalisada.Capacity():
    #     for i in range(len(filas)):
    #         tempoFilaAux = filas[i].ArrayDeTempos()
    #         tempoFilaAux[filas[i].Status()] = tempoFilaAux[filas[i].Status()] + (TEMPO_GLOBAL - ultimo_tempo_global)

    # Acumula tempo
    if filas[1].Status() <= filas[1].Capacity():
        for i in range(len(filas)):
           tempoFilaAux = filas[i].ArrayDeTempos()
           tempoFilaAux[filas[i].Status()] = tempoFilaAux[filas[i].Status()] + (TEMPO_GLOBAL - ultimo_tempo_global)

    ultimo_tempo_global = TEMPO_GLOBAL
    
    filas[1].Out()
    if filas[1].Status() >= filas[1].Servers():
        if nextRandon() < filas[1].filasTarget[0]['probability']:
            # Passagem para outra fila
            escalonador.append(Evento("Passagem", TEMPO_GLOBAL + sorteio(evento)))
        else:
            # Agenda o atendimento do cliente
            escalonador.append(Evento("Saida", TEMPO_GLOBAL + sorteio(evento)))

    # Ordena o escalonador de acordo com o tempo
    escalonador.sort(key=lambda x: x.tempo)


# Passagem para outra fila
def passagem(evento):
    global ultimo_tempo_global

    # Acumula tempo
    # if filas[1].Status() <= filas[1].Capacity():
    #     for i in range(len(filas)):
    #        tempoFilaAux = filas[i].ArrayDeTempos()
    #        tempoFilaAux[filas[i].Status()] = tempoFilaAux[filas[i].Status()] + (TEMPO_GLOBAL - ultimo_tempo_global)

    filaAnalisada = procuraFilaTarget(evento)

    # Acumula tempo    
    if filaAnalisada.Status() <= filaAnalisada.Capacity():
        for i in range(len(filas)):
            tempoFilaAux = filas[i].ArrayDeTempos()
            tempoFilaAux[filas[i].Status()] = tempoFilaAux[filas[i].Status()] + (TEMPO_GLOBAL - ultimo_tempo_global)


    ultimo_tempo_global = TEMPO_GLOBAL
    filaT = None

    filaAnalisada.Out()
    if filaAnalisada.Status() >= filaAnalisada.Servers():
        passagem_de_fila_feita = False
        for i in range(len(filaAnalisada.filasTarget)):
            if nextRandon < filaAnalisada.filasTarget[i]['probability']:
                # Passagem para outra fila
                filaT = filaAnalisada.filasTarget[i]['target']
                escalonador.append(Evento(filaT, "Passagem", TEMPO_GLOBAL + sorteio(evento)))
                passagem_de_fila_feita = True
                
                break
        if not passagem_de_fila_feita:
            # Agenda o atendimento do cliente
            escalonador.append(Evento(filaAnalisada.getIdentificadorFila(), "Saida", TEMPO_GLOBAL + sorteio(evento)))
        
    #     print(f"Fila {filaAnalisada.getIdentificadorFila()} -> FilaT {filaT} com probabilidade {filaAnalisada.filasTarget[i]['probability']}")
    #     print(f"Filas na posição 1: {filas[1]}")

    # print(f'fila Target: {filaT}')
    # print(f'fila analisadaaaaaaaaaaa: {filaAnalisada}')

    if filaT is not None:
        if filaT.Status() < filaT.Capacity():
            filaT.In()
            if filaT.Status() <= filaT.Servers():
                escalonador.append(Evento(filaT, "Saida", TEMPO_GLOBAL + sorteio(evento)))
        else:
            filaT.Loss()


def leituraArquivo(arquivo):
    global filas, TEMPO_CHEGADA
    with open(arquivo, 'r') as f:
        dados = yaml.safe_load(f)

    secaoFilasYml = dados['queues']
    secaoNetworkYml = dados['network']
    secaoArrivalsYml = dados.get('arrivals', {})
    
    for id, config in secaoFilasYml.items():
        min_arrival = min_arrival = config.get('minArrival')
        max_arrival = max_arrival = config.get('maxArrival')

        # Adiciona os targets para as filas com base no arquivo de configuração
        network = []
        for connection in secaoNetworkYml:
            if connection['source'] == id:
                network.append({
                    'target': connection['target'],
                    'probability': connection['probability']
                })

        print(f"Fila {id} -> Conexões: {network}")

        print(f'network: {network}')
        for conn in network:
            print(f"{id} -> {conn['target']} tem probabilidade {conn['probability']}")

        fila = Fila(
            IdentificadorFila=id,
            S=config['servers'],
            K=config['capacity'],
            CHEGADA_ENTRE_INICIAL=min_arrival,
            CHEGADA_ENTRE_FINAL=max_arrival,
            SAIDA_ENTRE_INICIAL=config['minService'],
            SAIDA_ENTRE_FINAL=config['maxService'],
            filasTarget=network
        )
        fila.setFilaTarget(network)
        # print(f'fila: {fila}')
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

    #for i in range(len(filas)):
     #   print(filas[i])
    
    # Criterio de Parada
    count = 123456

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
        print("Estado | Tempo | Probabilidade")
        total_tempo = 0
        t = filas[i].ArrayDeTempos()
        for j in range(filas[i].Capacity() + 1):
            print(f"{j}       {t[j]}       {round((t[j] / TEMPO_GLOBAL) * 100, 2)}%")
            total_tempo += t[j]
        print(f"Total Tempo: {total_tempo}")
        print()
        total_probabilidade = 0
        for j in range(filas[i].Capacity() + 1):
            total_probabilidade += (t[j] / TEMPO_GLOBAL) * 100
        print(f"Total Probabilidade: {round(total_probabilidade, 2)}%")
        print(f"Clientes Perdidos na Fila {i+1}: {filas[i].getLoss()}")

if __name__=="__main__":
    main()
