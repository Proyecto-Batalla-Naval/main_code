################################################################################################################
#Se inicializa firebase
import firebase_admin
from firebase_admin import credentials, db
import re

# Inicializamos la conexión con Firebase
cred = credentials.Certificate(r"C:\Users\danim\Downloads\intro-firebase-be732-firebase-adminsdk-fbsvc-d358dd2812.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://intro-firebase-be732-default-rtdb.firebaseio.com/'
})
coordenadas_juego = db.reference('coordenadas_juego') #Variable con la referencia al nodo en firebase

#Para conectar a los dos jugadores en el mismo juego, es necesario crear un ID único, para esto se usa push
def crear_juego(jugador_1, jugador_2):#Se hace una función que establezca los nombres de los juadores, los tableros vacíos y el primer turno
    game_ref = db.reference('Batalla Naval').push() #Se hace un único game ID con push y con el reference se crea un nuevo nodo llamado "Batalla Naval"
    game_id = game_ref.key  #Este es el game ID único para la partida, conocido como key, fundamental porque es identificador único del registro en la base de datos.
    game_ref.set({ #Almacena datos sobreescribiendo los que estén almacenados en el nodo "Batalla Naval" con set
        'jugador_1': 'Jugador1_nombre',
        'jugador2': 'Jugador2_nombre',
        'Turno': 'jugador1',
        'Tablero_jugador1': [[0] * 5 for _ in range(5)],#Se crea el tablero vacío
        'Tablero_jugador2': [[0] * 5 for _ in range(5)],

        'Estado': 'ongoing'
    })
    print(f'El ID del juego es: {game_id}')
    return game_id #La función va a devolver el ID único que permitirá la conexión

def unirse_al_juego(game_id): #Se hace una función que permita que otro jugador se conecte a la misma partida usando el ID único creado anteriormente
    game_ref = db.reference(f'Batalla Naval/{game_id}') #Se hace la referencia al nodo "Batalla Naval" para crear un subnodo dentro de este principal llamado game_id
    game_existe = game_ref.get() #game ref contiene los datos del juego, así que get leerá los valores y verificará que sí existan. Si sí lo hacen, estos se recuperarán en game_existe
    if 'Jugador_1' in game_existe and 'Jugador2' in game_existe:
        print(f"Juego encontrado: {game_existe['Jugador_1']} vs {game_existe['Jugador2']}")
    else:
        print("El juego no tiene jugadores registrados.")


# Funciones principales
def matrizI():
    #Crear una matriz 5x5 vacía
    return [["-" for _ in range(5)] for _ in range(5)]

def imprimirMatrix(matriz):#Se cambia el nombre de la variable para evitar confusiones
    for fila in matriz:
        print(" ".join(fila))
    print()

def ingresoCoordenada(jugador):
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


def verSelecciones(jugador):
    #traer los datos de coordenada guardados en firebase
    coordenadaActuales=coordenadas_juego.get() or {}
    matriz=matrizI()

    #actualizar matriz con las coordenadas exitentes
    for coord in coordenadaActuales.values():
        fila, columna = coord.split(",")
        matriz[int(fila)][int(columna)] = jugador


    #mostrar la matriz actualizada
    print("Matriz actulizada con los datos ingresados con anterioridad. ")
    imprimirMatrix(matriz)


# Menú principal
def menu():
    while True:
        print("\n--- MENÚ PRINCIPAL ---\n")
        print("1. Crear un nuevo juego.")
        print("2. Unirse a un juego existente.")
        print("3. Salir.\n")
        opcion = input("Opción: ")

        if opcion == "1":
            jugador_1 = input("Ingrese el nombre del Jugador 1: ")
            jugador_2 = input("Ingrese el nombre del Jugador 2 (puede ser añadido luego): ")
            game_id = crear_juego(jugador_1, jugador_2)  # Crea un nuevo juego
            print(f"El juego ha sido creado exitosamente. Comparta este ID con el otro jugador: {game_id}")
        elif opcion == "2":
            game_id = input("Ingrese el ID del juego para unirse: ")
            game_ref = unirse_al_juego(game_id)  # Intenta conectarse al juego con el ID proporcionado

            if game_ref:
                print("¡Conexión exitosa al juego!")
                jugador = seleccionar_jugador(game_ref)  # Selecciona si eres Jugador 1 o Jugador 2
                manejar_juego(game_ref, jugador)  # Comienza el juego
            else:
                print("Error: No se pudo conectar al juego. Verifique el ID.")
        elif opcion == "3":
            print("Saliendo del programa. ¡Gracias por jugar!")
            break
        else:
            print("Opción ingresada no válida.")

# Función para seleccionar jugador
def seleccionar_jugador(game_ref):
    while True:
        print("\n--- SELECCIÓN DE JUGADOR ---\n")
        print("1. Soy el Jugador 1.")
        print("2. Soy el Jugador 2.")
        print("3. Salir.\n")
        opcion = input("Opción: ")

        if opcion == "1":
            return "Jugador_1"
        elif opcion == "2":
            return "Jugador2"
        elif opcion == "3":
            print("Regresando al menú principal.")
            return None
        else:
            print("Opción ingresada no válida.")

# Función para manejar el juego
def manejar_juego(game_ref, jugador):
    if not jugador:
        return

    while True:
        print("\n--- MENÚ DE JUEGO ---\n")
        print("1. Ingresar coordenadas.")
        print("2. Visualizar el tablero.")
        print("3. Salir del juego.\n")
        opcion = input("Opción: ")

        if opcion == "1":
            ingresoCoordenada(jugador)
        elif opcion == "2":
            verSelecciones(jugador)
        elif opcion == "3":
            print("Saliendo del juego. ¡Hasta luego!")
            break
        else:
            print("Opción ingresada no válida.")
############################################
menu()
