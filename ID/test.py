import firebase_admin
from firebase_admin import credentials, db
import re

# Inicializamos la conexión con Firebase
cred = credentials.Certificate(r"C:\Users\danim\Downloads\intro-firebase-be732-firebase-adminsdk-fbsvc-d358dd2812.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://intro-firebase-be732-default-rtdb.firebaseio.com/'
})

# Función para crear un tablero vacío
def crear_tablero():
    return {f"{fila}_{columna}": 0 for fila in range(5) for columna in range(5)}

# Función para crear un nuevo juego
def crear_juego(jugador_1, jugador_2):
    game_ref = db.reference('Batalla Naval').push()
    game_id = game_ref.key
    game_ref.set({
        'jugador_1': jugador_1,
        'jugador_2': jugador_2,
        'Turno': 'jugador_1',
        'Tablero_jugador1': crear_tablero(),
        'Tablero_jugador2': crear_tablero(),
        'Estado': 'ongoing',
        'coordenadas_jugador1': {},  # Coordenadas del Jugador 1
        'coordenadas_jugador2': {},  # Coordenadas del Jugador 2
    })
    print(f'El ID del juego es: {game_id}')
    return game_id

# Función para unirse a un juego
def unirse_al_juego(game_id):
    game_ref = db.reference(f'Batalla Naval/{game_id}')
    game_existe = game_ref.get()
    if 'jugador_1' in game_existe and 'jugador_2' in game_existe:
        print(f"Juego encontrado: {game_existe['jugador_1']} vs {game_existe['jugador_2']}")
    else:
        print("El juego no tiene jugadores registrados.")

# Función para crear una matriz vacía 5x5
def matrizI():
    return [["-" for _ in range(5)] for _ in range(5)]

# Función para imprimir la matriz
def imprimirMatrix(matriz):
    for fila in matriz:
        print(" ".join(fila))
    print()

# Función para ingresar coordenada
def ingresoCoordenada(game_id, jugador):
    game_ref = db.reference(f'Batalla Naval/{game_id}')
    coordenadas_actuales = game_ref.child(f'coordenadas_{jugador}').get() or {}
    matriz = matrizI()

    # Actualizar matriz con las coordenadas existentes
    for coord in coordenadas_actuales.values():
        fila, columna = coord.split(",")
        # Asignar 'X' o 'O' dependiendo del jugador
        matriz[int(fila)][int(columna)] = 'X' if jugador == 'jugador_1' else 'O'

    while True:
        print(f"Ingrese la coordenada deseada en el formato: (fila,columna): ")
        coordenada = input()

        # Validar coordenada
        if not re.match(r"^[0-4],[0-4]$", coordenada):
            print("La coordenada ingresada es incorrecta, respete el rango propuesto.")
            continue

        # Verificar si esa coordenada ya está ocupada
        if coordenada in coordenadas_actuales.keys():
            print("La coordenada seleccionada ya está ocupada, elija otra.")
        else:
            fila, columna = coordenada.split(",")
            # Asignar 'X' o 'O' dependiendo del jugador
            matriz[int(fila)][int(columna)] = 'X' if jugador == 'jugador_1' else 'O'
            game_ref.child(f'coordenadas_{jugador}').push(coordenada)  # Guardar las coordenadas en el nodo correspondiente
            print(f"Coordenada {coordenada} guardada exitosamente")
            break

    imprimirMatrix(matriz)

# Función para ver las selecciones de los jugadores
def verSelecciones(game_id, jugador):
    game_ref = db.reference(f'Batalla Naval/{game_id}')
    coordenadas_actuales = game_ref.child(f'coordenadas_{jugador}').get() or {}
    matriz = matrizI()

    # Actualizar matriz con las coordenadas existentes
    for coord in coordenadas_actuales.values():
        fila, columna = coord.split(",")
        # Asignar 'X' o 'O' dependiendo del jugador
        matriz[int(fila)][int(columna)] = 'X' if jugador == 'jugador_1' else 'O'

    print(f"Matriz actualizada con las coordenadas del {jugador}.")
    imprimirMatrix(matriz)

# Menú principal del programa
def menu():
    while True:
        print("\n--- MENÚ PRINCIPAL ---\n")
        print("1. Crear un nuevo juego.")
        print("2. Unirse a un juego existente.")
        print("3. Salir.\n")
        opcion = input("Opción: ")

        if opcion == "1":
            jugador_1 = input("Ingrese el nombre del Jugador 1: ")
            jugador_2 = input("Ingrese el nombre del Jugador 2: ")
            game_id = crear_juego(jugador_1, jugador_2)
            print(f"¡Juego creado! El ID del juego es: {game_id}.")
            print("Comparta este ID con el segundo jugador para que se una.")
            seleccionar_jugador(game_id)
        
        elif opcion == "2":
            game_id = input("Ingrese el ID del juego al que desea unirse: ")
            unirse_al_juego(game_id)
            seleccionar_jugador(game_id)
        
        elif opcion == "3":
            print("Saliendo del programa. ¡Hasta la próxima!")
            break
        else:
            print("Opción inválida. Por favor, seleccione una opción válida.")

# Menú para seleccionar jugador
def seleccionar_jugador(game_id):
    game_ref = db.reference(f'Batalla Naval/{game_id}')
    while True:
        print("\n--- SELECCIÓN JUGADOR ---\n")
        print("1. Soy el Jugador 1.")
        print("2. Soy el Jugador 2.")
        print("3. Regresar al menú principal.\n")
        seleccion = input("Opción: ")

        if seleccion == "1":
            print("¡Eres el Jugador 1 (X)!")
            manejar_juego(game_ref, game_id, "jugador_1", "X")  # Empieza el juego como Jugador 1
            break
        elif seleccion == "2":
            print("¡Eres el Jugador 2 (O)!")
            manejar_juego(game_ref, game_id, "jugador_2", "O")  # Empieza el juego como Jugador 2
            break
        elif seleccion == "3":
            print("Regresando al menú principal...")
            return  # Regresa al menú principal
        else:
            print("Opción inválida. Por favor, seleccione una opción válida.")

# Manejo del juego
def manejar_juego(game_ref, game_id, jugador, simbolo):
    while True:
        print("\n--- MENÚ DEL JUEGO ---\n")
        print("1. Ingresar coordenadas.")
        print("2. Visualizar tablero.")
        print("3. Salir.\n")
        opcion = input("Opción: ")

        if opcion == "1":
            ingresoCoordenada(game_id, jugador)
            # Cambiar turno
            if jugador == "jugador_1":
                game_ref.update({"Turno": "jugador_2"})
            else:
                game_ref.update({"Turno": "jugador_1"})
        elif opcion == "2":
            verSelecciones(game_id, jugador)
        elif opcion == "3":
            print("Saliendo del juego. Regresando al menú principal.")
            break
        else:
            print("Opción inválida. Por favor, seleccione una opción válida.")

# Ejecutar el juego
menu()
