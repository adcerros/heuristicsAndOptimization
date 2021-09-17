
set AVION;
/* parametros de los aviones */
param Asientos {i in AVION};
param Capacidad {i in AVION};
param Hora_programada_avion {i in AVION};
param Hora_limite_avion {i in AVION};
param Coste {i in AVION};

set TARIFA;
/* parametros de las tarifas */
param Equipaje_permitido {j in TARIFA};
param Precio {j in TARIFA};

set PISTAS;

param numero_slots;
/* se declaran numericamente para hacerlos iterables */
set SLOTS := 1..numero_slots;

/* parametros de los Slots */
param Hora_inicio_slot {l in SLOTS};
param Slot_preasignado {k in PISTAS, l in SLOTS};

/* variables de decision */
var billetes {i in AVION, j in TARIFA} integer >=0;
/* 1 = asignado , 0 = no asignado */ 
var asignacion {i in AVION, k in PISTAS, l in SLOTS} binary;

/* funcion objetivo */
maximize Profit : (sum{i in AVION, j in TARIFA} billetes[i,j]*Precio[j]) - (sum{i in AVION, k in PISTAS, l in SLOTS} asignacion[i,k,l] * (Hora_inicio_slot[l] - Hora_programada_avion[i]) * Coste[i]);

/* restricciones */
s.t. Peso_maximo {i in AVION}: sum{j in TARIFA} billetes[i,j]*Equipaje_permitido[j] <= Capacidad[i];
s.t. Capacidad_maxima {i in AVION} : sum{j in TARIFA} billetes[i,j] <= Asientos[i];
s.t. Minimo_billetes_estandar_total : sum{i in AVION} billetes[i,'estandar'] >= (sum{i in AVION} Asientos[i])*0.6; 
s.t. Minimo_billetes_leisure {i in AVION} : billetes[i,'leisure_plus'] >= 20;
s.t. Minimo_billetes_business {i in AVION} :  billetes[i,'business_plus'] >= 10;  
s.t. Hora_incio_mayor_hora_programada {i in AVION} : sum{k in PISTAS, l in SLOTS} Hora_inicio_slot[l] * asignacion[i,k,l] >= Hora_programada_avion[i];
s.t. Hora_inicio_menor_hora_limite {i in AVION}: sum{k in PISTAS, l in SLOTS} Hora_inicio_slot[l] * asignacion[i,k,l] <= Hora_limite_avion[i];
s.t. Un_slot_por_avion {i in AVION} : sum{k in PISTAS, l in SLOTS} asignacion[i,k,l] = 1;
s.t. Asignacion_unica_slots {k in PISTAS, l in SLOTS} : sum{i in AVION} asignacion[i,k,l] <= 1;
s.t. Asignacion_slots_libres {i in AVION, k in PISTAS, l in SLOTS} :  asignacion[i,k,l] + Slot_preasignado[k,l] <= 1;
s.t. Asignacion_slots_no_consecutivos {k in PISTAS, l in 1..(numero_slots-1)} : sum{i in AVION}(asignacion[i,k,l] + asignacion[i,k,l+1]) <= 1; 

end;
