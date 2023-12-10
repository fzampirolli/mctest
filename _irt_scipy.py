#  python3.8 _irt_scipy.py _irt_test_12QM.csv
from scipy.optimize import minimize
import numpy as np
import csv
import sys

# Função de Log-Verosimilhança para o modelo de TRI
def log_likelihood(params, responses):
    a, b, c = params
    P = 1 / (1 + np.exp(-a * (b - c)))
    log_likelihood = np.sum(responses * np.log(P) + (1 - responses) * np.log(1 - P))
    return -log_likelihood  # Negativo porque minimize encontra o mínimo, e queremos maximizar a verossimilhança

# Função para calcular as habilidades dos alunos pela TRI
def calculate_student_ability(params, response):
    a, b, c = params
    return b + (1 - c) * (response - 0.5) / (c * (1 - 2 * response) + 1e-12)

# Função para calcular as habilidades dos alunos pela TRI para todo o conjunto de dados
def calculate_student_abilities(params_list, responses_matrix):
    student_abilities = []
    for i in range(responses_matrix.shape[0]):
        abilities = [calculate_student_ability(params, response) for params, response in zip(params_list, responses_matrix[i, :])]
        student_abilities.append(abilities)
    return np.array(student_abilities)

# Leitura do arquivo CSV
print("Starting IRT...")
file_name = str(sys.argv[1])
print("File: " + file_name)

with open(file_name, 'r') as f:
    reader = csv.reader(f, delimiter=',')
    responses_matrix = np.array([list(map(int, row)) for row in reader])

# Estimação dos parâmetros para cada questão
params_list = []
for i in range(responses_matrix.shape[1]):
    initial_params = [1, 0, 0.25]
    result = minimize(log_likelihood, initial_params, args=(responses_matrix[:, i],), method='L-BFGS-B')
    a_est, b_est, c_est = result.x
    params_list.append((a_est, b_est, c_est))
    print(f"Parâmetros Estimados para Questão {i + 1}:")
    print("Discriminação (a):", a_est)
    print("Habilidade (b):", b_est)
    print("Chute (c):", c_est)
    print()

# Calcular as habilidades dos alunos pela TRI
student_abilities = calculate_student_abilities(params_list, responses_matrix)

# Calcular a habilidade média de cada aluno
average_student_ability = np.mean(student_abilities, axis=1)

# Classificar os alunos com base na habilidade média pela TRI
sorted_students_tri = np.argsort(average_student_ability)[::-1]

# Exibir os rankings dos alunos pela TRI
print("Ranking dos Alunos pela TRI:")
for rank, student_index in enumerate(sorted_students_tri):
    print(f"Posição {rank + 1}: Aluno {student_index + 1} - Habilidade Média: {average_student_ability[student_index]}")

# Calcular as pontuações totais dos alunos pela TCI
classical_scores = np.sum(responses_matrix, axis=1)

# Classificar os alunos com base na pontuação total pela TCI
sorted_students_classical = np.argsort(classical_scores)[::-1]

# Exibir os rankings dos alunos pela TCI
print("\nRanking dos Alunos pela Teoria Clássica do Item:")
for rank, student_index in enumerate(sorted_students_classical):
    print(f"Posição {rank + 1}: Aluno {student_index + 1} - Pontuação Total: {classical_scores[student_index]}")

# Comparar rankings entre TRI e TCI
common_ranking_tri = np.argsort(np.argsort(sorted_students_tri))
common_ranking_classical = np.argsort(np.argsort(sorted_students_classical))

# Nome do arquivo de saída
output_file_name = file_name[:-4] + '_output.csv'

# Criar uma lista de dicionários para os alunos
students_data = []
for student_index in range(len(common_ranking_tri)):
    student_data = {'Aluno': student_index + 1,
                    'Soma_TCI': classical_scores[student_index],
                    'Ranking_TCI': sorted_students_classical[student_index] + 1, # erro ordem
                    'Habilidade_TRI': average_student_ability[student_index],
                    'Ranking_TRI': common_ranking_tri[student_index] + 1} # erro ordem

    for i in range(responses_matrix.shape[1]):
        student_data[f'q{i + 1}'] = responses_matrix[student_index, i]

    students_data.append(student_data)

# Abrir o arquivo CSV de saída para escrita
with open(output_file_name, 'w', newline='') as csvfile:
    fieldnames = [f'q{i + 1}' for i in range(responses_matrix.shape[1])] + ['Aluno', 'Soma_TCI', 'Ranking_TCI',
                                                                            'Habilidade_TRI', 'Ranking_TRI']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    # Escrever cabeçalho
    writer.writeheader()

    # Escrever informações para cada aluno
    for student_data in sorted(students_data, key=lambda x: x['Aluno']):
        writer.writerow(student_data)

print(f"Arquivo '{output_file_name}' gerado com sucesso.")