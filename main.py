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
escalonador = []
filaClientes = []
times = [0] * (K+1)
clientesPerdidos = 0

TEMPO_GLOBAL = 0

# Estado Inicial
TEMPO_CHEGADA = 2
ultimo_tempo_global = 0
tempo_saida = float('inf')

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
        times[tamFila] = times[tamFila] + ultimo_tempo_global 

    ultimo_tempo_global = evento.tempo

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
        times[tamFila] = times[tamFila] + ultimo_tempo_global

    ultimo_tempo_global = evento.tempo
    
    tamFila = tamFila - 1
    if tamFila >= S:
        # Agenda o atendimento do cliente
        escalonador.append(Evento("Saida", TEMPO_GLOBAL + sorteio(evento)))
    
    # Ordena o escalonador de acordo com o tempo
    escalonador.sort(key=lambda x: x.tempo)

def main():
    global TEMPO_GLOBAL

    # Criterio de Parada
    count = 100
    
    # Primeiro cliente chegando...
    escalonador.append(Evento("Chegada", TEMPO_CHEGADA))

    while(count > 0):
        count = count - 1

        #print(escalonador[0])
        print(times)
        
        evento = escalonador.pop(0)
        TEMPO_GLOBAL = evento.tempo
        
        if evento.tipoEvento == "Chegada":
            chegada(evento)
        else:
            saida(evento)


    print("Tempo Global do Sistema:", TEMPO_GLOBAL)
    print("Clientes perdidos: ", clientesPerdidos, "\n")
    print("Simulação (Estado - Tempo - Probabilidade)")

    for i in range(K+1):      
        print(f"{i}: {times[i]} ({times[i] / TEMPO_GLOBAL}%)\n ")
    
if __name__=="__main__":
    main()
