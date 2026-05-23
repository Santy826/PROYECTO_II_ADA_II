% Modelo base (placeholder)
% Se completará en la siguiente fase.

int: N;
int: M;

array[1..M] of int: city_x;
array[1..M] of int: city_y;

var 0..N: concert_x;
var 0..N: concert_y;

% TODO: agregar restricciones y función objetivo.

solve satisfy;

output [
  "concert_x=", show(concert_x), "\n",
  "concert_y=", show(concert_y), "\n"
];
