import re

def extrair_probabilidades(texto):
    """
    Extrai as probabilidades de um texto de relatório da fila.
    Converte de percentual com vírgula para float decimal.
    """
    linhas = texto.strip().split("\n")
    probabilidades = []

    for linha in linhas:
        # Extrai números e percentuais
        partes = re.findall(r"[\d.,]+%", linha)
        if partes:
            prob_percent = partes[0].replace('.', '').replace(',', '.').replace('%', '')
            prob = float(prob_percent) / 100
            probabilidades.append(prob)

    return probabilidades

def calcular_metricas(probabilidades, C, tempo_medio_atendimento):
    """
    Calcula N, D, U e W com base nas fórmulas fornecidas.
    """
    K = len(probabilidades) - 1
    mu = 60 / tempo_medio_atendimento  # taxa de atendimento (clientes/hora)

    N = sum(probabilidades[i] * i for i in range(1, K + 1))
    D = sum(probabilidades[i] * min(i, C) * mu for i in range(1, K + 1))
    U = sum(probabilidades[i] * (min(i, C) / C) for i in range(1, K + 1))
    W = N / D if D > 0 else float('inf')

    return {
        "População média (N)": round(N, 4),
        "Vazão (D) [clientes/hora]": round(D, 4),
        "Utilização (U)": round(U, 4),
        "Tempo de resposta (W) [horas]": round(W, 4),
        "Tempo de resposta (W) [minutos]": round(W * 60, 2)
    }

# ===================== EXEMPLO DE USO =====================

# Entradas dos relatórios
input_fila_1 = """
  State               Time               Probability
      0          613545,5900                61,42%
      1          374545,8585                37,50%
      2           10813,4220                 1,08%
"""
input_fila_2 = """
  0              55,0002                 0,01%
      1              36,2275                 0,00%
      2              64,4645                 0,01%
      3             129,7194                 0,01%
      4          184414,7717                18,46%
      5          814204,6873                81,51%
"""
input_fila_3 = """
      0          849062,3793                85,00%
      1          148735,2719                14,89%
      2            1107,2194                 0,11%
"""

# Parâmetros de entrada
C_1 = 2
C_2 = 6
C_3 = 2
tempo_medio_atendimento_fila_1 = 11.0
tempo_medio_atendimento_fila_2 = 75.0
tempo_medio_atendimento_fila_3 = 37.5

# Fila 1
probs1 = extrair_probabilidades(input_fila_1)
resultados1 = calcular_metricas(probs1, C_1, tempo_medio_atendimento_fila_1)
print("\n=== Resultados da Fila 1 ===")
for k, v in resultados1.items():
    print(f"{k}: {v}")
print("===========================\n")

# Fila 2
probs2 = extrair_probabilidades(input_fila_2)
resultados2 = calcular_metricas(probs2, C_2, tempo_medio_atendimento_fila_2)
print("=== Resultados da Fila 2 ===")
for k, v in resultados2.items():
    print(f"{k}: {v}")
print("===========================\n")

# Fila 3
probs3 = extrair_probabilidades(input_fila_3)
resultados3 = calcular_metricas(probs3, C_3, tempo_medio_atendimento_fila_3)
print("=== Resultados da Fila 3 ===")
for k, v in resultados3.items():
    print(f"{k}: {v}")
print("===========================\n")
