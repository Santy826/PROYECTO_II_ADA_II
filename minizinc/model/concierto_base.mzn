% ============================================================
% concierto_base.mzn
% Modelo MiniZinc: ¿Dónde pongo mi concierto?
% Asignatura: Análisis y Diseño de Algoritmos
% ============================================================
%
% Este modelo recibe los datos desde un archivo .dzn separado
% (generado por la aplicación Python) y encuentra la posición
% óptima para el concierto dentro del cuadrado N x N.
%
% Criterio de equidad: minimizar la distancia Manhattan máxima
% a cualquier ciudad (estrategia minimax).
%
% Para usar este modelo junto con un archivo de datos:
%   1. Generar el .dzn desde la aplicación Python.
%   2. En MiniZinc IDE: File > Open Model + Data > seleccionar ambos.
%   3. Ejecutar el solver.

% --- Parámetros (vienen del archivo .dzn) ---
int: N;                           % Tamaño del cuadrado (N x N)
int: M;                           % Número de ciudades
array[1..M] of int: ciudad_x;     % Coordenadas X de cada ciudad
array[1..M] of int: ciudad_y;     % Coordenadas Y de cada ciudad

% --- Variables de decisión ---
var 0..N: px;           % Coordenada X del concierto
var 0..N: py;           % Coordenada Y del concierto
var 0..2*N: dist_max;   % Distancia Manhattan al vecino más lejano

% --- Restricciones ---

% 1. El concierto NO puede estar exactamente en ninguna ciudad
constraint forall(i in 1..M)(
    not (px = ciudad_x[i] /\ py = ciudad_y[i])
);

% 2. dist_max debe ser mayor o igual a la distancia a cada ciudad.
%    Esto hace que dist_max tome el valor de la distancia máxima real.
constraint forall(i in 1..M)(
    dist_max >= abs(px - ciudad_x[i]) + abs(py - ciudad_y[i])
);

% --- Objetivo ---
% Minimizar la distancia máxima = ubicación más equitativa posible.
% La ciudad más lejana queda lo más cerca que sea posible del concierto.
solve minimize dist_max;

% --- Salida ---
output [
    "=== Resultado del modelo ===\n",
    "Posición del concierto: (", show(px), ", ", show(py), ")\n",
    "Distancia máxima (equidad): ", show(dist_max), "\n"
];
