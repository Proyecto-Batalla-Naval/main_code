import pygame, sys, random, time, re,requests.exceptions
import firebase_admin
from firebase_admin import credentials, db,auth

# -------------------------- Firebase -----------------------------
# Inicializar Firebase con tu certificado y URL
cred = credentials.Certificate(r"C:\Users\julia\OneDrive\Documentos\bookstoreproject-8b4f0-firebase-adminsdk-2eymv-b7972991ba (1).json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://bookstoreproject-8b4f0-default-rtdb.firebaseio.com/"
})
# Referencia a la sala de juego
sala_ref = db.reference("salas/partida1")

def guardar_datos_jugador(jugador, datos_personales, barcos_completos):
    data = {
        "datos_personales": datos_personales,
        "barcos": [],
        "disparos": []
    }
    
    for nombre_barco, info in barcos_completos.items():
        barco_firebase = {
            "nombre": nombre_barco,
            "posiciones": [[int(coord[1:])-1, ord(coord[0].upper())-65] for coord in info["posiciones"]],
            "tamaño": info["size"],
            "impactos": 0,
            "hundido": False
        }
        data["barcos"].append(barco_firebase)
    
    sala_ref.child(jugador).set(data)

def esperar_oponente():
    start_time = time.time()
    # Espera a que ambos jugadores se hayan registrado
    while True:
        if time.time() - start_time > 30:
            raise Exception("Tiempo de espera agotado. El oponente no se conectó.")
        sala = sala_ref.get()
        if sala and "jugador1" in sala and "jugador2" in sala:
            print("Ambos jugadores están listos.")
            break
        print("Esperando al otro jugador...")
        time.sleep(1)

def obtener_barcos_oponente(jugador_actual):
    oponente = "jugador2" if jugador_actual == "jugador1" else "jugador1"
    data = sala_ref.child(oponente).child("barcos").get() or []
    barcos = []
    for barco in data:
        if isinstance(barco, dict) and 'posiciones' in barco:
            # Convertir cada posición a lista de enteros
                        barcos.extend([[
                int(pos[0]) if isinstance(pos[0], str) else pos[0],
                int(pos[1]) if isinstance(pos[1], str) else pos[1]
            ] for pos in barco['posiciones']]) 
    return barcos

def registrar_disparo(jugador, coordenada):
    oponente = "jugador2" if jugador == "jugador1" else "jugador1"
    disparo = [int(coordenada[0]), int(coordenada[1])]
    
    # Registrar disparo
    sala_ref.child(jugador).child("disparos").push(disparo)
    
    # Actualizar impactos en barcos del oponente
    barcos_oponente = sala_ref.child(oponente).child("barcos").get() or []
    for idx, barco in enumerate(barcos_oponente):
        if disparo in barco['posiciones'] and not barco['hundido']:
            nuevo_impactos = barco['impactos'] + 1
            hundido = nuevo_impactos >= barco['tamaño']
            
            # Actualizar en Firebase
            sala_ref.child(oponente).child("barcos").child(str(idx)).update({
                "impactos": nuevo_impactos,
                "hundido": hundido
            })

def set_turno(turno):
    sala_ref.child("turno").set(turno)

def get_turno():
    return sala_ref.child("turno").get()

def switch_turn(jugador_actual):
    nuevo_turno = "jugador2" if jugador_actual == "jugador1" else "jugador1"
    set_turno(nuevo_turno)



# -------------------------- Configuración Pygame y Recursos -----------------------------
pygame.init()

# Dimensiones y colores
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
ANCHO_VENTANA, ALTO_VENTANA = screen.get_size()
info = pygame.display.Info()
ANCHO_PANTALLA = info.current_w    # Ejemplo: 1920 (depende de tu monitor)
ALTO_PANTALLA = info.current_h     # Ejemplo: 1080
ventana = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA), pygame.FULLSCREEN)
# Factores de escalado
BASE_WIDTH = 1920
BASE_HEIGHT = 1080
escala_x = ANCHO_PANTALLA / BASE_WIDTH
escala_y = ALTO_PANTALLA / BASE_HEIGHT

azul = (0, 0, 150)
gris = (100, 100, 100)
azulsuave=(0,90,250)
rojo = (200, 0, 0)
blanco = (255, 255, 255)
negro = (0, 0, 0)
verde = (0, 190, 0)
azul_bonito = (61, 145, 197)
azul_botones = (58, 111, 147)
COLOR_BARCO = (75, 75, 75)
COLOR_HUNDIDO = (200, 0, 0)
COLOR_AGUA = (0, 100, 200)
COLOR_FONDO = (30, 45, 60)

# Parámetros para la fase de ataque (tablero)
tam_tablero = 7
tam_celda = int(40 * min(escala_x, escala_y))  # Escala proporcional
inicioX = (ANCHO_PANTALLA - (tam_tablero * tam_celda)) // 2  # Centrado horizontal
inicioY = (ALTO_PANTALLA - (tam_tablero * tam_celda)) // 2 + int(40 * escala_y)  # Ajuste escalado

# Recursos gráficos y fuentes
def escalar_imagen(ruta_imagen, ancho, alto):
    imagen = pygame.image.load(ruta_imagen)  # Carga la imagen
    imagen_escalada = pygame.transform.scale(imagen, (ancho, alto))  # Escala la imagen
    return imagen_escalada

ventana = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))        
pygame.display.set_caption("Batalla Naval - UN")

fondo = escalar_imagen("Fondo 1 - 8 bits.jpg", 800, 600)
fondo = pygame.transform.scale(fondo, (ANCHO_VENTANA, ALTO_VENTANA))
fondo2 = escalar_imagen("Fondo 2 - 8 Bits.jpg", 800, 600)
fondo2 = pygame.transform.scale(fondo2, (ANCHO_VENTANA, ALTO_VENTANA))
icono = escalar_imagen("Icono.jpg", 32, 32)  # Tamaño original del ícono
fondoTablero = escalar_imagen("Fondo Tablero.jpg", 280, 280)
fondoEstrategia = escalar_imagen("Fondo estrategia.jpg", 800, 600)


pygame.display.set_icon(icono)

pygame.font.init()
tamaño_base = int(24 * min(escala_x, escala_y))  # Escala proporcional
Fuente_titulo = pygame.font.Font(None, int(tamaño_base * 2.0))
Fuente_opcion = pygame.font.Font(None, int(tamaño_base * 1.8))
Fuente_Principal = pygame.font.Font(None, int(tamaño_base * 2.5))
letras_Tablero = pygame.font.Font(None, int(tamaño_base * 1.5))
fuente = pygame.font.SysFont(None, 24)
# REGISTRO E IDENTIFICACION 
import pygame
import sys
import re
import requests  # Se usa en manejar_errores

def run_sistema_juego():
    # Inicialización de fuentes con escala proporcional
    pygame.font.init()
    # Se asume escala_x y escala_y; si se requiere, se pueden parametrizar.
    escala_x, escala_y = 1, 1  
    tamaño_base = int(24 * min(escala_x, escala_y))
    Fuente_titulo    = pygame.font.Font(None, int(tamaño_base * 2.0))
    Fuente_opcion    = pygame.font.Font(None, int(tamaño_base * 1.8))
    Fuente_Principal = pygame.font.Font(None, int(tamaño_base * 2.5))
    letras_Tablero   = pygame.font.Font(None, int(tamaño_base * 1.5))
    fuente           = pygame.font.SysFont(None, 24)
    
    # Inicialización de Pygame y creación de la ventana
    pygame.init()
    info = pygame.display.Info()
    ANCHO_PANTALLA, ALTO_PANTALLA = info.current_w, info.current_h
    ventana = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA), pygame.FULLSCREEN)
    pygame.display.set_caption("Sistema de Juego")
    
    # Definición de colores
    blanco      = (255, 255, 255)
    azul        = (0, 102, 204)
    azulsuave   = (173, 216, 230)
    negro       = (0, 0, 0)
    rojo        = (255, 0, 0)
    inactivo    = (200, 200, 200)
    cerrar      = (200, 50, 50)
    cerrar_hover = (230, 70, 70)
    
    # Funciones internas
    def dibujar_boton_cerrar(hover=False):
        tam = 30
        margen = 10
        rect = pygame.Rect(ANCHO_PANTALLA - tam - margen, margen, tam, tam)
        color = cerrar_hover if hover else cerrar
        pygame.draw.line(ventana, color, (rect.left + 8, rect.top + 8), (rect.right - 8, rect.bottom - 8), 3)
        pygame.draw.line(ventana, color, (rect.right - 8, rect.top + 8), (rect.left + 8, rect.bottom - 8), 3)
        return rect

    def dibujar_texto(texto, y, fuente_local=Fuente_opcion, color=negro):
        texto_surface = fuente_local.render(texto, True, color)
        rect = texto_surface.get_rect(center=(ANCHO_PANTALLA // 2, y))
        ventana.blit(texto_surface, rect)

    def dibujar_boton(y, texto, activo=True, ancho=None, alto=None):
        ancho = ancho or ANCHO_PANTALLA // 3.5
        alto = alto or ALTO_PANTALLA // 12
        color = azul if activo else inactivo
        rect = pygame.Rect(0, y, ancho, alto)
        rect.centerx = ANCHO_PANTALLA // 2
        pygame.draw.rect(ventana, color, rect, border_radius=15)
        dibujar_texto(texto, rect.centery, Fuente_opcion, blanco)
        return rect, activo

    def validar_password(password):
        errores = []
        if len(password) < 6 or len(password) > 10:
            errores.append("Debe tener entre 6-10 caracteres")
        if not re.search(r'[A-Z]', password):
            errores.append("Al menos 1 mayúscula")
        if not re.search(r'[!@#$%^&*()]', password):
            errores.append("Al menos 1 carácter especial")
        return errores

    def validar_username(username):
        if len(username) < 3:
            return "Mínimo 3 caracteres"
        if not re.match(r'^[\wñáéíóú]+$', username):
            return "Solo letras, números y _"
        return None

    def menu_principal():
        while True:
            ventana.fill(blanco)
            mouse_pos = pygame.mouse.get_pos()
            btn_cerrar = dibujar_boton_cerrar()
            if btn_cerrar.collidepoint(mouse_pos):
                dibujar_boton_cerrar(hover=True)
            
            dibujar_texto("Menú Principal", ALTO_PANTALLA // 5, Fuente_Principal, azul)
            boton_login = dibujar_boton(ALTO_PANTALLA // 2 - ALTO_PANTALLA // 8, "ACCEDER")[0]
            boton_registro = dibujar_boton(ALTO_PANTALLA // 2 + ALTO_PANTALLA // 16, "REGISTRARSE")[0]
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if btn_cerrar.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()
                    elif boton_login.collidepoint(event.pos):
                        formulario_login()
                    elif boton_registro.collidepoint(event.pos):
                        formulario_registro()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            pygame.display.update()

    def formulario_login():
        campos = ["", ""]
        campo_activo = None
        error_msg = ""
        
        while True:
            ventana.fill(blanco)
            mouse_pos = pygame.mouse.get_pos()
            btn_cerrar = dibujar_boton_cerrar()
            if btn_cerrar.collidepoint(mouse_pos):
                dibujar_boton_cerrar(hover=True)
            
            dibujar_texto("Inicio de Sesión", ALTO_PANTALLA // 6, Fuente_Principal, azul)
            campos_rect = [
                pygame.Rect(ANCHO_PANTALLA // 4, ALTO_PANTALLA // 3, ANCHO_PANTALLA // 2, ALTO_PANTALLA // 15),
                pygame.Rect(ANCHO_PANTALLA // 4, ALTO_PANTALLA // 3 + ALTO_PANTALLA // 8, ANCHO_PANTALLA // 2, ALTO_PANTALLA // 15)
            ]
            
            for i, rect in enumerate(campos_rect):
                color = azul if i == campo_activo else azulsuave
                pygame.draw.rect(ventana, color, rect, 2, border_radius=10)
                texto = campos[0] if i == 0 else "*" * len(campos[1])
                dibujar_texto(texto, rect.centery, Fuente_opcion, negro)
            
            dibujar_texto("Correo electrónico:", campos_rect[0].top - ALTO_PANTALLA // 30, Fuente_opcion)
            dibujar_texto("Contraseña:", campos_rect[1].top - ALTO_PANTALLA // 30, Fuente_opcion)
            btn_volver = dibujar_boton(ALTO_PANTALLA - ALTO_PANTALLA // 5, "Volver", ancho=ANCHO_PANTALLA // 4)[0]
            btn_siguiente, btn_activo = dibujar_boton(ALTO_PANTALLA - ALTO_PANTALLA // 3.5, "Siguiente", all(campos), ancho=ANCHO_PANTALLA // 4)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if btn_cerrar.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()
                    elif btn_volver.collidepoint(event.pos):
                        menu_principal()
                    elif btn_siguiente.collidepoint(event.pos) and btn_activo:
                        try:
                            user = auth.get_user_by_email(campos[0])
                            ref = db.reference(f"usuarios/{user.uid}")
                            datos = ref.get()
                            if datos and datos["password"] == campos[1]:
                                pantalla_juego(datos["username"])
                            else:
                                error_msg = "Credenciales incorrectas"
                        except Exception as e:
                            error_msg = manejar_errores(e)
                    else:
                        campo_activo = next((i for i, r in enumerate(campos_rect) if r.collidepoint(event.pos)), None)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        menu_principal()
                    elif campo_activo is not None:
                        campos[campo_activo] = campos[campo_activo][:-1] if event.key == pygame.K_BACKSPACE else campos[campo_activo] + event.unicode
                        btn_activo = all(campos)
            
            if error_msg:
                dibujar_texto(error_msg, ALTO_PANTALLA - ALTO_PANTALLA // 7, color=rojo)
            pygame.display.update()

    def formulario_registro():
        campos = ["", "", ""]
        campo_activo = None
        error_msg = ""
        submitted = False
        start_y = ALTO_PANTALLA // 6
        espacio_vertical = ALTO_PANTALLA // 5
        espacio_extra = ALTO_PANTALLA // 10
        
        posiciones = [
            start_y,  # Correo
            start_y + espacio_vertical,  # Contraseña
            start_y + espacio_vertical + espacio_vertical + espacio_extra  # Usuario
        ]
        
        while True:
            ventana.fill(blanco)
            mouse_pos = pygame.mouse.get_pos()
            btn_cerrar = dibujar_boton_cerrar()
            if btn_cerrar.collidepoint(mouse_pos):
                dibujar_boton_cerrar(hover=True)
            
            dibujar_texto("Registro de Usuario", ALTO_PANTALLA // 10, Fuente_Principal, azul)
            
            for i, pos_y in enumerate(posiciones):
                rect = pygame.Rect(ANCHO_PANTALLA // 4, pos_y, ANCHO_PANTALLA // 2, ALTO_PANTALLA // 12)
                color = azul if i == campo_activo else azulsuave
                pygame.draw.rect(ventana, color, rect, 2, border_radius=10)
                texto = campos[i] if i != 1 else "*" * len(campos[i])
                dibujar_texto(texto, rect.centery, Fuente_opcion, negro)
                
                label_y = rect.top - ALTO_PANTALLA // 25
                dibujar_texto(["Correo:", "Contraseña:", "Usuario:"][i], label_y, Fuente_opcion)
                
                if i == 1:
                    ayudas = [
                        "Mínimo 6-10 caracteres",
                        "Al menos 1 mayúscula",
                        "Al menos 1 símbolo (!@#$%^&*())"
                    ]
                    y_ayuda = rect.bottom + 10
                    for ayuda in ayudas:
                        dibujar_texto(ayuda, y_ayuda, Fuente_opcion, negro)
                        y_ayuda += 25
                    
                    if submitted:
                        errores = validar_password(campos[1])
                        if errores:
                            y_error = y_ayuda + 10
                            for error in errores:
                                dibujar_texto(error, y_error, Fuente_opcion, rojo)
                                y_error += 25
                
                elif i == 2:
                    ayuda_y = rect.bottom + 10
                    dibujar_texto("Solo letras, números y _", ayuda_y, Fuente_opcion, negro)
                    
                    if submitted:
                        error = validar_username(campos[2])
                        if error:
                            dibujar_texto(error, ayuda_y + 30, Fuente_opcion, rojo)
            
            btn_volver_y = posiciones[-1] + espacio_vertical
            btn_siguiente_y = btn_volver_y + ALTO_PANTALLA // 10
            
            valido = all(campos) and not validar_password(campos[1]) and validar_username(campos[2]) is None
            btn_volver = dibujar_boton(btn_volver_y, "Volver", ancho=ANCHO_PANTALLA // 4)[0]
            btn_siguiente = dibujar_boton(btn_siguiente_y, "Siguiente", valido, ancho=ANCHO_PANTALLA // 4)[0]
            
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if btn_cerrar.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()
                    elif btn_volver.collidepoint(event.pos):
                        menu_principal()
                    elif btn_siguiente.collidepoint(event.pos):
                        if valido:
                            try:
                                ref = db.reference("usuarios")
                                if ref.order_by_child("username").equal_to(campos[2]).get():
                                    error_msg = "Usuario ya existe"
                                    continue
                                user = auth.create_user(email=campos[0], password=campos[1])
                                ref.child(user.uid).set({"email": campos[0], "username": campos[2], "password": campos[1]})
                                pantalla_juego(campos[2])
                            except Exception as e:
                                error_msg = manejar_errores(e)
                        else:
                            submitted = True
                    else:
                        campo_activo = next((i for i, pos in enumerate(posiciones)
                                              if pygame.Rect(ANCHO_PANTALLA // 4, pos, ANCHO_PANTALLA // 2, ALTO_PANTALLA // 12)
                                              .collidepoint(event.pos)), None)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        menu_principal()
                    elif campo_activo is not None:
                        campos[campo_activo] = (campos[campo_activo][:-1]
                                                 if event.key == pygame.K_BACKSPACE
                                                 else campos[campo_activo] + event.unicode)
                        error_msg = ""
            
            if error_msg:
                dibujar_texto(error_msg, btn_siguiente_y + ALTO_PANTALLA // 15, color=rojo)
            pygame.display.update()

    def pantalla_juego(username):
        while True:
            ventana.fill(blanco)
            mouse_pos = pygame.mouse.get_pos()
            btn_cerrar = dibujar_boton_cerrar()
            if btn_cerrar.collidepoint(mouse_pos):
                dibujar_boton_cerrar(hover=True)
            
            dibujar_texto(f"¡Bienvenido, {username}!", ALTO_PANTALLA // 4, Fuente_Principal, azul)
            btn_volver = dibujar_boton(ALTO_PANTALLA - ALTO_PANTALLA // 5, "Volver al Menú", ancho=ANCHO_PANTALLA // 3)[0]
            
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if btn_cerrar.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()
                    elif btn_volver.collidepoint(event.pos):
                        menu_principal()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    menu_principal()
            pygame.display.update()

    def manejar_errores(e):
        if isinstance(e, requests.exceptions.ConnectionError):
            return "Error de conexión"
        elif isinstance(e, auth.UserNotFoundError):
            return "Usuario no registrado"
        elif isinstance(e, ValueError) and any(kw in str(e).lower() for kw in ['invalid', 'mail']):
            return "Correo inválido"
        elif 'email' in str(e).lower():
            return "Correo ya registrado"
        else:
            return f"Error: {str(e)}"

    # Inicia el menú principal
    menu_principal()

if __name__ == "__main__":
    run_sistema_juego()



# -------------------------- Funciones de Menú e Interfaz -----------------------------
def NombreTitulo(textoTitulo, fuenteTitulo, color, ventana, x, y):
    principalTitulo = fuenteTitulo.render(textoTitulo, True, color)
    ajuste = principalTitulo.get_rect(center=(x, y))
    ventana.blit(principalTitulo, ajuste)
def OpcionesMenu(textoOpcion, fuenteOpcion, color, colorRect, ventana, x, y, anchoo, altoo):
    botonRect = pygame.Rect(x, y, anchoo, altoo)
    pygame.draw.rect(ventana, colorRect, botonRect)
    opcion = fuenteOpcion.render(textoOpcion, True, color)
    txtRect = opcion.get_rect(center=botonRect.center)
    ventana.blit(opcion, txtRect)
    return botonRect

def MenuPrincipal():
    while True:
        ventana.blit(fondo, (0, 0))
        NombreTitulo("BATALLA NAVAL - INTERACTIVO", Fuente_Principal, azul, ventana, ANCHO_PANTALLA//2, ALTO_PANTALLA//6)
        BotonJuego = OpcionesMenu("Jugar", Fuente_opcion, azul, blanco, ventana, ANCHO_PANTALLA//2-120, ALTO_PANTALLA//2-75, 250, 80)
        BotonSalir = OpcionesMenu("Salir", Fuente_opcion, verde, blanco, ventana, ANCHO_PANTALLA//2-120, ALTO_PANTALLA//2+50, 250, 80)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                posMou = pygame.mouse.get_pos()
                if BotonJuego.collidepoint(posMou):
                    return "jugar"
                if BotonSalir.collidepoint(posMou):
                    pygame.quit()
                    sys.exit()
        pygame.display.flip()
        boton_cerrar = pygame.Rect(
            ANCHO_PANTALLA - int(50 * escala_x),
            int(20 * escala_y),
            int(40 * escala_x),
            int(40 * escala_y)
        )
        pygame.draw.rect(ventana, rojo, boton_cerrar, border_radius=20)
        # Dibujar "X"
        pygame.draw.line(ventana, blanco, 
                        (boton_cerrar.x + 10 * escala_x, boton_cerrar.y + 10 * escala_y),
                        (boton_cerrar.x + 30 * escala_x, boton_cerrar.y + 30 * escala_y), 
                        int(4 * escala_x))
        pygame.draw.line(ventana, blanco, 
                        (boton_cerrar.x + 30 * escala_x, boton_cerrar.y + 10 * escala_y),
                        (boton_cerrar.x + 10 * escala_x, boton_cerrar.y + 30 * escala_y), 
                        int(4 * escala_x))
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if BotonJuego.collidepoint(pos):
                    return "jugar"
                elif BotonSalir.collidepoint(pos) or boton_cerrar.collidepoint(pos):
                    confirmar_salida()
        
        pygame.display.flip()
def confirmar_salida():
    # Fondo semitransparente
    overlay = pygame.Surface((ANCHO_PANTALLA, ALTO_PANTALLA))
    overlay.set_alpha(150)
    overlay.fill(negro)
    ventana.blit(overlay, (0, 0))
    
    # Cuadro de diálogo
    cuadro_ancho = int(600 * escala_x)
    cuadro_alto = int(300 * escala_y)
    cuadro = pygame.Rect(
        (ANCHO_PANTALLA - cuadro_ancho) // 2,
        (ALTO_PANTALLA - cuadro_alto) // 2,
        cuadro_ancho,
        cuadro_alto
    )
    pygame.draw.rect(ventana, gris, cuadro, border_radius=15)
    
    # Texto
    texto = Fuente_titulo.render("¿Salir del juego?", True, blanco)
    ventana.blit(texto, texto.get_rect(center=(cuadro.centerx, cuadro.top + 50 * escala_y)))
    
    # Botones
    boton_si = pygame.Rect(
        cuadro.centerx - 150 * escala_x,
        cuadro.centery + 50 * escala_y,
        120 * escala_x,
        60 * escala_y
    )
    boton_no = pygame.Rect(
        cuadro.centerx + 30 * escala_x,
        cuadro.centery + 50 * escala_y,
        120 * escala_x,
        60 * escala_y
    )
    
    pygame.draw.rect(ventana, rojo, boton_si, border_radius=10)
    pygame.draw.rect(ventana, verde, boton_no, border_radius=10)
    
    texto_si = Fuente_opcion.render("SÍ", True, blanco)
    texto_no = Fuente_opcion.render("NO", True, blanco)
    ventana.blit(texto_si, texto_si.get_rect(center=boton_si.center))
    ventana.blit(texto_no, texto_no.get_rect(center=boton_no.center))
    
    pygame.display.flip()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if boton_si.collidepoint(pos):
                    pygame.quit()
                    sys.exit()
                elif boton_no.collidepoint(pos):
                    return
# -------------------------- PANEL DE ESTRATEGIA (COLOCACIÓN DE BARCOS) -----------------------------

# Parámetros y variables para el panel
GRID_SIZE = 7
# Para el panel, usaremos celdas de 40 píxeles y una grilla ubicada en (ORIGEN_GRID_X, ORIGEN_GRID_Y)
ORIGEN_GRID_X = (ANCHO_PANTALLA - (GRID_SIZE * tam_celda)) // 2
ORIGEN_GRID_Y = (ALTO_PANTALLA - (GRID_SIZE * tam_celda)) // 2

# Lista de tamaños (puedes ajustar la cantidad y tamaños; aquí usamos 6 barcos)
TAMAÑOS_BARCOS = [4, 3, 3, 2, 2, 1]
barcos = []   # Lista de barcos (cada uno es un diccionario)
grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]  # 0 = libre, 1 = ocupado

# Botones escalados y posicionados en la parte inferior
boton_vertical = pygame.Rect(50, ALTO_VENTANA - 80, 120, 40)
boton_limpiar = pygame.Rect(200, ALTO_VENTANA - 80, 120, 40)
boton_aleatorio = pygame.Rect(350,ALTO_VENTANA - 80, 120, 40)
boton_inicio = pygame.Rect(500, ALTO_VENTANA - 80, 120, 40)
# Variable para indicar si se inició el juego (después de colocar barcos) y almacenar posiciones
juego_iniciado = False
posiciones_barcos = {}
def inicializar_barcos():
    global barcos
    barcos.clear()
    x_inicial = 50
    y_inicial = 100
    separacion = 60
    for i, size in enumerate(TAMAÑOS_BARCOS):
        default_x = x_inicial
        default_y = y_inicial + i * separacion
        barco = {
            'size': size,
            'vertical': False,
            'on_board': False,
            'board_col': -1,
            'board_row': -1,
            'x': default_x,
            'y': default_y,
            'default_x': default_x,
            'default_y': default_y,
            'dragging': False,
            'selected': False,
            'offset_x': 0,
            'offset_y': 0
        }
        barcos.append(barco)

def limpiar_grid():
    for i in range(GRID_SIZE):
        grid[i] = [0] * GRID_SIZE

def ocupar_celdas_en_grid(barco):
    col = barco['board_col']
    row = barco['board_row']
    size = barco['size']
    vertical = barco['vertical']
    for i in range(size):
        if vertical:
            grid[row+i][col] = 1
        else:
            grid[row][col+i] = 1

def liberar_celdas_en_grid(barco):
    col = barco['board_col']
    row = barco['board_row']
    size = barco['size']
    vertical = barco['vertical']
    for i in range(size):
        if vertical:
            grid[row+i][col] = 0
        else:
            grid[row][col+i] = 0

def forzar_vertical():
    for b in barcos:
        if b['selected']:
            nueva_orientacion = not b['vertical']
            if b['on_board']:
                col, row = b['board_col'], b['board_row']
                quitar_barco_de_grilla(b)
                if puede_colocar(b, col, row, nueva_orientacion):
                    b['vertical'] = nueva_orientacion
                    colocar_barco_en_grilla(b, col, row)
                else:
                    reiniciar_barco_fuera(b)
            else:
                b['vertical'] = nueva_orientacion
            break

def resetear_barcos():
    for b in barcos:
        b['on_board'] = False
        b['board_col'] = -1
        b['board_row'] = -1
        b['x'] = b['default_x']
        b['y'] = b['default_y']
        b['vertical'] = False
        b['selected'] = False
        b['dragging'] = False
    limpiar_grid()

def dentro_limites(col, fila, size, vertical):
    if vertical:
        return 0 <= fila and fila + size <= GRID_SIZE and 0 <= col < GRID_SIZE
    else:
        return 0 <= col and col + size <= GRID_SIZE and 0 <= fila < GRID_SIZE

def puede_colocar(barco, col, fila, vertical):
    size = barco['size']
    if not dentro_limites(col, fila, size, vertical):
        return False
    for i in range(size):
        r = fila + i if vertical else fila
        c = col if vertical else col + i
        if grid[r][c] == 1:
            return False
    return True
def colocar_barco_en_grilla(barco, col, fila):
    barco['on_board'] = True
    barco['board_col'] = col
    barco['board_row'] = fila
    ocupar_celdas_en_grid(barco)

def quitar_barco_de_grilla(barco):
    if barco['on_board']:
        liberar_celdas_en_grid(barco)
        barco['on_board'] = False
        barco['board_col'] = -1
        barco['board_row'] = -1

def puede_colocar_estricto(barco, col, fila, vertical):
    size = barco['size']
    if not dentro_limites(col, fila, size, vertical):
        return False
    for i in range(size):
        r = fila + i if vertical else fila
        c = col if vertical else col + i
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                nr = r + dr
                nc = c + dc
                if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
                    if grid[nr][nc] == 1:
                        return False
    return True

def reiniciar_barco_fuera(barco):
    barco['on_board'] = False
    barco['board_col'] = -1
    barco['board_row'] = -1
    barco['x'] = barco['default_x']
    barco['y'] = barco['default_y']
    barco['vertical'] = False
    barco['selected'] = False
    barco['dragging'] = False

def randomizar_barcos():
    limpiar_grid()
    for barco in barcos:
        placed = False
        attempts = 0
        while not placed and attempts < 10000:
            attempts += 1
            orientacion = random.choice([True, False])
            barco['vertical'] = orientacion
            if orientacion:
                max_row = GRID_SIZE - barco['size']
                max_col = GRID_SIZE - 1
            else:
                max_row = GRID_SIZE - 1
                max_col = GRID_SIZE - barco['size']
            col = random.randint(0, max_col)
            fila = random.randint(0, max_row)
            if puede_colocar_estricto(barco, col, fila, orientacion):
                barco['board_col'] = col
                barco['board_row'] = fila
                colocar_barco_en_grilla(barco, col, fila)
                barco['x'] = ORIGEN_GRID_X + col * tam_celda
                barco['y'] = ORIGEN_GRID_Y + fila * tam_celda
                placed = True
        if not placed:
            reiniciar_barco_fuera(barco)

def iniciar_juego():
    global juego_iniciado, posiciones_barcos
    if all(b['on_board'] for b in barcos):
        posiciones_barcos = {}
        columnas = ['A','B','C','D','E','F','G']
        for idx, b in enumerate(barcos):
            pos_list = []
            col = b['board_col']
            row = b['board_row']
            size = b['size']
            if b['vertical']:
                for i in range(size):
                    pos_list.append(f"{columnas[col]}{row+i+1}")
            else:
                for i in range(size):
                    pos_list.append(f"{columnas[col+i]}{row+1}")
            posiciones_barcos[f"barco_{idx+1}"] = {
                "size": size,
                "orientacion": "vertical" if b['vertical'] else "horizontal",
                "posiciones": pos_list
            }
        print("Posiciones de los barcos:", posiciones_barcos)
        juego_iniciado = True

def barco_en_punto(x, y):
    for barco in reversed(barcos):
        size = barco['size']
        vertical = barco['vertical']
        if barco['on_board']:
            px = ORIGEN_GRID_X + barco['board_col'] * tam_celda
            py = ORIGEN_GRID_Y + barco['board_row'] * tam_celda
        else:
            px = barco['x']
            py = barco['y']
        if vertical:
            w = tam_celda
            h = tam_celda * size
        else:
            w = tam_celda * size
            h = tam_celda
        rect_barco = pygame.Rect(px, py, w, h)
        if rect_barco.collidepoint(x, y):
            return barco
    return None

def dibujar_grilla_panel(superficie):
    # Dibuja la grilla de colocación (en el panel de estrategia)
    for fila in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            x = ORIGEN_GRID_X + col * tam_celda
            y = ORIGEN_GRID_Y + fila * tam_celda
            rect = pygame.Rect(x, y, tam_celda, tam_celda)
            pygame.draw.rect(superficie, negro, rect, 1)
    # Dibujar encabezados (A, B, C, ... y 1, 2, 3, ...)
    columnas = ['A','B','C','D','E','F','G'][:GRID_SIZE]
    for col in range(GRID_SIZE):
        x = ORIGEN_GRID_X + col * tam_celda + tam_celda//2
        y = ORIGEN_GRID_Y - 20
        txt = fuente.render(columnas[col], True, rojo)
        txt_rect = txt.get_rect(center=(x, y))
        superficie.blit(txt, txt_rect)
    for fila in range(GRID_SIZE):
        x = ORIGEN_GRID_X - 20
        y = ORIGEN_GRID_Y + fila * tam_celda + tam_celda//2
        txt = fuente.render(str(fila+1), True, rojo)
        txt_rect = txt.get_rect(center=(x, y))
        superficie.blit(txt, txt_rect)

def dibujar_grid_tablero(x, y, tam_celda, grid_size):
    # Líneas verticales
    for i in range(grid_size + 1):
        inicio_x = x + i * tam_celda
        pygame.draw.line(ventana, negro, 
                        (inicio_x, y), 
                        (inicio_x, y + grid_size * tam_celda), 
                        2)
    
    # Líneas horizontales
    for j in range(grid_size + 1):
        inicio_y = y + j * tam_celda
        pygame.draw.line(ventana, negro, 
                        (x, inicio_y), 
                        (x + grid_size * tam_celda, inicio_y), 
                        2)

def dibujar_barcos_panel(superficie):
    for barco in barcos:
        size = barco['size']
        vertical = barco['vertical']
        selected = barco['selected']
        if barco['on_board']:
            px = ORIGEN_GRID_X + barco['board_col'] * tam_celda
            py = ORIGEN_GRID_Y + barco['board_row'] * tam_celda
        else:
            px = barco['x']
            py = barco['y']
        if vertical:
            w = tam_celda
            h = tam_celda * size
        else:
            w = tam_celda * size
            h = tam_celda
        color = gris if selected else COLOR_BARCO
        rect = pygame.Rect(px, py, w, h)
        pygame.draw.rect(superficie, color, rect)
        pygame.draw.rect(superficie, azul_bonito, rect, 2)

def dibujar_botones_panel(superficie):
    botones = [
        (boton_vertical, "Rotar", (10, 10)),
        (boton_limpiar, "Limpiar", (5, 10)),
        (boton_aleatorio, "Aleatorio", (5, 10))
    ]
    for rect, text, offset in botones:
        pygame.draw.rect(superficie, azul_botones, rect)
        txt = fuente.render(text, True, negro)
        superficie.blit(txt, (rect.x + offset[0], rect.y + offset[1]))
    if all(b['on_board'] for b in barcos):
        pygame.draw.rect(superficie, azul_bonito, boton_inicio)
        txt = fuente.render("Inicio", True, blanco)
        superficie.blit(txt, (boton_inicio.x + 10, boton_inicio.y + 10))

def manejar_mousebuttondown_panel(event):
    x, y = event.pos
    if event.button == 1:
        if boton_vertical.collidepoint(x, y):
            forzar_vertical()
            return
        if boton_limpiar.collidepoint(x, y):
            resetear_barcos()
            return
        if boton_aleatorio.collidepoint(x, y):
            randomizar_barcos()
            return
        if boton_inicio.collidepoint(x, y):
            iniciar_juego()
            return
        barco = barco_en_punto(x, y)
        if barco:
            for b in barcos:
                b['selected'] = False
            barco['selected'] = True
            barco['dragging'] = True
            if barco['on_board']:
                quitar_barco_de_grilla(barco)
                barco['x'] = x
                barco['y'] = y
            barco['offset_x'] = x - barco['x']
            barco['offset_y'] = y - barco['y']
        else:
            for b in barcos:
                b['selected'] = False
    elif event.button == 3:
        for b in barcos:
            if b['selected']:
                nueva_orientacion = not b['vertical']
                if not b['on_board']:
                    b['vertical'] = nueva_orientacion
                else:
                    col = b['board_col']
                    row = b['board_row']
                    quitar_barco_de_grilla(b)
                    if puede_colocar(b, col, row, nueva_orientacion):
                        b['vertical'] = nueva_orientacion
                        colocar_barco_en_grilla(b, col, row)
                    else:
                        reiniciar_barco_fuera(b)
                break

def manejar_mousemotion_panel(event):
    x, y = event.pos
    for b in barcos:
        if b['dragging']:
            b['x'] = x - b['offset_x']
            b['y'] = y - b['offset_y']

def manejar_mousebuttonup_panel(event):
    x, y = event.pos
    if event.button == 1:
        for b in barcos:
            if b['dragging']:
                b['dragging'] = False
                col = (x - ORIGEN_GRID_X) // tam_celda
                fila = (y - ORIGEN_GRID_Y) // tam_celda
                if 0 <= col < GRID_SIZE and 0 <= fila < GRID_SIZE:
                    if puede_colocar_estricto(b, col, fila, b['vertical']):
                        colocar_barco_en_grilla(b, col, fila)
                    else:
                        reiniciar_barco_fuera(b)
                else:
                    reiniciar_barco_fuera(b)

# -------------------------- FASE DE ATAQUE (con Firebase) -----------------------------
def dibujar_coordenadas_tablero(x, y, tam_celda, grid_size):
    # Letras (columnas)
    letras = "ABCDEFG"
    for i in range(grid_size):
        texto = letras[i]
        render = letras_Tablero.render(texto, True, negro)
        offset_y = 30 * escala_y  # Escalar desplazamiento
        ventana.blit(render, (x + i*tam_celda + tam_celda//2 - render.get_width()//2, y - offset_y))
    # Números (filas)
    for i in range(grid_size):
        texto = str(i+1)
        render = letras_Tablero.render(texto, True, negro)
        ventana.blit(render, (x - 30, y + i*tam_celda + tam_celda//2 - render.get_height()//2))


def dibujar_impacto(x, y, es_impacto):
    rect = pygame.Rect(x, y, tam_celda, tam_celda)
    if es_impacto:
        pygame.draw.line(ventana, COLOR_HUNDIDO, rect.topleft, rect.bottomright, 3)
        pygame.draw.line(ventana, COLOR_HUNDIDO, rect.bottomleft, rect.topright, 3)
    else:
        pygame.draw.circle(ventana, COLOR_AGUA, rect.center, 15)


def coord_str_to_indices(coord):
    # Si la coordenada ya es una lista [fila, col], devolver directamente
    if isinstance(coord, list) and len(coord) == 2:
        return coord[0], coord[1]
    
    # Si es string tipo "A1"
    columnas = "ABCDEFG"
    col_letter = coord[0].upper()
    row = int(coord[1:]) - 1
    col = columnas.index(col_letter)
    return row, col
def dibujar_tablero_defensa(x, y, barcos_propios, disparos_oponente):
    ventana.blit(fondoTablero, (x, y))
    dibujar_grid_tablero(x, y, tam_celda, GRID_SIZE)  
    dibujar_coordenadas_tablero(x, y, tam_celda, GRID_SIZE)
    
    # Dibujar barcos (ya vienen en formato numérico desde Firebase)
    for coord in barcos_propios:
        row, col = coord_str_to_indices(coord)
        rect = pygame.Rect(x + col * tam_celda, y + row * tam_celda, tam_celda, tam_celda)
        pygame.draw.rect(ventana, COLOR_BARCO, rect.inflate(-4, -4))
    
    # Dibujar disparos recibidos
    for d in disparos_oponente:
        if len(d) == 2:
            fila, col = d
            pos_x = x + col * tam_celda
            pos_y = y + fila * tam_celda
            pygame.draw.circle(ventana, COLOR_AGUA, (pos_x + tam_celda//2, pos_y + tam_celda//2), 15)

def dibujar_tablero_ataque(x, y, barcos_oponente, disparos_jugador):
    ventana.blit(fondoTablero, (x, y))
    dibujar_grid_tablero(x, y, tam_celda, GRID_SIZE)
    dibujar_coordenadas_tablero(x, y, tam_celda, GRID_SIZE)
    
    # Procesar todos los disparos
    for d in disparos_jugador:
        if len(d) == 2:
            fila, col = map(int, d)
            pos_x = x + col * tam_celda
            pos_y = y + fila * tam_celda
            
            # Verificar impacto y hundimiento
            impacto = False
            hundido = False
            for barco in barcos_oponente:
                if [fila, col] in barco.get('posiciones', []):
                    impacto = True
                    if barco.get('hundido', False):
                        hundido = True
                    break
            
            if hundido:
                pygame.draw.rect(ventana, COLOR_HUNDIDO, (pos_x, pos_y, tam_celda, tam_celda))
            elif impacto:
                pygame.draw.circle(ventana, rojo, (pos_x + tam_celda//2, pos_y + tam_celda//2), 15)
            else:
                pygame.draw.circle(ventana, COLOR_AGUA, (pos_x + tam_celda//2, pos_y + tam_celda//2), 15)



def mostrar_mensaje_hundido(barcos_oponente):
    mensajes = []
    for barco in barcos_oponente:
        if barco.get('hundido', False):
            nombre = barco.get('nombre', 'Barco desconocido')
            tamaño = barco.get('tamaño', 0)
            mensajes.append(f"¡Hundiste {nombre} ({tamaño} cañones)!")
    
    # Posicionamiento mejorado
    y_pos = 50  # Bajar un poco desde el título
    for msg in mensajes[-1:]:  # Mostrar últimos 1 mensajes
        texto = Fuente_opcion.render(msg, True, rojo)
        fondo_msg = pygame.Surface((texto.get_width() + 20, texto.get_height() + 10))
        fondo_msg.set_alpha(150)  # Transparencia
        fondo_msg.fill(negro)
        ventana.blit(fondo_msg, (ANCHO_VENTANA//2 - texto.get_width()//2 - 10, y_pos - 5))
        ventana.blit(texto, (ANCHO_VENTANA//2 - texto.get_width()//2, y_pos))
        y_pos += 40


#------------------------------------
def JuegoAtaque(jugador_actual):
    clock = pygame.time.Clock()
    run = True
    mensaje = ""
    mensaje_tiempo = 0

    # Coordenadas de los tableros en la fase de ataque
    inicioX_defensa = 50
    inicioX_ataque = ANCHO_VENTANA//2 + 50
    inicioY_tableros = 180

    while run:
        ventana.blit(fondo2, (0, 0))
        turno_actual = get_turno()
        oponente = "jugador2" if jugador_actual == "jugador1" else "jugador1"
        barcos_oponente = sala_ref.child(oponente).child("barcos").get() or []
        
        # Obtener datos desde Firebase
        disparos_jugador_data = sala_ref.child(jugador_actual).child("disparos").get()
        disparos_jugador = list(disparos_jugador_data.values()) if disparos_jugador_data else []
        disparos_oponente_data = sala_ref.child(oponente).child("disparos").get()
        disparos_oponente = list(disparos_oponente_data.values()) if disparos_oponente_data else []
        
        # Obtener posiciones de barcos (convertidos a listas) de ambos jugadores
        barcos_oponente = sala_ref.child(oponente).child("barcos").get() or []


        mis_barcos_data = sala_ref.child(jugador_actual).child("barcos").get() or []
        mis_barcos = []
        for barco in mis_barcos_data:
            if isinstance(barco, dict) and 'posiciones' in barco:
                mis_barcos.extend(barco['posiciones'])
        
        # Dibujar interfaz de ataque
        titulo = Fuente_titulo.render("Fase de Ataque", True, azul)
        ventana.blit(titulo, (ANCHO_VENTANA//2 - titulo.get_width()//2, 20))
        dibujar_tablero_defensa(inicioX_defensa, inicioY_tableros, mis_barcos, disparos_oponente)
        dibujar_tablero_ataque(inicioX_ataque, inicioY_tableros, barcos_oponente, disparos_jugador)        
        
        texto_defensa = Fuente_opcion.render("Tu Tablero", True, azul)
        texto_ataque = Fuente_opcion.render("Tablero Enemigo", True, rojo)
        ventana.blit(texto_defensa, (inicioX_defensa + 50, inicioY_tableros - 80))
        ventana.blit(texto_ataque, (inicioX_ataque , inicioY_tableros - 80))

        mostrar_mensaje_hundido(barcos_oponente)
        
        
        if time.time() - mensaje_tiempo < 2:
            mensaje_texto = Fuente_opcion.render(mensaje, True, rojo)
            ventana.blit(mensaje_texto, (ANCHO_VENTANA//2 - mensaje_texto.get_width()//2, ALTO_VENTANA - 100))
        
        texto_turno = Fuente_opcion.render("Tu turno" if turno_actual == jugador_actual else "Turno del oponente",
                                            True, verde if turno_actual == jugador_actual else rojo)
        ventana.blit(texto_turno, (ANCHO_VENTANA//2 - texto_turno.get_width()//2, ALTO_VENTANA - 50))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and turno_actual == jugador_actual:
                pos = pygame.mouse.get_pos()
                celda = ClickTablero(pos, inicioX_ataque, inicioY_tableros)
                
                if celda:
                    fila, col = celda
                    coordenada = [fila, col]
                    
                    if not any(d == coordenada for d in disparos_jugador):
                        registrar_disparo(jugador_actual, coordenada)
                        
                        # Verificar impacto usando barcos_oponente directamente
                        impacto = False
                        for barco in barcos_oponente:
                            if coordenada in barco.get('posiciones', []):
                                impacto = True
                                break
                        
                        mensaje = "¡IMPACTO!" if impacto else "AGUA"
                        mensaje_tiempo = time.time()
                        switch_turn(jugador_actual)
                        time.sleep(0.3)
        clock.tick(30)


def ClickTablero(posicionT, inicioX_tablero, inicioY_tablero):
    xMouse, yMouse = posicionT
    for fila in range(tam_tablero):
        for col in range(tam_tablero):
            x = inicioX_tablero + col * tam_celda
            y = inicioY_tablero + fila * tam_celda
            rect = pygame.Rect(x, y, tam_celda, tam_celda)
            if rect.collidepoint(xMouse, yMouse):
                return fila, col
    return None

# -------------------------- FASE DEL PANEL (SHIP PLACEMENT) -----------------------------
def panel_strategy():
    # Esta función ejecuta la fase de colocación de barcos (panel de estrategia)
    reloj = pygame.time.Clock()
    inicializar_barcos()
    limpiar_grid()
    global juego_iniciado
    while not juego_iniciado:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                manejar_mousebuttondown_panel(event)
            elif event.type == pygame.MOUSEMOTION:
                manejar_mousemotion_panel(event)
            elif event.type == pygame.MOUSEBUTTONUP:
                manejar_mousebuttonup_panel(event)
        ventana.blit(fondoEstrategia, (0, 0))
        NombreTitulo("Panel de Estrategia", Fuente_opcion, negro, ventana, ANCHO_VENTANA//2, 30)

        dibujar_grilla_panel(ventana)
        dibujar_barcos_panel(ventana)
        dibujar_botones_panel(ventana)
        pygame.display.flip()
        reloj.tick(60)
    return posiciones_barcos

# -------------------------- FLUJO PRINCIPAL -----------------------------
def resetear_sala():
    # Eliminar todos los datos de la sala
    sala_ref.delete()
    # Volver a crear la estructura básica
    sala_ref.set({
        "jugador1": {},
        "jugador2": {},
        "turno": None
    })

def main():
    modo = MenuPrincipal()
    if modo != "jugar":
        pygame.quit()
        sys.exit()

    resetear_sala()

    # Selección de jugador (en este ejemplo, se asume que el usuario es jugador1)
# Selección de jugador (en este ejemplo, se asume que el usuario es jugador1)
    ventana.blit(fondo2, (0,0))
    NombreTitulo("Selecciona tu jugador", Fuente_Principal, azul, ventana, ANCHO_VENTANA//2, 100)
    boton_j1 = OpcionesMenu("Jugador 1", Fuente_opcion, blanco, azul, ventana, ANCHO_VENTANA//2 - 250, 250, 200, 50)
    boton_j2 = OpcionesMenu("Jugador 2", Fuente_opcion, blanco, azul, ventana, ANCHO_VENTANA//2 + 50, 250, 200, 50)
   
    pygame.display.flip()
    jugador_num = None
    while jugador_num not in [1, 2]:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if boton_j1.collidepoint(pos):
                    jugador_num = 1
                elif boton_j2.collidepoint(pos):
                    jugador_num = 2
    jugador_actual, datos_jugador = run_sistema_juego(jugador_num)
    # Fase de colocación de barcos (panel de estrategia)
    barcos_completos = panel_strategy()  # Se obtienen las posiciones a través de "posiciones_barcos"
    # Enviar datos a Firebase

    guardar_datos_jugador(jugador_actual, datos_jugador, posiciones_barcos,barcos_completos)
    esperar_oponente()
    if not get_turno():
        set_turno("jugador1" if jugador_num == 1 else "jugador2")
    # Fase de ataque (basada en Firebase)
    try:
        JuegoAtaque(jugador_actual)
    except Exception as e:
        print(f"Error: {str(e)}")
        mostrar_error("Error de conexión. Reintentando...")
        time.sleep(2)
        JuegoAtaque(jugador_actual)

    def mostrar_error(mensaje):
        ventana.blit(fondo2, (0,0))
        texto = Fuente_Principal.render(mensaje, True, rojo)
        ventana.blit(texto, (100 * escala_x, 300 * escala_y))  # Añade escalado
        pygame.display.flip()
        pygame.time.wait(3000)
   
    try:
        JuegoAtaque(jugador_actual)
    except Exception as e:
        print(f"Error: {str(e)}")
        mostrar_error("Error de conexión. Reintentando...")
        time.sleep(2)
        JuegoAtaque(jugador_actual)


if __name__ == '__main__':
    main()
