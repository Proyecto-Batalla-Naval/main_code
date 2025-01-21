################################################################################################################
#Se inicializa firebase
import firebase_admin
from firebase_admin import credentials, db

# Inicializamos la conexión con Firebase
cred = credentials.Certificate('intro-firebase-be732-firebase-adminsdk-fbsvc-d358dd2812.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://intro-firebase-be732-default-rtdb.firebaseio.com/'
})

#Para conectar a los dos jugadores en el mismo juego, es necesario crear un ID único, para esto se usa push
def crear_juego(jugador_1, jugador_2):#Se hace una función que cumpla este rerquerimiento
    game_ref = db.reference('Batalla Naval').push() #Se hace un único game ID con push y con el reference se crea un nuevo nodo llamado "Batalla Naval"
    game_id = game_ref.key  #Este es el game ID único para la partida, conocido como key, fundamental porque es identificador único del registro en la base de datos.
    game_ref.set({ #Almacena datos sobreescribiendo los que estén almacenados en el nodo "Batalla Naval" con set
        'Jugador_1': 'Jugador1_nombre',
        'Jugador2': 'Jugador2_nombre',
        'Truno': 'Jugador1',
        'Tablero_jugador1': [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]], #Los tableros están vacíos por el momento
        'Tablero_jugador2': [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]],
        'Estado': 'ongoing'
    })
    return game_id #La función va a devolver el ID único que permitirá la conexión


