################################################################################################################
#Se inicializa firebase
import firebase_admin
from firebase_admin import credentials, db

# Inicializamos la conexión con Firebase
cred = credentials.Certificate(r"bookstoreproject-8b4f0-firebase-adminsdk-2eymv-b7972991ba.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://intro-firebase-be732-default-rtdb.firebaseio.com/'
})

#Para conectar a los dos jugadores en el mismo juego, es necesario crear un ID único, para esto se usa push
def crear_juego(jugador_1, jugador_2):#Se hace una función que establezca los nombres de los juadores, los tableros vacíos y el primer turno
    game_ref = db.reference('Batalla Naval').push() #Se hace un único game ID con push y con el reference se crea un nuevo nodo llamado "Batalla Naval"
    game_id = game_ref.key  #Este es el game ID único para la partida, conocido como key, fundamental porque es identificador único del registro en la base de datos.
    game_ref.set({ #Almacena datos sobreescribiendo los que estén almacenados en el nodo "Batalla Naval" con set
        'Jugador_1': 'Jugador1_nombre',
        'Jugador2': 'Jugador2_nombre',
        'Turno': 'Jugador1',
        'Tablero_jugador1': [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]], #Los tableros están vacíos por el momento
        'Tablero_jugador2': [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]],
        'Estado': 'ongoing'
    })
    print(f'El ID del juego es: {game_id}')
    return game_id #La función va a devolver el ID único que permitirá la conexión

def unirse_al_juego(game_id): #Se hace una función que permita que otro jugador se conecte a la misma partida usando el ID único creado anteriormente
    game_ref = db.reference(f'Batalla Naval/{game_id}') #Se hace la referencia al nodo "Batalla Naval" para crear un subnodo dentro de este principal llamado game_id
    game_existe = game_ref.get() #game ref contiene los datos del juego, así que get leerá los valores y verificará que sí existan. Si sí lo hacen, estos se recuperarán en game_existe
    if game_existe: #Si los datos existen
        print(f'Juego encontrado: {game_existe['Jugador1']} vs {game_existe['Jugador2']}') #Se imprime la información indicando que {game_existe} es el diccionario en donde están almacenadas las claves 'Jugador1' y 'Jugador2'
        print("Ahora pueden actualizar el juego en tiempo real")
        return game_ref #Se retorna la referencia al juego para que el programa pueda seguir interactuando con el nodo "Batalla Naval"

    else:
        print('Juego no encontrado')
        return None #No hay referencia válida al juego

#Juego provisional no revisado
###########################################################################
# Funciones Provisionales para Simular el Juego
def estado_del_juego(game_id):
    """Función provisional para simular el estado del juego."""
    return "en curso"

# Función Principal del Juego
def jugar(game_id, jugador1, jugador2):
    print("El juego ha comenzado.")
    turno_actual = jugador1  # Comienza el turno de jugador1.

    while True:
        print(f"Es el turno de {turno_actual}.")
        input(f"{turno_actual}, haz tu movimiento (presiona Enter para continuar).")
        
        # Verifica el estado del juego
        if estado_del_juego(game_id) == "terminado":
            print("El juego ha terminado.")
            break

        # Alterna el turno
        turno_actual = jugador2 if turno_actual == jugador1 else jugador1

# Menú Interactivo
def menu():
    while True:
        print("Bienvenido a Batalla Naval!")
        print("1. Crear un juego")
        print("2. Unirse a un juego")
        print("3. Salir")

        opcion = input("Elige una opción: ")

        if opcion == "1":
            jugador1 = input("Ingresa tu nombre (Jugador 1): ")
            jugador2 = input("Ingresa el nombre del Jugador 2: ")  # Provisional, ambos en una máquina
            game_id = crear_juego(jugador1, jugador2)
            jugar(game_id, jugador1, jugador2)
        elif opcion == "2":
            game_id = input("Ingresa el Game ID: ")
            unirse_al_juego(game_id)
            # Aquí podrías llamar a `jugar()` si ambos jugadores están conectados.
        elif opcion == "3":
            print("Saliendo del juego. ¡Hasta luego!")
            break
        else:
            print("Opción no válida. Inténtalo de nuevo.")

# Ejecuta el Menú
menu()





