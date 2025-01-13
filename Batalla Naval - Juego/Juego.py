import pygame
import sys

pygame.init()

ancho=800
alto=600
azul=(0,0,150)
gris=(100,100,100)
rojo=(200,0,0)
blanco=(255,255,255)
negro=(0,0,0)
verde=(0,190,0)


#configuracion de la ventana -------------------------------------
ventana=pygame.display.set_mode((ancho,alto))
pygame.display.set_caption("Batalla Naval - UN") #Nombre de la ventana
#Fondos---------------------++++++++++--------
fondo=pygame.image.load("Fondo 1 - 8 bits.jpg") #Ruta de acceso de la imagen
fondo2=pygame.image.load("Fondo 2 - 8 Bits.jpg")

icono=pygame.image.load("Icono.jpg")
pygame.display.set_icon(icono)


#Fuentes----------------------------------------------------------
pygame.font.init()
Fuente_titulo=pygame.font.Font(None,50) #crecion de la fuente del titulo - none fuente predeterminada- 50 tamaño
Fuente_opcion=pygame.font.Font(None,55)
Fuente_Principal=pygame.font.Font(None,65)

#funciones para dibujar el texto de la pantalla inicial y sus botones
def NombreTitulo(textoTitulo,Fuente_Principal,color,ventana,x,y):
    principalTitulo=Fuente_Principal.render(textoTitulo,True,color)
    ajuste=principalTitulo.get_rect(center=(x,y))
    ventana.blit(principalTitulo, ajuste)


def OpcionesMenu(textoOpcion,Fuente_opcion,color,colorRect,ventana,x,y,anchoo,altoo):
    botonRectangulo=pygame.Rect(x,y,anchoo,altoo)
    pygame.draw.rect(ventana,colorRect,botonRectangulo) #dibujo del rectangulo - surface es la superficie donde se realiza el dibujo
    opcion=Fuente_opcion.render(textoOpcion,True,color) #creacion del texto
    textoRectangulo=opcion.get_rect(center=botonRectangulo.center) #centrar el texto en el rectangulo
    ventana.blit(opcion, textoRectangulo)
    return botonRectangulo

#buble de la pantallla inicial
def MenuPrincipal():
    while True:
        #ventana.fill(negro) #limpia la pantalla al inicio de cada iteracion de los bubles, borra lo dibujado anteriormente
        ventana.blit(fondo,(0,0))
        NombreTitulo("BATALLA NAVAL - INTERACTIVO",Fuente_Principal,azul,ventana,ancho//2,alto//6)
        #Dibujar botones
        BotonJuego=OpcionesMenu("Jugar",Fuente_opcion,azul,blanco,ventana,ancho//2-120,alto//2-75,250,80)
        BotonSalir=OpcionesMenu("Salir",Fuente_opcion,verde,blanco,ventana,ancho//2-120,alto//2+50,250,80)
        #Eventos
        for event in pygame.event.get():
            if(event.type==pygame.QUIT):
                pygame.quit()
                sys.exit()
            if(event.type==pygame.MOUSEBUTTONDOWN): #detecta el click
                posMou=pygame.mouse.get_pos() #optener posicion mouse
                if(BotonJuego.collidepoint(posMou)):#hace click en "jugar"
                    return "jugar"
                if(BotonSalir.collidepoint(posMou)):
                    pygame.quit()
                    sys.exit()
        
    
        pygame.display.flip()

def JuegoLoop():
    mensaje="Haz click en el area roja"
   
    titulo=Fuente_titulo.render("Batalla Naval",True, azul) #renderiza el texto con suavizado
    run=True
    while run:
        #ventana.fill(negro) #limpia la pantalla al inicio de cada iteracion de los bubles, borra lo dibujado anteriormente
        ventana.blit(fondo2,(0,0))
        #Eventos-------------------------------------------------------------------------

        for evento in pygame.event.get(): #el pygame.event.get(), genera una lista de los eventos que ocurran dentro de la ventana 
            if(evento.type==pygame.QUIT): #si se cierra la ventana el progrmama lo interpreta cerrando el ciclo while
                run=False
            if(evento.type==pygame.MOUSEBUTTONDOWN): #evento del clic
                x,y=evento.pos #coordenada del clic
                if(100<=x<=300 and 100<=y<=300 ):
                    mensaje ="Clic detactado"


        #Desarrollo juego-------------------------------------------------------------

        #titulo 
        ventana.blit(titulo,(ancho//2 - titulo.get_width()//2,20)) #(texto,(Coordenada x,y))
        pygame.draw.line(ventana,gris,(30,80),(ancho-30,80),2) #(30 valor de ancho, 80 alto), el 2 es el grosor

        #dibujar rectangulo
        pygame.draw.rect(ventana,rojo,(100,100,200,200)) #(x,y,ancho,alto)

        fuente=pygame.font.Font(None,33)
        texto=fuente.render(mensaje, True, blanco)
        ventana.blit(texto,(50,50))

        pygame.display.flip() #refresca la pantalla
    pygame.quit()#Salir del juego 
    sys.exit()#Salir del juego 

#EJECUCION PRINCIPAL
while True:
    modo=MenuPrincipal()
    if(modo=="jugar"):
        JuegoLoop()




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
Letras_coordenadas="ABCDEFGHIJKLMNÑOPQRSTUVWXYZ"
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