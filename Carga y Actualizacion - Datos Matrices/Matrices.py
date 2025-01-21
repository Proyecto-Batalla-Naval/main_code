import firebase_admin
from firebase_admin import credentials, db
import re 


#Conectar a firebase
cred = firebase_admin.credentials.Certificate(r"C:\Users\User\Documents\Visual Studio Code - Programación\Python\Firebase\Firebase compartido - Batalla naval\bookstoreproject-8b4f0-firebase-adminsdk-2eymv-b7972991ba.json")
default_app = firebase_admin.initialize_app(cred, {
    'databaseURL':"https://bookstoreproject-8b4f0-default-rtdb.firebaseio.com/"
})

#[][][][][][][][][][]-- INICIALIZACIÓN FIREBASE --[][][][][][][][][][][][][][]

#Referencia al nodo en la base de datos
refe= db.reference("Datos_del_usuario") #Genera un nodo de informacion diferente

##Funciones para conectar dos jugadores en tiempo real
'''
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

'''

#Escribir datos en tiempo real

#[][][]---------- PRUEBA ENVIO DE DATOS Matriz [][][]---------- 

# Referencias
juego = db.reference("Juego")  # Nodo principal del juego
coordenadas_juego = juego.child("Coordenadas")  # Subnodo para las coordenadas


# Funciones principales
def matrizI():
    #Crear una matriz 5x5 vacía
    return [["-" for _ in range(5)] for _ in range(5)]

def imprimirMatrix(matrizI):
    #Mostrar la matriz en consola
    for fila in matrizI:
        print(" ".join(fila)) #fusiona todo en una cadena de caracteres separada por espacios en blanco "-"
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
        fila, columna=coord.split(",") #split divide la cadena en dos partes separadas por ,
        matriz[int(fila)][int(columna)]=jugador #a la matriz se le nombran las coordenadas donde se selecciono y debe ir una X

    #mostrar la matriz actualizada
    print("Matriz actulizada con los datos ingresados con anterioridad. ")
    imprimirMatrix(matriz)


def menu():
  
    while True:
        while True:
            print("\n--- SELECION JUGADOR ---\n")
            print("1. Jugador 1 (X).")
            print("2. Jugador 2 (O)")
            print("3. Salir\n")
            opcion=input("Opcion: ")

            if(opcion=="1"):
                print("Ha selecionado ser el jugador 1.")
                jugador="X"
                break
            elif(opcion=="2"):
                print("Ha selecionado ser el jugador 2.")
                jugador="O"
                break
            elif(opcion=="3"):
                print("Saliendo del programa.")
                return opcion
            else:
                print("La opcion ingresada no es valida")


        while True:
            print("\n--- MENU ---\n")
            print("1. ingreso de coordenadas.")
            print("2. Vizualizar selecciones")
            print("3. Salir\n")
            opcion=input("Opcion: ")

            if(opcion=="1"):
                ingresoCoordenada(jugador)
                break

            elif(opcion=="2"):
                verSelecciones(jugador)
                break
            elif(opcion=="3"):
                print("Saliendo del programa, gracias.")
                return opcion
                
            else:
                print("Opcion ingresada no valida")
            
#ejecucion codigo 
menu()


#/////////////////////////////////////////////////////////////////////////////////////////////////

