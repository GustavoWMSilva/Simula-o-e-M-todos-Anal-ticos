# Gerador de Números Pseudo-Aleatórios: Congruência Linear
# Xn+1c= (aXn+c) mod m
A = 1255
C = 4164
M = 1048576576

previous = 5000

# G/G/S/K
S = 1 # Número de servidores
K = 5 # Capacidade de clientes da fila

# Tempo de chegada entre os clientes
CHEGADA_ENTRE_INICIAL = 2
CHEGADA_ENTRE_FINAL = 5

# Tempo de saida entre os clientes
SAIDA_ENTRE_INICIAL = 3
SAIDA_ENTRE_FINAL = 5

# fila de clientes
fila = []
times = [0] * K
n_perdas = 0

TEMPO_GLOBAL = 0

# Estado Inicial
tempo_chegada = 2
tempo_saida = float('inf')

from enum import Enum

class EventoTipo(Enum):
    tipo_chegada = 1
    tipo_saida = 2

def nextRandon():
    global previous
    previous = (A*previous + C) % M
    return previous / M

def sorteio(evento):
    if evento == EventoTipo.tipo_chegada:
        return (CHEGADA_ENTRE_FINAL - CHEGADA_ENTRE_INICIAL) * nextRandon() + CHEGADA_ENTRE_INICIAL
    return (SAIDA_ENTRE_FINAL - SAIDA_ENTRE_INICIAL) * nextRandon() + SAIDA_ENTRE_INICIAL

# Chegada de um cliente
def chegada(evento):
    global tempo_chegada
    global n_perdas

    if isinstance(tempo_chegada, EventoTipo):
        tempo_chegada = tempo_chegada.value 
    else:
        times[len(fila)] = times[len(fila)] + tempo_chegada 
    tempo_chegada = evento

    if len(fila) < K:
        fila.append(1)
        
        if len(fila) <= S:
            saida(TEMPO_GLOBAL + sorteio(evento))
            return
    else:
        n_perdas = n_perdas + 1
        return
    chegada(TEMPO_GLOBAL + sorteio(evento))


# Saída de um cliente
def saida(evento):
    global tempo_saida
    times[len(fila)] = times[len(fila)] + tempo_saida
    
    tempo_saida = evento
    
    if fila:
        fila.pop()
        if len(fila) >= S:
            saida(TEMPO_GLOBAL + sorteio(evento))
   
# Próximo evento
def nextEvent():
    global TEMPO_GLOBAL

    if isinstance(tempo_chegada, EventoTipo):
        aux_tempo_chegada = TEMPO_GLOBAL + tempo_chegada.value
    else:
        aux_tempo_chegada = TEMPO_GLOBAL + tempo_chegada

    aux_tempo_saida = TEMPO_GLOBAL + tempo_saida
    
    if(aux_tempo_chegada < aux_tempo_saida):
        TEMPO_GLOBAL = aux_tempo_chegada
        return EventoTipo.tipo_chegada
    
    TEMPO_GLOBAL = aux_tempo_saida

    return EventoTipo.tipo_saida


def main():
    # Criterio de Parada
    count = 100000

    while(count > 0):
        count = count - 1
        evento = nextEvent()

        if(evento == EventoTipo.tipo_chegada):
            chegada(evento)
        elif(evento == EventoTipo.tipo_saida):
            saida(evento)    

    for i in range(K):      
        print(f"{i}: {times[i]} ({times[i] / TEMPO_GLOBAL}%)\n ")
    
        

if __name__=="__main__":
    main()
