import re
import numpy as np
import random
import csv
import math  # Importar las funciones matemáticas


def parse_params(file_path):
    params = {}
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                # Evaluar números, pero mantener las expresiones como cadenas
                try:
                    value = eval(value)
                except:
                    pass
                params[key] = value
    return params


def extract_variables(expression):
    # Lista de funciones matemáticas conocidas
    math_functions = {"sin", "cos", "tan", "sqrt", "exp"}

    # Buscar todas las variables en la expresión
    variables = re.findall(r"[a-zA-Z_]\w*", expression)

    # Filtrar las funciones matemáticas conocidas
    unique_variables = set(var for var in variables if var not in math_functions)

    return len(unique_variables)


def extract_individual(individual, VARNUM):
    var_names = ["x", "y", "z", "w", "u", "v"]
    variables = {var_names[i]: individual[i] for i in range(VARNUM)}
    return variables


def check_restrictions(RESTRICT, variables, INTERVALO, VARNUM):
    valid = True
    # Verificar límites
    for var in variables:
        for i in range(VARNUM):
            min_val, max_val = INTERVALO[i]
            if variables[i] < min_val or variables[i] > max_val:
                return False
    # Verificar restricciones
    for restriction in RESTRICT:
        if not eval(restriction, {"__builtins__": None}, variables):
            valid = False
            break
    return valid


def clamp_value(value, MINB, MAXB):
    # Asegurarse de que el valor esté dentro de los límites
    return max(MINB, min(value, MAXB))


def create_population(PSIZE, VARNUM, INTERVALO, RESTRICT):
    population = []
    for _ in range(PSIZE):
        while True:
            individual = []
            for i in range(VARNUM):
                min_val, max_val = INTERVALO[i]
                value = np.random.uniform(min_val, max_val)
                individual.append(value)
            is_valid = check_restrictions(RESTRICT, individual, INTERVALO, VARNUM)
            if is_valid:
                break
        population.append(individual)
    return population


def process_ind(target, child, FUNCION, RESTRICT, OBJECTIVE, VARNUM, INTERVALO):
    variablesC = extract_individual(child, VARNUM)
    # Verificar si el hijo es válido
    child_valid = check_restrictions(RESTRICT, variablesC, INTERVALO, VARNUM)
    if not child_valid:
        return (
            False,
            None,
            None,
        )  # Devolver una tupla con valores None para child_value y target_value
    variablesT = extract_individual(target, VARNUM)
    # Evaluar las funciones matemáticas con math
    child_value = eval(
        FUNCION,
        {
            "__builtins__": None,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "sqrt": math.sqrt,
            "exp": math.exp,
        },
        variablesC,
    )
    target_value = eval(
        FUNCION,
        {
            "__builtins__": None,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "sqrt": math.sqrt,
            "exp": math.exp,
        },
        variablesT,
    )
    win = (
        (child_value > target_value)
        if OBJECTIVE == "MAX"
        else (child_value < target_value)
    )
    return win, child_value, target_value


def evaluate_fitness(individual, FUNCION):
    variables = extract_individual(individual, len(individual))
    try:
        # Evaluar las funciones matemáticas con math
        return eval(
            FUNCION,
            {
                "__builtins__": None,
                "sin": math.sin,
                "cos": math.cos,
                "tan": math.tan,
                "sqrt": math.sqrt,
                "exp": math.exp,
            },
            variables,
        )
    except Exception as e:
        print(f"Error evaluando FUNCION '{FUNCION}': {e}")
        return None  # Manejo de error


def main():
    # Obtener parámetros desde el archivo config
    file_path = "config.txt"
    parameters = parse_params(file_path)
    FM = parameters.get("FMUTACION")
    CR = parameters.get("CRECOMBINACION")
    FUNCION = parameters.get("FUNCION")
    NGEN = parameters.get("NGENERACIONES")
    PSIZE = parameters.get("TPOBLACION")
    INTERVALO = parameters.get("INTERVALO")
    RESTRICT = parameters.get("RESTRICT")
    OBJECTIVE = parameters.get("OBJETIVO")
    # Obtener el número de variables
    VARNUM = extract_variables(FUNCION)
    # Abrir archivo CSV para registrar resultados
    with open("genetic_algorithm_log.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Generation", "Individual", "Fitness", "Best Fitness"])
        # Crear población inicial
        population = create_population(PSIZE, VARNUM, INTERVALO, RESTRICT)
        best_fitness = float("-inf") if OBJECTIVE == "MAX" else float("inf")
        best_individual = None
        for individual in population:
            fitness_value = evaluate_fitness(individual, FUNCION)
            if (OBJECTIVE == "MAX" and fitness_value > best_fitness) or (
                OBJECTIVE == "MIN" and fitness_value < best_fitness
            ):
                best_fitness = fitness_value
                best_individual = individual
            writer.writerow(
                [
                    "Initial Population",
                    [round(gene, 4) for gene in individual],
                    fitness_value,
                    best_fitness,
                ]
            )
        # Algoritmo principal
        for n in range(NGEN):
            print(f"\nGeneration {n}:")
            for i, target in enumerate(population):
                populationEX = [ind for j, ind in enumerate(population) if j != i]
                values = random.sample(populationEX, 3)
                child = np.add(values[0], (FM * (np.subtract(values[1], values[2]))))
                # Limitar para asegurar que esté dentro de los límites
                print(f"\nChild generated: {[round(gene, 4) for gene in child]}")
                rand_value = random.uniform(-1, 1)
                print(f"Random value for evaluation: {rand_value}")
                evaluate = rand_value <= CR
                print(f"Child evaluation {'accepted' if evaluate else 'rejected'}")
                if evaluate:
                    win, child_value, target_value = process_ind(
                        target, child, FUNCION, RESTRICT, OBJECTIVE, VARNUM, INTERVALO
                    )
                    if win:
                        population[i] = child
                        print(f"Child replaces target: {target} -> {child}")
                    if child_value is not None and target_value is not None:
                        writer.writerow(
                            [
                                n,
                                [round(gene, 4) for gene in child],
                                child_value,
                                best_fitness,
                            ]
                        )
            # Imprimir la población después de cada generación
            print(f"\nPopulation after generation {n}:")
            for individual in population:
                print([round(gene, 4) for gene in individual])


if __name__ == "__main__":
    main()
