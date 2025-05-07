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
      0          230516,7589                54,22%
      1          170437,6391                40,09%
      2           22671,8230                 5,33%
      3            1517,4587                 0,36%
      4              29,4535                 0,01%
"""
input_fila_2 = """
  State               Time               Probability
      0              62,3686                 0,01%
      1            1395,7643                 0,33%
      2           11302,9206                 2,66%
      3           39599,5342                 9,31%
      4           73150,4304                17,20%
      5           87927,4772                20,68%
      6           77839,5901                18,31%
      7           53091,7278                12,49%
      8           33602,7505                 7,90%
      9           20405,2585                 4,80%
     10           12156,0372                 2,86%
     11            6229,8187                 1,47%
     12            3626,1852                 0,85%
     13            2019,3224                 0,47%
     14            1275,8168                 0,30%
     15             937,0140                 0,22%
     16             428,5007                 0,10%
     17             107,5648                 0,03%
     18              15,0509                 0,00%
"""
input_fila_3 = """
                Time               Probability
      0          181660,2723                42,73%
      1          161007,8525                37,87%
      2           63987,1959                15,05%
      3           15519,1497                 3,65%
      4            2756,0411                 0,65%
      5             236,7520                 0,06%
      6               5,8696                 0,00%
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
