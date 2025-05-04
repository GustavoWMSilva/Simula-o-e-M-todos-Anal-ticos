class Fila:
    def __init__(self, IdentificadorFila, S, K, SAIDA_ENTRE_INICIAL, SAIDA_ENTRE_FINAL, CHEGADA_ENTRE_INICIAL = None, CHEGADA_ENTRE_FINAL = None,):
        self.IdentificadorFila = IdentificadorFila
        self.S = S                                          # Quantidade de servidores
        self.K = K                                          # Capacidade da fila
        self.CHEGADA_ENTRE_INICIAL = CHEGADA_ENTRE_INICIAL  # Tempo Min chegada na fila Q1
        self.CHEGADA_ENTRE_FINAL = CHEGADA_ENTRE_FINAL      # Tempo Max chegada na fila Q1
        self.SAIDA_ENTRE_INICIAL = SAIDA_ENTRE_INICIAL      # Tempo Min de atendimento
        self.SAIDA_ENTRE_FINAL = SAIDA_ENTRE_FINAL          # Tempo Max de atendimento
        self.times = [0] * (K+1)                            # Array de tempos
        self.QuantidadeClientes = 0
        self.ClientesPerdidos = 0


    def __str__(self):
        return f"Fila: {self.IdentificadorFila}, {self.S}, {self.CHEGADA_ENTRE_INICIAL}, {self.CHEGADA_ENTRE_FINAL}, {self.K}, {self.SAIDA_ENTRE_INICIAL}, {self.SAIDA_ENTRE_FINAL}, {self.times}"
    

    def Status(self):
        return self.QuantidadeClientes
    

    def Capacity(self):
        return self.K
    

    def Servers(self):
        return self.S
    

    def Loss(self):
        self.ClientesPerdidos += 1


    def In(self):
        self.QuantidadeClientes += 1

    
    def Out(self):
        self.QuantidadeClientes -= 1

    
    def ArrayDeTempos(self):
        return self.times
    

    def ChegadaInicio(self):
        return self.CHEGADA_ENTRE_INICIAL
    

    def ChegadaFinal(self):
        return self.CHEGADA_ENTRE_FINAL
    

    def AtendimentoInicio(self):
        return self.SAIDA_ENTRE_INICIAL
    

    def AtendimentoFinal(self):
        return self.SAIDA_ENTRE_FINAL
    