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
cred = firebase_admin.credentials.Certificate(r"bookstoreproject-8b4f0-firebase-adminsdk-2eymv-b7972991ba.json")
default_app = firebase_admin.initialize_app(cred, {
    'databaseURL':"https://bookstoreproject-8b4f0-default-rtdb.firebaseio.com/"
})

#[][][][][][][][][][]-- INICIALIZACIÓN FIREBASE --[][][][][][][][][][][][][][]

#Referencia al nodo en la base de datos
refe= db.reference("Datos_del_usuario") #Genera un nodo de informacion diferente


#Escribir datos en tiempo real
#[][][][][][][][][][]-- BORRADOR MENU --[][][][][][][][][][][][][][]

#Para validar el correo electrónico
def validar_correo(correo):
    while True:
        caracteres_invalidos = r"^[a-zA-Z0-9]+(\.[a-zA-Z0-9])?@[a-zA-Z]+(\.[a-zA-Z]+)?\.[a-zA-Z]{2,}$"
        """
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
        """
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

#-*-----------------------------------------------------------------------------------

"""
#Referencia al nodo en la base de datos
ref = db.reference("hola") #Cambia nodo principal por el nombre que se le asigna
ref_2=db.reference("Prueba con 2do nodo") ##Probando agregar nuevo nodo

#Escribir datos en tiempo real
ref.set ({
    "mensaje1": "Hola buenas",
    "activo": True
})
ref_2.set ({
    "Mensaje2": "¿Prueba exitosa?",
    "activo": True
})

#Escucha cambios en tiempo real
def escuchar_eventos(event):
    print(f"Cambio detectado: {event.data}")

ref.listen(escuchar_eventos)"""
##Se realizaron las adiciones a la base de datos 
##Intento de pull and push