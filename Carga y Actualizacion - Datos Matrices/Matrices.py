import firebase_admin
from firebase_admin import credentials, db
import re 

"""
Esta librería va a permitir: Buscar coincidencias en cadenas, validar texto, reemplazar texto,
dividir texto en partes y extraer texto de una cadena. Es especialmente útil al momento de
manejar los errores de escritura por parte del usuario :)
"""
credentials
#Conectar a firebase
cred = firebase_admin.credentials.Certificate(r"C:\Users\MIANO\Documents\Proyectos Python\Python\bookstoreproject-8b4f0-firebase-adminsdk-2eymv-b7972991ba.json")
default_app = firebase_admin.initialize_app(cred, {
    'databaseURL':"https://bookstoreproject-8b4f0-default-rtdb.firebaseio.com/"
})

#[][][][][][][][][][]-- INICIALIZACIÓN FIREBASE --[][][][][][][][][][][][][][]

#Referencia al nodo en la base de datos
refe= db.reference("Datos_del_usuario") #Genera un nodo de informacion diferente
matriz=db.reference("Coordenadas")

#Escribir datos en tiempo real

"""
#[][][][][][][][][][]-- BORRADOR MENU --[][][][][][][][][][][][][][]

#Para validar el correo electrónico
def validar_correo(correo):
    while True:
        caracteres_invalidos = r"^[a-zA-Z0-9]+(\.[a-zA-Z0-9])?@[a-zA-Z]+(\.[a-zA-Z]+)?\.[a-zA-Z]{2,}$"
        
            Se llama la librería 'Re' con la r (raw string), esto evita posibles errores y hace que
            cada letra se lea de manera literal.
            Se empieza con '^' para indicar que se lea desde el primer carácter, luego,
            se abre un [] en donde se indica que son válidos las letras mayúsculas, minúsculas
            y los dígitos una o más veces (+), opcionalmente (?), puede en otra posición [] haber letras mayúsculas,
            minúsculas y carácteres separados por UN solo punto (\.)
            Se busca un @ que esté seguido [] de letras mayúsculas, minúsculas una o más veces.
            Para el sub dominio opcional (?), se permite nuevamente letras mayúsculas y minúsculas
            una o más veces. Finalmente, para el dominio principal, se busca que luego del último punto (\.) haya
            un mínimo de 2 letras mayúsculas o minúsculas.El $ cierra 
        
        if not re.match(caracteres_invalidos, correo): #Se buscan las coincidencias de los carácteres definidos en la variable correo con la librería re
            print("Error. Asegúrese de digitar un formato válido (ej. usuario@dominio.com)") #Si no está, muestra error, un ejemplo y solicita de nuevo una opción correcta
            correo = input("Ingrese su correo electrónico: ")#Se vuelve a solicitar el correo
        else: 
            return correo #Si coincide, se guarda el valor diitado y termina el ciclo

def ingresoDatos():
    userName=input("Ingrese su UserName: ")
    examen=int(input("Cuántas veces presento el examen de la Universidad Nacional: "))
    nombre=input("Ingrese su nombre: ")
    edad=input("Ingrese su edad: ")
    correo = input("Ingrese su correo")
    correo = validar_correo(correo)
    pregunta=input("¿Disfruta de juegos de estrategia como Batalla Naval?: ")

    #diccionario de datos
    data={
        "UserName":userName,
        "Intentos_examen":examen,
        "Edad":edad,
        "Nombre":nombre,
        "Correo":correo,
        "Respuesta":pregunta

    }
    #cargar los datos
    refe.push(data)
    print("\nLos datos han sido cargados con exito.\n")

def mostrarDatos():
    datosGuardados=refe.get() #metodo get(), trae los datos ya guardados en el nodo ref, las claves ID y los datos especificos
    if(datosGuardados):
        print("\nDatos guardados en la base de datos. ")
        for key, value in datosGuardados.items(): #el metodo get() retorna la informacion de los nodos como diccionarios, el primer valor es la ID, corresponde al subnodo. y el segundo "valor" son todos los datos dentro de ese subnodo, nombre, edad ...
            username=value.get("UserName","No hay UserName")
            intentosExamen=value.get("Intentos_examen","No hay Intento_examen")
            Nombre=value.get("Nombre","No hay nombre")
            Edad=value.get("Edad","No hay edad")
            Correo=value.get("Correo","No hay correo")
            Pregunta=value.get("Respuesta","No hay respuesta")
          
            print(f" ID: {key}, UserName: {username}, Intentos: {intentosExamen},Nombre{Nombre},Edad{Edad}")
            
    else:
        print("No hay datos guardados \n") 

def sobreescribirDatos():
    userName=input("Ingrese su UserName para identificar usuario y subnodo: ")

    datoGuarda=refe.get()
    subnodo_id=None
    for key,value in datoGuarda.items():
        if(value["UserName"]==userName):
            subnodo_id=key
            break
    
    if(subnodo_id):
        #si se encontro el subnodo, se solicitan los nuevos datos
        nuevoNombre=input("Ingrese su nuevo Username: ")
        nuevosIntentos=int(input("Ingrese los intentos que realizó: "))
        nuevonombre=input("Ingrese su nuevo Nombre: ")
        nuevaedad=int(input("Ingrese su nueva Edad: "))
        nuevoCorreo=input("Ingrese su nuevo correo: ")
        nuevoCorreo=validar_correo(nuevoCorreo)
        nuevaPregunta=input("¿Disfruta de juegos de estrategia como Batalla Naval?")

        #sobreescibir datos
        nuevosDatos={
            "UserName":nuevoNombre,
            "Intentos_examen":nuevosIntentos,
            "Edad": nuevaedad,
            "Nombre": nuevonombre,
            "Correo": nuevoCorreo,
            "Pregunta": nuevaPregunta
        }

        refe.child(subnodo_id).set(nuevosDatos) #refe es el nodo el .child(id del subnodo)se posa sobre ese subnodo; .set() sobreescribe los datos
        print("Los datos han sido sobreescritos exitosamente. \n")
    else:
        print("No se encontro el UserName ingresado para actualizar los datos. \n")

def menu():
    while True:
        print("\n\t[][][][]-- MENU --[][][][]\n")
        print("1. Ingrese datos. ")
        print("2. Mostrar datos. ")
        print("3. Sobreescribir datos. ")
        print("4. Salir. ")
  
        opcion=int(input("\nSeleccione la opcion que desea realizar: "))

        if(opcion==1):
            ingresoDatos()
        elif(opcion==2):
            mostrarDatos()
        elif(opcion==3):
            sobreescribirDatos()
        elif(opcion==4):
            print("Usted esta saliendo del programa. Gracias...")
            break
        else:
            print("Opcion ingresada no valida, intente de nuevo\n")

menu()
"""
#-*-----------------------------------------------------------------------------------


#[][][]---------- PRUEBA ENVIO DE DATOS [][][]---------- 

#creacion matriz 
def matrix():
    return[["-" for _ in range(5)] for _ in range(5)] #for anidado, crea las filas y las columnas directamente es un 5x5

def imprimirMatrix(matrix): #mostrar la matriz generada
    for fila in matrix:
        print(" ".join(fila))
    print()

#coordenada al firebase subirlos
def SubCoordenada(fila,columna,jugador):
    matriz.set({
        "Fila":fila,
        "Columna":columna,
        "Jugador":jugador
    })

#coordenada recibida
def recibirCambios(matrix):
    print("Esperando actualizaciones de coordenadas en la matriz...")

    def actualizacion(event):
        datos=event.data

        if(datos):
            fila, columna, jugador=datos["Fila"],datos["Columna"],datos["Jugador"]
            matriz[fila][columna]=jugador
            print(f"El jugador {jugador} seleccionó la coordenada ({fila},{columna}\n)")
            imprimirMatrix(matrix)
    
    matriz.listen(update_type="value", listener=actualizacion)

#Planteamiento de nuevo menu
def Menu():
    print("Bienvenido al juego. ")
    print("Iniciando...")
    matriz=matrix()
    imprimirMatrix(matriz)

    print("1. Marcar coordenada.")
    print("2. Ver las actualizaciones. ")
    seleccion=int(input("Su opcion escogida es: "))

    if(seleccion==1):
        jugador=input("¿Qué jugador es?, ¿J1 O J2?")
        while True:
            fila=int(input("Ingrese datos de la fila (0-4)"))
            columna=int(input("Ingresa datos de la columna (0-4)"))
            if(0<=fila<5 and 0<=columna<5):
                SubCoordenada(fila,columna,jugador)
                print(f"Marco la coordenada ({fila},{columna}) siendo el jugador {jugador}")
                break
            else:
                print("Coordenadas seleccionadas invalidas")
                break
    elif(seleccion==2):
        recibirCambios(matriz)
    else:
        print("La selección es invalida ")


Menu()
##Para correr Batalla Naval
##------------------------------------------------------------------------------------------------------------
import random
import time
##--------------------------------------------------------------------------------
##CREACION DE CUADRICULA DEL TABLERO Y UBICACION DE POSICION DE LOS BARCOS
##Creacion del tablero
##Definir una variable global para el tablero como una lista
Tablero=[[]]
##Definir el tamaño del tablero
Tamaño_tablero=10
##Definimos la cantidad de barcos
Cantidad_barcos=5
##Definimos la cantidad de cañones o ataques
Cantidad_cañones=30
##Definimos la variable para cuando se acaben las oportunidades de ataque o para cuando todos los barcos hayan 
##o para cuando todos los barcos hayan sido derribados 
Fin_del_juego=False
##Definimos la variable para los barcos derribados
Barcos_derribados=0
##Definimos la variable para la posicion de los barcos como una lista
Posicion_barcos=[[]]
##Determinamos las letras de las coordenadas del tablero
Letras_coordenadas="ABCDEFGHIJ"
##------------------------------------------------------------------
##Con las variables ya creadas empezamos con la creacion de funciones 
##La primera funcion va a ser para validar el tablero y colocar la posicion de los barcos 
##Definimos como parametros de la funcion las medidas del tablero,donde comienza
##la fila y donde termina y asi mismo con las columnas
def Tablero_y_posicion_barcos(Inicio_fila,Final_fila,Inicio_columna,Final_columna):
##Esto nos va a permitir conocer si donde clickeamos se encuentra un barco o no
##Llamamos con global las variables creadas fuera de la funcion para
##que se modifiquen dentro de la funcion 
    global Tablero
    global Posicion_barcos
##Ahora vamos a comprobar si todas las posiciones han sido validadas 


    Posiciones_validadas=True
##Con un for dentro de los rangos que componen el tablero
##tanto filas como columnas
    for i in range(Inicio_fila,Final_fila):
        for j in range(Inicio_columna,Final_columna):
##Utilizaremos el simbolo * para
##determinar que ese es un espacio vacio en donde no se 
##encuentran barcos,por lo que si en el tablero,al revisar
##en filas y columnas se encuentra un simbolo diferente 
## al * del espacio vacios devuelve falso y se rompe el bucle
            if Tablero[i] [j] != "*":
                Posiciones_validadas=False
                break
##Si en el anterior bucle fue validado True(quiere decir que no encontramos nada)
##podemos crear un barco 
##Crearemos un if con la variable de posiciones validadas  
##y en su cuerpo usaremos el metodo .append con la  variable  
##posicion de los barcos para agregar las coordenadas de inicio y fin
##tanto en filas como en columnas para asi ubicar los barcos 
##para mantener un registro de donde pusimos el barco
## y asi conocer si todo el barco ha sido hundido

    if Posiciones_validadas:
        Posicion_barcos.append([Inicio_fila,Final_fila,Inicio_columna,Final_columna])
        for i in range(Inicio_fila,Final_fila):
            for j in range(Inicio_columna,Final_columna):
##Nuevamente utilizamos el for en filas y columnas                
                Tablero[i] [j] = "+"
##Definimos que la posicion de los barcos en el Tablero va 
##a ser modificada con otro simbolo
##en i(filas) y en j(columnas) es equivalente
##por a el simbolo + que va a representar  
## las partes que abarca el navio en la cuadricula 
## en vez del * que representaba el vacio              
                return Posiciones_validadas
##Devolvemos el valor de las Posiciones validadas
##------------------------------------------------------------------------------
##Ahora vamos a ubicar un barco en la cuadricula 
##Creamos la funcion 
def Ubicar_barco_cuadricula(Fila,Columna,Direccion,Longitud):
##Le introducimos a la funcion como parametros la fila,columna
##direccion(como se ubicara el barco)y la cantidad de espacios
##que ocupara o su longitud en la cuadricula
    global Tamaño_tablero
##Llamamos nuevamente con global la variable creada fuera de la funcion para
##que se modifique dentro de la funcion 
    Inicio_fila,Final_fila,Inicio_columna,Final_columna = Fila,Fila+1,Columna,
    Columna+1 
##Definimos las variables que utilizaremos,en este caso son,el inicio y fin 
##de filas y columnas que se ajustaran a las casillas del tablero 
##para que se ajuste el rango de las posiciones le sumamos a cada fila y columna 1 
##esto las ajustara a la longitud del barco dependiendo de la direccion 
##Fila es donde comienza el barco al colocarlo(Inicio_fila)
##Fila + 1 es donde termina el barco de ser colocado(Final_fila)
##Columna es donde comienza el barco al colocarlo(Inicio_columna)
##Columna + 1 es donde termina el barco de ser colocado(Final_columna)
    if Direccion.lower() == "izquierda":
##Usaremos un if para conocer cual es la direccion que se nos esta indicando
##tambien haremos uso del metodo .lower para que no hayan confusiones 
##al digitar la direccion
        if Columna - Longitud < 0:
##Ahora vamos a validar que la posicion seleccionada sea correcta 
##si la columna menos la longitud es menor que 0 quiere decir
##que nos estamos saliendo de los limites del tablero y por ello 
##devuelve false pues la posicion no es valida 
            return False
        Inicio_columna = Columna - Longitud + 1
       
##Si la posicion esta bien entonces procedera restar la 
##columna inicial con la longitud mas 1 para asi ajustar
##el calculo del espacio inicial(columna) con la cantidad
##de espacios ocupados(longitud),desplazandose hacia 
##la izquierda desde el punto inicial(tomandolo)para 
##no sobrepasar los limites del tablero
    elif Direccion.lower() == "derecha":
        if Columna + Longitud >= Tamaño_tablero:
            return False
##Hacemos lo mismo con la direccion a la derecha 
##en este caso es para verficar que no nos salgamos
##de los limites del tablero y si lo hacemos
##retorna Falso
        Final_columna = Columna + Longitud 
##Para ajustar la posicion final de la columna 
##tras comprobar que no salga de los limites
##se suma la columna inicial con la longitud 
    elif Direccion.lower() == "arriba":
        if Fila - Longitud < 0:
            return False
        Inicio_fila = Fila - Longitud + 1
    elif Direccion.lower() == "abajo":
        if Fila + Longitud >= Tamaño_tablero:
            return False
        Final_fila = Fila + Longitud 
##Realizamos el mismo codigo para cada direccion
##tanto en inicio como en fin de fila y columna 
    return Tablero_y_posicion_barcos(Inicio_fila,Final_fila,Inicio_columna,Final_columna)
##Para devolver un valor llamamos a la funcion creada que 
##nos permite saber si en el espacio clickeado se encuentra o no un barco
def Crear_tablero():
    global Tablero
    global Tamaño_tablero
    global Cantidad_barcos
    global Posicion_barcos
    random.seed(time.time())

    filas,columnas=(Tamaño_tablero,Tamaño_tablero)
    Tamaño_tablero=[]
    for r in range(filas):
        fila=[]
        for i in range(columnas):
            fila.append("*")
        Tablero.append(fila)
    Numero_de_barcos_puestos= 0
    Posicion_barcos= []
    while Numero_de_barcos_puestos != Cantidad_barcos:
        random_fila = random.randint(0,filas-1)
        random_columna= random.randint(0,columnas-1)
        Direccion= random.choice(["izquierda","derecha","arriba","abajo"])
        Medida_del_barco= random.randint(3,5)
        if Posicion_barcos(random_fila,random_columna,Direccion,Medida_del_barco):
            Numero_de_barcos_puestos+= 1
def Mostrar_Tablero():
    global Tablero
    global Letras_coordenadas
    Depuracion= True

    Letras_coordenadas= Letras_coordenadas[0:len(Tablero)+1]
    for fila in range(len(Tablero)):
        print(Letras_coordenadas(fila),end=")")
        for columna in range(len(Tablero[fila])):
            if Tablero[fila][columna]=="0":
                if Depuracion:
                    print("0",end=" ")
                else:
                    print("*")
            else:
                print(Tablero[fila][columna],end=" ")
        print("")
    print(" ",end=" ")
    for r in range(len(Tablero[0])):
        print(str(r),end=" ")
    print("")
def Aceptar_cañon_valido():
    global Letras_coordenadas
    global Tablero
    Lugar_Valido= False
    fila= -1
    columna= -1
    while Lugar_Valido is False:
        Colocacion= input("Por favor siga el ejemplo:\nB4\no\nE9\nIngrese una fila(entre las letras A-J) y una columna (entre los números 0-9):\n") 
        Colocacion=Colocacion.upper()
        if len(Colocacion) <=0 or len(Colocacion)> 2:
            print("Error: Por favor ingrese UNICAMENTE\nUNA fila y UNA columna: \n")
            continue
        fila=Colocacion[0]
        columna=Colocacion[1]
        if not fila.isalpha() or not columna.isnumeric():
            print("Error: Por favor ingrese letras para las filas:\nDe la A a la J\ny números para las columnas:\nDel 0 al 9:\n")
            continue
        fila= Letras_coordenadas.find(fila)
        if not (-1 < fila < Tamaño_tablero):
            print("Error: Por favor ingrese letras para las filas:\nDe la A a la J\ny números para las columnas:\nDel 0 al 9:\n")
            continue
        columna=int(columna)
        if not (-1 < columna < Tamaño_tablero):
            print("Error: Por favor ingrese letras para las filas:\nDe la A a la J\ny números para las columnas:\nDel 0 al 9:\n")
            continue
        if Tablero[fila][columna]== "$" or Tablero[fila][columna]=="X":
            print("Usted ya ha disparado un cañon aquí,por favor elija otro lugar,para realizar su disparo")
            continue
        if Tablero[fila][columna]== "*" or Tablero[fila][columna]=="0":
            Lugar_Valido = True
    return fila,columna
def Validar_barco_hundido(fila,columna):
    global Posicion_barcos
    global Tablero
    for Posicion in Posicion_barcos:
        Inicio_fila= Posicion [0]
        Final_fila= Posicion [1]
        Inicio_columna= Posicion [2]
        Final_columna= Posicion [3]
        if Inicio_fila <= fila <= Final_fila and Inicio_columna <= columna <= Final_columna:
            for r in range(Inicio_fila,Final_fila):
                for i in range(Inicio_columna,Final_columna):
                    if Tablero [r][i] != "X":
                        return True
def Disparo_cañon():
    global Tablero
    global Barcos_derribados
    global Cantidad_cañones     
    fila,columna= Aceptar_cañon_valido()  
    print("")
    print("----------------------------------")

    if Tablero[fila][columna]== "*":
        print("Disparo fallido,ningún barco fue hundido")
        Tablero[fila][columna]="$"
    elif Tablero[fila][columna]=="0":
        print("Ha disparado",end=" ")
        Tablero[fila][columna]="X"
        if Validar_barco_hundido(fila,columna):
            print("¡El barco ha sido completamente hundido!")
            Barcos_derribados+= 1
        else:
            print("¡Le ha dado a un barco!")
    Cantidad_cañones -= 1
def Validar_fin_juego():
    global Barcos_derribados
    global Cantidad_barcos
    global Cantidad_cañones
    global Fin_del_juego
    if Cantidad_barcos == Barcos_derribados:
        print("Felicidades ha ganado")
        Fin_del_juego= True
    elif Cantidad_cañones <= 0:
        print("Usted ha perdido,intentelo de nuevo en una próxima ocasión") 
        Fin_del_juego= True
def main():
    global Fin_del_juego
    print("Bienvenido a Batalla Naval")
    print("Usted tiene 30 balas de cañon para hundir 5 barcos")
    Crear_tablero()
    while Fin_del_juego is False:
        Mostrar_Tablero()
        print("Número de barcos restantes"+ str(Cantidad_barcos-Barcos_derribados))
        print("Numero de balas de cañon"+str(Cantidad_cañones))
        Disparo_cañon()
        print("---------------------------------------------------")
        print("")
        Validar_fin_juego

main()

