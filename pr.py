import numpy as np
import re
import pandas as pd

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

def create_population(PSIZE, VARNUM, INTERVALO):
    population = []
    for _ in range(PSIZE):
        individual = []
        for i in range(VARNUM):
            min_val, max_val = INTERVALO[i]
            value = np.random.uniform(min_val, max_val)
            individual.append(value)
        population.append(individual)
    return population

def main():
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
    # Crear la población inicial
    population = create_population(PSIZE, VARNUM, INTERVALO)
    df = pd.DataFrame(population, columns=[f"Var{i+1}" for i in range(VARNUM)])
    
    # Guardar el DataFrame en un archivo CSV
    df.to_csv("evolutive.csv", index=False)
    
    print(df)

main()