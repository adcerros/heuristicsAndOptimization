#!/usr/bin/env python3

import copy
import math
import sys
import time


class parser:

    # Parser de documento de entrada, retorna tres listas, una para los parametros de cada satelite y otra para los objetivos del problema (observaciones a transmitir)
    # Se eliminan los caracteres innecesarios y se transforman los objetivos en vectores para hacerlo mas manejable en el solver
    def __init__(self, file):
        fr = open(file)
        text = fr.readlines()
        i = 0
        self.objectives = []
        OBS = text[0].split(":")
        OBS = OBS[1].split()
        OBS = OBS[0].split(";")
        while i < len(OBS):
            OBS[i] = OBS[i].replace("(", "")
            OBS[i] = OBS[i].replace(")", "")
            self.objectives.append((int(OBS[i][0]), int(OBS[i][2:4])))
            i = i+1
        SAT1 = text[1].split(":")
        SAT1 = SAT1[1].split()
        SAT1 = SAT1[0].split(";")
        self.sat1State = SAT1
        j = 0
        while j < len(SAT1):
            self.sat1State[j] = int(SAT1[j])
            j = j+1
        SAT2 = text[2].split(":")
        SAT2 = SAT2[1].split()
        SAT2 = SAT2[0].split(";")
        self.sat2State = SAT2
        k = 0
        while k < len(SAT2):
            self.sat2State[k] = int(SAT2[k])
            k = k+1


class problem:

    # Constructor de la clase problema
    def __init__(self, file, heuristic):
        # Inicializacion de los satelites, las condiciones iniciales y parseo del archivo de entrada
        print(file)
        myParser = parser(str(file))
        sat1 = satelite(myParser.sat1State, 0, 1, "SAT1")
        sat2 = satelite(myParser.sat2State, 2, 3, "SAT2")

        # Inicializacion de las herramientas para la resolucion del problema
        initialState = state(sat1, sat2, 0, myParser.objectives)
        # Se llama al solver del problema, como solo se implementa A* se realiza este algoritmo por defecto
        solver(initialState, str(heuristic))





class state:

    # Constructor del objeto estado, incluye los dos objetos satelites, el puntero a sus nodos padres, los objetivos y las funciones.
    # Se asigna un gran valor heuristico por defecto
    def __init__(self, sat1=None, sat2=None, dayTime=0, objectives=[]):
        self.time = dayTime
        self.sat1 = sat1
        self.sat2 = sat2
        # La lista de objetivos incluye las observaciones que deben ser transmitidas
        self.objectives = objectives
        self.heuristic = self.objectives * 2
        self.cost = 0
        self.f = 9999
        self.parents = []

    # Retorna el valor de la funcion F
    def calculateF(self):
        return self.cost + self.heuristic


class satelite:

    # Constructor del objeto satelite, los costes de las acciones del  satelite
    # se extraen de la lista que retorna el parser del documento de entrada
    def __init__(self, list=[1, 1, 1, 1, 1], strip1=None, strip2=None, name=None):
        self.name = name
        # Lista de observaciones que ha realizado el satelite
        self.observations = []
        # Bandas de observacion
        self.strip1 = strip1
        self.strip2 = strip2
        # Ultima accion realizada por el satelite
        self.lastAction = ""
        self.observationCost = list[0]
        self.transmissionCost = list[1]
        self.spinCost = list[2]
        self.unitsPerCharge = list[3]
        self.availablePowerUnits = list[4]
        self.maxPowerUnits = list[4]


class solver:

    # Constructor del objeto solver, se crea tanto la lista abierta como cerrada,
    # se asigna la heuristica y se llama a A* para la resolucion del problema
    def __init__(self, initialState, heuristic):
        self.heuristic = heuristic
        self.openList = []
        self.closedList = []
        self.aStar(initialState)



    #ALGORITHM////////////////////////////////////////////////////////////////////////////////////////////////////////////
    # Algoritmo A*, recibe el estado inicial y una vez ha encontrado la solucion optima llama
    # al metodo printSolution que se encarga de generar los documentos de salida
    def aStar(self, initialState):
        # Se inicializa un contador de tiempo para obtener el tiempo total empleado en la obtencion del resultado
        startTime = time.time()
        # Se añade el estado inicial a abierta
        self.openList.append(initialState)
        # Mientras que abierta no este vacia o no se llegue al estado final se saca el primer nodo de abierta y se expande
        # El estado final es el momento en el que se han realizado todas las observaciones
        # y transmisiones programadas es decir cuando la lista de objetivos se encuentra vacia
        while len(self.openList) > 0:
            actualState = self.openList.pop(0)
            if len(actualState.objectives) == 0:
                self.generateDocuments(actualState, startTime)
                sys.exit()
            # Si el estado actual no es el final se extrae el primer nodo de abierta se expande y se añade
            # a cerrada, los sucesores se insertan en abierta en orden en metodos posteriores
            else:
                self.generateSuccessors(actualState)
                self.closedList.append(actualState)
        else:
            return None

    # Genera los ficheros de salida del problema
    def generateDocuments(self, actualState, startTime):
        planDocument = open(str(sys.argv[1]) + ".output", "w")
        planLength = len(actualState.parents)
        for i in range(len(actualState.parents)):
            parent = actualState.parents.pop(0)
            if i == 0:
                planDocument.write("PLAN" + "\n")
            else:
                planDocument.write(str(i) + "." + " SAT1 " + str(parent.sat1.lastAction) + ", SAT2 " + str(parent.sat2.lastAction) + "\n")
        planDocument.write(str(i + 1) + "." + " SAT1 " + str(actualState.sat1.lastAction) + ", SAT2 " + str(actualState.sat2.lastAction) + "\n")
        staticsDocument = open(str(sys.argv[1]) + ".statistics", "w")
        staticsDocument.write("Tiempo de ejecucion : " + str(" %s seconds" % (time.time() - startTime)) + "\n")
        staticsDocument.write(("Coste total : " + str(planLength) + "\n"))
        staticsDocument.write(("Longitud del plan : " + str(planLength) + "\n"))
        staticsDocument.write("Nodos expandidos : " + str(len(self.closedList)) + "\n")
        staticsDocument.write(("Nodos generados : " + str(len(self.closedList) + len(self.openList)) + "\n"))

    # Genera los sucesores del nodo actual
    def generateSuccessors(self, actualState):
        # Se realizan las operaciones que posibles en el estado actual para ambos satelites y se añaden a sus respectivas listas
        sat1OperationsList = self.operate(actualState.sat1, actualState)
        sat2OperationsList = self.operate(actualState.sat2, actualState)
        # Se llama al metodo generateStates que se encarga de combinar las diferentes acciones
        # realizadas por cada uno de los satelites y generar los nodos sucesores
        self.generateStates(sat1OperationsList, sat2OperationsList, actualState)

    # Realiza la llamadas a los metodos que realizan las  operaciones comprobando que  cumplen las
    # restricciones en el estado actual para el satelite que recibe por parametro
    def operate(self, satX, actualState):
        # Se considera que la accion no hacer nada siempre es posible
        auxList = [self.idle(satX)]
        # Si las unidades de bateria del satelite actual no estan al maximo y se encuentra dentro de la franja horaria
        # donde puede realizar acciones puede realizar la accion de carga de bateria
        if actualState.time < 12 and satX.availablePowerUnits < satX.maxPowerUnits:
            auxList.append(self.rechargeBattery(satX))
        # Comprueba si el satelite se encuentra dentro de la franja horaria donde puede realizar acciones y si tiene bateria disponible
        if actualState.time < 12 and satX.availablePowerUnits > 0:
            # Llama al operador rotar
            auxList.append(self.rotate(satX))
            # Se extraen los vectores que indican las bandas y la hora
            pos1 = (satX.strip1, actualState.time)
            pos2 = (satX.strip2, actualState.time)
            # Se comprueba si el satelite se encuentra sobre un punto observable de ser asi puede realizar la accion observar
            if pos1 in actualState.objectives and pos1 not in satX.observations:
                auxList.append(self.takeObservationStrip1(satX, actualState.time))
            if pos2 in actualState.objectives and pos2 not in satX.observations:
                auxList.append(self.takeObservationStrip2(satX, actualState.time))
            # Si el satelite tiene observaciones realizadas en su lista de observaciones y estas aun no han
            # sido transmitidas por el otro satelite puede realizar la operacion de transmitir
            if len(satX.observations) > 0:
                selectedObservation = satX.observations[0]
                if selectedObservation in actualState.objectives:
                    auxList.append(self.toTransmit(satX))
        return auxList

    # Metodo que combina las diferentes operaciones de los satelites creando los nuevos nodos
    def generateStates(self, sat1OperationsList, sat2OperationsList, actualState):
        # Combina cada accion del satelite uno con las del satelite dos
        for i in range(len(sat1OperationsList)):
            for j in range(len(sat2OperationsList)):
                # Se construye el nuevo objeto estado
                newState = self.newStateCreator(actualState, sat1OperationsList[i], sat2OperationsList[j])
                # Se actualizan las transmisiones pendientes
                # Si la accion anterior fue transmitir y la  observacion ya ha sido transmitida por el otro satelite en un momento anterior se desecha la observacion
                # Si la tranmision de la observacion aun no ha sido realizada se elimina aqui de la lista comun de objetivos
                # Se realiza la eliminacion en este momento del programa para obtener un codigo mas simple y realizar las operaciones de manera independiente
                if newState.sat1.lastAction == "transmit":
                    currentObservation = newState.sat1.observations.pop(0)
                    if currentObservation in newState.objectives:
                        newState.objectives.remove(currentObservation)
                if newState.sat2.lastAction == "transmit":
                    currentObservation = newState.sat2.observations.pop(0)
                    if currentObservation in newState.objectives:
                        newState.objectives.remove(currentObservation)
                # La actualizacion de costes de las funciones se realizan despues de actualizar el valor de la lista de transmisiones restantes
                # Se actualiza el valor del coste, definido por el numero de horas que han transcurrido desde el inicio
                newState.cost = actualState.cost + 1
                # Se actualiza el valor de la funcion heuristica
                newState.heuristic = self.calculateHeuristic(newState)
                # Se actualiza el valor de la funcion F
                newState.f = newState.calculateF()
                # Se llama al metodo que comprueba si el nuevo estado esta repetido
                self.checkRepeatedState(newState)

    # Metodo auxiliar que crea un nuevo nodo (se realiza esta accion aparte por limpieza del codigo pero podria incluirse en el metodo generateStates)
    def newStateCreator(self, actualState, sat1, sat2):
        newState = state()
        # Se añaden al nuevo estado los satelites
        newState.sat1 = self.sateliteClonator(sat1)
        newState.sat2 = self.sateliteClonator(sat2)
        newState.time = self.setNewTime(actualState.time)
        # Se añaden los nodos anteriores a la lista de padres del nuevo nodo
        for k in range(len(actualState.parents)):
            newState.parents.append(actualState.parents[k])
        # Se añade el nodo actual en la ultima posicion de la lista de padres del nuevo nodo
        # para finalmente obtener el camino que ha seguido el algortimo hasta la solucion
        newState.parents.append(actualState)
        # Se clonan las transmisiones que quedan por realizar del estado anterior
        newState.objectives = copy.deepcopy(actualState.objectives)
        # Se clonan la ultimas acciones realizadas por los satelites al nuevo nodo
        newState.sat1.lastAction = sat1.lastAction
        newState.sat2.lastAction = sat2.lastAction
        return newState

    # Se calcula el nuevo valor de la funcion heuristica segun sea la heuristica seleccionada
    def calculateHeuristic(self, newState):
        if self.heuristic == "remainingObjectives":
            return len(newState.objectives)
        if self.heuristic == "middleDistance":
            return self.getDistances(newState)
        else:
            print("Heuristic not found, please select a heuristic of the list")
            sys.exit()

    def getDistances(self, newState):
        maxDistance = 0
        if len(newState.objectives) > 0:
            # Se realiza el calculo de la distancia a los diferentes objetivos
            for i in range(len(newState.objectives)):
                objective = newState.objectives[i]
                # Si el objetivo ha sido observado y los satelites no tienen bateria aun quedaran al menos la accion de recargar y transmitir
                # por tanto se suma dos a la distancia
                if objective in newState.sat1.observations and objective in newState.sat2.observations:
                    if newState.sat1.availablePowerUnits == 0 and newState.sat2.availablePowerUnits == 0:
                        maxDistance += 2
                    else:
                        maxDistance += 1
                # Si el objetivo ha sido observado por el satelite uno y no tiene bateria aun quedaran al menos la accion de recargar y transmitir
                # por tanto se suma dos a la distancia
                if objective in newState.sat1.observations:
                    if newState.sat1.availablePowerUnits == 0:
                        maxDistance += 2
                    else:
                        maxDistance += 1
                # Si el objetivo ha sido observado por el satelite dos y no tiene bateria y no ha sido observado por el satelite uno
                # aun quedaran al menos la accion de recargar y transmitir por tanto se suma dos a la distancia
                elif objective in newState.sat2.observations:
                    if newState.sat2.availablePowerUnits == 0:
                        maxDistance += 2
                    else:
                        maxDistance += 1
                # Si el objetivo aun no ha sido observado por ningun satelite
                else:
                    # Si se encuentra en la posicion actual aun quedaran minimo dos acciones observarlo y transmitirlo
                    if objective[1] == newState.time:
                        maxDistance += 2
                    # Si el objetivo se encuentra en una posicion alcanzable en esta vuelta se suma la distancia
                    if objective[1] > newState.time:
                        maxDistance += (objective[1] - newState.time) + 2
                    # Si el objetivo ya se ha pasado esta vuelta se suma la distancia real
                    if newState.time - 1 > objective[1]:
                        maxDistance += ((24 + objective[1]) - newState.time) + 2
            # Se retorna la distancia media de la distancia a los objetivos
            return math.ceil(maxDistance / len(newState.objectives))
        # Cuando no queden transmisiones por realizar la heuristica retorna 0
        else:
            return 0

    # Metodo auxiliar que llama a la funcion isSameState para comprobar si el estado es repetido
    # Primero comprueba si se encuentra en abierta, si el nuevo estado tiene mejor valor F que el antiguo se sustituye antiguo por nuevo
    # Si no esta en abierta y tampoco en cerrada lo añade en abierta
    def checkRepeatedState(self, newState):
        position = self.isSameState(newState, self.openList)
        if position != -1:
            if newState.f < self.openList[position].f:
                self.openList[position] = newState
            else:
                return
        else:
            position = self.isSameState(newState, self.closedList)
            if position != -1:
                return
        self.openList.insert(self.insertInOpenListNeatly(newState, self.openList), newState)



    # OPERATORS////////////////////////////////////////////////////////////////////////////////////////////////////////////
    # Se actualizan los valores del parametro lastAction que se utiliza para una vez resuelto el
    # problema poder indicar correctamente las diferentes operaciones que han ido realizando los satelites en cada uno de los nodos

    # Operador no hacer nada
    def idle(self, satX):
        newSatX = self.sateliteClonator(satX)
        newSatX.lastAction = "IDLE"
        return newSatX

    # Se actualiza el numero de unidades de energia disponibles en la bateria del satelite seleccionado
    def rechargeBattery(self, satX):
        newSatX = self.sateliteClonator(satX)
        newSatX.availablePowerUnits += satX.unitsPerCharge
        newSatX.lastAction = "recharge"
        return newSatX

    # Se cambian las bandas de observacion y se actuializa el valor de la bateria del satelite seleccionado
    def rotate(self, satX):
        newSatX = self.sateliteClonator(satX)
        # Se comprueba con que satelite se esta operando dado que realizan giros
        # distintos y tiene bandas posibles diferentes
        if newSatX.name == "SAT1":
            if satX.strip1 == 0:
                newSatX.strip1 = 1
                newSatX.strip2 = 2
            else:
                newSatX.strip1 = 0
                newSatX.strip2 = 1
        else:
            if satX.strip1 == 2:
                newSatX.strip1 = 1
                newSatX.strip2 = 2
            else:
                newSatX.strip1 = 2
                newSatX.strip2 = 3
        newSatX.availablePowerUnits -= newSatX.spinCost
        newSatX.lastAction = "rotate"
        return newSatX

    # Se toma la observacion del objetivo con el satelite respecto a la posicion de su primera banda
    # de observacion y la hora actual, ademas se actualiza la bateria restante
    def takeObservationStrip1(self, satX, dayTime):
        newSatX = self.sateliteClonator(satX)
        newSatX.observations.append((newSatX.strip1, dayTime))
        newSatX.availablePowerUnits -= newSatX.observationCost
        newSatX.lastAction = "observe" + "(" + str(newSatX.strip1) + "," + str(dayTime) + ")"
        return newSatX

    # Se toma la observacion del objetivo con el satelite respecto a la posicion de su
    # segunda banda de observacion y la hora actual, ademas se actualiza la bateria restante
    def takeObservationStrip2(self, satX, dayTime):
        newSatX = self.sateliteClonator(satX)
        newSatX.observations.append((newSatX.strip2, dayTime))
        newSatX.availablePowerUnits -= newSatX.observationCost
        newSatX.lastAction = "observe " + "(" + str(newSatX.strip2) + "," + str(dayTime) + ")"
        return newSatX

    # Se indica que en el momento de creacion del nuevo estado debe actualizarse la lista de objetivos pendientes
    # dado que la ultima accion ha sido transmitir, ademas se actualiza la bateria restante
    def toTransmit(self, satX):
        newSatX = self.sateliteClonator(satX)
        newSatX.availablePowerUnits -= newSatX.transmissionCost
        newSatX.lastAction = "transmit"
        return newSatX



    # UTILS////////////////////////////////////////////////////////////////////////////////////////////////////////////
    # Comprueba si el nuevo nodo se encuentra repetido en la lista que recibe por parametro
    # Se considera nodos iguales si:
    # Ambos satelites ha realizado las mismas observaciones y tienen la misma bateria en ambos nodos
    # Ambos satelites se encuentran en las mismas bandas de observacion
    # La hora es la misma
    # Quedan las mismas transmisiones por realizar
    def isSameState(self, newState, list):
        for i in range(len(list)):
            selectedState = list[i]
            if newState.sat1.observations == selectedState.sat1.observations and newState.sat2.observations == selectedState.sat2.observations \
                    and newState.sat1.strip1 == selectedState.sat1.strip1 and newState.sat1.strip2 == selectedState.sat1.strip2 \
                    and newState.sat2.strip1 == selectedState.sat2.strip1 and newState.sat2.strip2 == selectedState.sat2.strip2 \
                    and newState.time == selectedState.time and newState.sat1.availablePowerUnits == selectedState.sat1.availablePowerUnits \
                    and newState.sat2.availablePowerUnits == selectedState.sat2.availablePowerUnits and newState.objectives == selectedState.objectives:
                return i
        return -1

    # Inserta el nuevo nodo en abierta por orden
    # Se considera que un nodo tiene mejor valor que otro y por tanto se inserta antes si el valor de su funcion F es menor
    # En caso de empate se desempata por heuristica
    def insertInOpenListNeatly(self, newState, list):
        i = 0
        for i in range(len(list)):
            if newState.f < list[i].f:
                return i
            elif newState.f == list[i].f:
                if newState.heuristic < list[i].heuristic:
                    return i
                if newState.heuristic == list[i].heuristic:
                    return i
        return i

    # Retorna la hora en modulo 24
    def setNewTime(self, dayTime):
        newTime = dayTime
        if newTime + 1 == 24:
            return 0
        else:
            newTime += 1
            return newTime

    # Metodo auxiliar para clonar objetos satelite
    def sateliteClonator(self, satX):
        newSat = satelite()
        newSat.name = satX.name
        newSat.strip1 = satX.strip1
        newSat.strip2 = satX.strip2
        newSat.observations = copy.deepcopy(satX.observations)
        newSat.observationCost = satX.observationCost
        newSat.transmissionCost = satX.transmissionCost
        newSat.unitsPerCharge = satX.unitsPerCharge
        newSat.availablePowerUnits = satX.availablePowerUnits
        newSat.maxPowerUnits = satX.maxPowerUnits
        return newSat

if __name__ == "__main__":
    problem(sys.argv[1], sys.argv[2])