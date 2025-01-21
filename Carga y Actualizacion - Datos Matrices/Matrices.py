import firebase_admin
from firebase_admin import credentials, db
import re 


#Conectar a firebase
cred = firebase_admin.credentials.Certificate(r"C:\Users\MIANO\Documents\Proyectos Python\Python\bookstoreproject-8b4f0-firebase-adminsdk-2eymv-b7972991ba.json")
default_app = firebase_admin.initialize_app(cred, {
    'databaseURL':"https://bookstoreproject-8b4f0-default-rtdb.firebaseio.com/"
})

#[][][][][][][][][][]-- INICIALIZACIÓN FIREBASE --[][][][][][][][][][][][][][]
#peticion de borrar datos inicial 
#se podria crear dos nodos y restingir el codigo a la seleccion inicial hasta que se cierre el programa 
#menu de inicio o creacion de partida, al crearla
#variable de juego para los turnos, hacer la peticion de autenticar atributo para los turnos
#coordenada de jugador 1 y 2

#Referencia al nodo en la base de datos
refe= db.reference("Datos_del_usuario") #Genera un nodo de informacion diferente

##Funciones para conectar dos jugadores en tiempo real

#Escribir datos en tiempo real

#[][][]---------- PRUEBA ENVIO DE DATOS Matriz [][][]---------- 

# Referencias
juego = db.reference("Juego")  # Nodo principal del juego
#coordenadas_juego = juego.child("Coordenadas")  # Subnodo para las coordenadas
jugador_1=juego.child("Jugador_1")#se crea un subnodo
jugador_2=juego.child("Jugador_2")



def seleccionJugador():
    while True:
        print("\n--- SELECION JUGADOR ---\n")
        print("1. Jugador 1 (X).")
        print("2. Jugador 2 (O)")
        print("3. Salir\n")
        opcion=input("Opcion: ")

        if(opcion=="1"):
            print("Ha selecionado ser el jugador 1.")
            return "x", db.reference("Juego/Jugador_1/Coordenada") #nodo para el jugador 1
        elif(opcion=="2"):
            print("Ha selecionado ser el jugador 2.")
            return "O", db.reference("Juego/Jugador_2/Coordenada") #Nodo para el jugaodr 2 
        elif(opcion=="3"):
            print("Saliendo del programa.")
            return None, None
        else:
            print("La opcion ingresada no es valida")
    

# Funciones principales
def matrizI():
    #Crear una matriz 5x5 vacía
    return [["-" for _ in range(5)] for _ in range(5)]

def imprimirMatrix(matrizI):
    #Mostrar la matriz en consola
    for fila in matrizI:
        print(" ".join(fila)) #fusiona todo en una cadena de caracteres separada por espacios en blanco "-"
    print()

def limpiarMatriz(coordenadas_juego):
    print("Eliminando los datos previos del tablero")
    coordenadas_juego.delete()
    print("Los datos han sido eliminados correctamente")

        
def ingresoCoordenada(jugador,coordenadas_juego):
    coordenadaActuales=coordenadas_juego.get() or {}
    matriz=matrizI()

    #actualizar matriz con las coordenadas exitentes
    for coord in coordenadaActuales.values():
        fila, columna=coord.split(",") #split divide la cadena en dos partes separadas por ,
        matriz[int(fila)][int(columna)]=jugador #a la matriz se le nombran las coordenadas donde se selecciono y debe ir una X
    
    #pedir la coordenada
    while True:
        print("Ingrese la coordenada deseada en el formato: (fila,columna): ")
        coordenada=input()

        #validar la coordenada
        if not re.match(r"^[0-4],[0-4]$",coordenada):
            print("La coordenada ingresada es incorrecta, respete el rango propuesto.")
            continue #hace que el programa se vuelva a ejecutar, saltandose todo lo que hay despues

        #verificar si esa coordenada ya esta ocupada
        if(coordenada in coordenadaActuales.values()):
            print("la coordenada seleccionada ya esta ocupada, elija otra.")
        else:
            fila,columna=coordenada.split(",")#nuevamente se separa la coordenada por una ,
            matriz[int(fila)][int(columna)]=jugador
            coordenadas_juego.push(coordenada) #carga la coordenada en la base de datos
            print(f"Coordenada {coordenada} guardada exitosamente")
            break
    #imprimirMatrix(matriz)


def verSelecciones(jugador,coordenadas_juego):
    #traer los datos de coordenada guardados en firebase
    coordenadaActuales=coordenadas_juego.get() or {}
    matriz=matrizI()

    #actualizar matriz con las coordenadas exitentes
    for coord in coordenadaActuales.values():
        fila, columna=coord.split(",") #split divide la cadena en dos partes separadas por ,
        matriz[int(fila)][int(columna)]=jugador #a la matriz se le nombran las coordenadas donde se selecciono y debe ir una X

    #mostrar la matriz actualizada
    print("Matriz actulizada con los datos ingresados con anterioridad. ")
    imprimirMatrix(matriz)


def menu():

    print("Configurando el tablero.")
    jugador,coordenadas_juego=seleccionJugador() #seleccion del jugador y nodo asociado 
    if not jugador: #si seleccionan "salir"
        return

    limpiarMatriz(coordenadas_juego)
  
    while True:

        while True:
            print("\n--- MENU ---\n")
            print("1. ingreso de coordenadas.")
            print("2. Vizualizar selecciones")
            print("3. Salir\n")
            opcion=input("Opcion: ")

            if(opcion=="1"):
                ingresoCoordenada(jugador,coordenadas_juego)
                break

            elif(opcion=="2"):
                verSelecciones(jugador,coordenadas_juego)
                break
            elif(opcion=="3"):
                print("Saliendo del programa, gracias.")
                return opcion
                
            else:
                print("Opcion ingresada no valida")
            
#ejecucion codigo 
menu()


#/////////////////////////////////////////////////////////////////////////////////////////////////
