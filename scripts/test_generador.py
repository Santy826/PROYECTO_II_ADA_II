from src.core.generador_minizinc import generar_codigo_minizinc

example = {
    "variables": [
        ("int", "x_1", "Mesa"),
        ("int", "x_2", "Notebook"),
    ],
    "constraints": [
        "x_1 >= 0; %No negatividad",
        "x_2 >= 0; %No negatividad",
        "x_1 + x_2 <= 10000; %Procesadores y = 10000 - x",
        "2*x_1 + x_2 <= 15000; %Memoria y = 15000 - 2x",
        "3*x_1 + 4*x_2 <= 25000; %Tiempo y = (25000 - 3x)/4",
    ],
    "objective": "maximize 1000*x_1 + 750*x_2;",
    "output_vars": ["x_1", "x_2"],
}

if __name__ == '__main__':
    print(generar_codigo_minizinc(example))
