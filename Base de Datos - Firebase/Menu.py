import firebase_admin
from firebase_admin import credentials, db

#Conectar a firebase
cred = firebase_admin.credentials.Certificate(r"C:\Users\User\Documents\Visual Studio Code - Programación\Python\Firebase\Firebase compartido - Batalla naval\bookstoreproject-8b4f0-firebase-adminsdk-2eymv-b7972991ba.json")
default_app = firebase_admin.initialize_app(cred, {
    'databaseURL':"https://bookstoreproject-8b4f0-default-rtdb.firebaseio.com/"
})

#[][][][][][][][][][]-- INICIALIZACIÓN FIREBASE --[][][][][][][][][][][][][][]

#Referencia al nodo en la base de datos
refe= db.reference("Datos_del_usuario") #Genera un nodo de informacion diferente


#Escribir datos en tiempo real
#[][][][][][][][][][]-- BORRADOR MENU --[][][][][][][][][][][][][][]

def ingresoDatos():
    userName=input("Ingrese su UserName: ")
    examen=int(input("Cuántas veces presento el examen de la Universidad Nacional:  "))


    #diccionario de datos
    data={
        "UserName":userName,
        "Intentos_examen":examen

    }
    #cargar los datos
    refe.push(data)
    print("\nLos datos han sido cargados con exito.\n")

def mostrarDatos():
    datosGuardados=refe.get() #metodo get(), trae los datos ya guardados en el nodo ref, las claves ID y los datos especificos
    if(datosGuardados):
        print("\nDatos guardados en la base de datos: ")
        for key, value in datosGuardados.items(): #el metodo get() retorna la informacion de los nodos como diccionarios, el primer valor es la ID, corresponde al subnodo. y el segundo "valor" son todos los datos dentro de ese subnodo, nombre, edad ...
            username=value.get("UserName","No hay UserName")
            intentosExamen=value.get("Intentos_examen","No hay Intento_examen")
          
            print(f" ID: {key}, UserName: {username}, Intentos: {intentosExamen}")
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

        #sobreescibir datos
        nuevosDatos={
            "UserName":nuevoNombre,
            "Intentos_examen":nuevosIntentos
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
  
        opcion=int(input("\nSelecciones la opcion que desea realizar: "))

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