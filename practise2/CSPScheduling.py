from constraint import *

# CREACION DEL OBJETO PROBLEMA
problem = Problem()

#DECLARACION DE VARIABLES

# Se declaran las variables y sus dominios, cada una de las franjas de los satelites se declara como una variable
problem.addVariable('SAT1', [1, 2, 3, 4])
problem.addVariable('SAT2', [1, 2, 3])
problem.addVariable('SAT3_F1', [4, 6])
problem.addVariable('SAT3_F2', [7, 9, 10])
problem.addVariable('SAT4', [8, 11, 12])
problem.addVariable('SAT5', [1, 7, 12])
problem.addVariable('SAT6_F1', [7, 9])
problem.addVariable('SAT6_F2', [3, 4, 5])



# METODOS

# Funcion para la restriccion de SAT4 y SAT5
# Si SAT5 se comunica con ANT12, SAT4 no se puede comunicar con ANT11
def sat4AndSat5Condition(a, b):
    if a == 12 and b == 11:
        return False
    else:
        return True

# Funcion para la restriccion de ANT7 y ANT12
# Si en una solucion se asignan las antenas ANT7 y ANT12, se deben asignar ambas a franjas horarias
# que comiencen antes de las 12:00 o a franjas horarias que comiencen despues de las 12:00
def sameTimeSLot(a, b):
    if (a == 7 and b == 12) or (a == 12 and b == 7):
        return False
    else:
        return True



# LLAMADA AL METODO CONSTRAINT DE LA LIBRERIA PARA ASIGNAR LAS DIFERENTES RESTRICCIONES

# SAT1 y SAT2 deben tener asignada la misma antena de transmision
problem.addConstraint(AllEqualConstraint(), ['SAT1', 'SAT2'])

# Los satelites SAT2, SAT4 y SAT5 deben tener asignados antenas de transmision diferentes
problem.addConstraint(AllDifferentConstraint(), ['SAT2', 'SAT4', 'SAT5'])

# Si SAT5 se comunica con ANT12, SAT4 no se puede comunicar con ANT11
problem.addConstraint(sat4AndSat5Condition, ['SAT5', 'SAT4'])

# Si en una solucion se asignan las antenas ANT7 y ANT12, se deben asignar ambas a franjas horarias
# que comiencen antes de las 12:00 o a franjas horarias que comiencen despues de las 12:00
problem.addConstraint(sameTimeSLot, ['SAT3_F2', 'SAT5'])
problem.addConstraint(sameTimeSLot, ['SAT4', 'SAT5'])
problem.addConstraint(sameTimeSLot, ['SAT4', 'SAT6_F1'])


# Se llama al solver del problema mediante la libreria
solutions = problem.getSolutions()

# Format para la salida en un formato mas legible
print("Soluciones encontradas: ".format(len(solutions)))
for i in solutions:
    print("{0} {1} {2} {3} {4} {5} {6} {7}".format("SAT1 = " + str(i['SAT1']), "\tSAT2 = " + str(i['SAT2']),
                                                   "\tSAT3_F1 = " + str(i['SAT3_F1']),
                                                   "\tSAT3_F2 = " + str(i['SAT3_F2']), "\tSAT4 = " + str(i['SAT4'])
                                                   , "\tSAT5 = " + str(i['SAT5']), "\tSAT6_F1 = " + str(i['SAT6_F1']),
                                                   "\tSAT6_F2 = " + str(i['SAT6_F2'])))

print("Number of solutions: " + str(len(solutions)))
