#  python3.8 _irt_scipy.py _irt_test_12QM.csv

from scipy.optimize import minimize
import numpy as np
import csv, sys

print("Starting IRT...")

print("File: "+str(sys.argv[1]))

file_name = str(sys.argv[1])

print("File: "+file_name)

# Suponha que o arquivo CSV esteja localizado no caminho '_irt_test_12QM.csv'
with open(file_name, 'r') as f:
    reader = csv.reader(f, delimiter=',')
    responses_matrix = np.array([list(row) for row in reader]).astype(np.int)

# Função de Log-Verosimilhança para o modelo de TRI
def log_likelihood(params, responses):
    a, b, c = params
    P = 1 / (1 + np.exp(-a * (b - c)))
    log_likelihood = np.sum(responses * np.log(P) + (1 - responses) * np.log(1 - P))
    return -log_likelihood  # Negativo porque minimize encontra o mínimo, e queremos maximizar a verossimilhança

params_list = []

# Estimação dos parâmetros para cada questão
for i in range(responses_matrix.shape[1]):  # Itera sobre as questões
    initial_params = [1, 0, 0.25]  # Valores iniciais para a, b, e c
    result = minimize(log_likelihood, initial_params, args=(responses_matrix[:, i],), method='L-BFGS-B')

    # Parâmetros estimados para a questão i
    a_est, b_est, c_est = result.x
    params_list.append((a_est, b_est, c_est))

# Exibindo os parâmetros estimados para cada questão
for i, params in enumerate(params_list):
    print(f"Parâmetros Estimados para Questão {i + 1}:")
    print("Discriminação (a):", params[0])
    print("Habilidade (b):", params[1])
    print("Chute (c):", params[2])
    print()