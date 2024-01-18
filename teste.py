def gerar_e_verificar_pares(total_numeros):
    """
    Gera números aleatórios e retorna a porcentagem de números pares.

    Args:
        total_numeros (int): O total de números a serem gerados.

    Returns:
        float: A porcentagem de números pares.
    """
    import random  # biblioteca para gerar números aleatórios
    numeros_pares = 0

    for _ in range(total_numeros):
        numero_aleatorio = random.randint(1, 100)
        print("Número gerado:", numero_aleatorio)

        if numero_aleatorio % 2 == 0:  # se for par, incrementa
            numeros_pares += 1

    porcentagem_pares = (numeros_pares / total_numeros) * 100
    return porcentagem_pares


# Solicita ao usuário o total de números a serem gerados
total_numeros = int(input("Digite o total de números a serem gerados: "))

# Chama a função e exibe o resultado
porcentagem_resultante = gerar_e_verificar_pares(total_numeros)
print(f"\nA porcentagem de números pares é: {porcentagem_resultante:.2f}%")
