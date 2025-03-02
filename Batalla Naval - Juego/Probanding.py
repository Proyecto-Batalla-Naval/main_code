import firebase_admin
from firebase_admin import credentials, db, auth
import pygame
import re
import sys
import requests.exceptions

# Configurar Firebase
cred = credentials.Certificate(r"C:\Users\julia\OneDrive\Documentos\bookstoreproject-8b4f0-firebase-adminsdk-2eymv-b7972991ba (1).json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://bookstoreproject-8b4f0-default-rtdb.firebaseio.com/'
})

# Inicializar Pygame
pygame.init()
info = pygame.display.Info()
ANCHO, ALTO = info.current_w, info.current_h
screen = pygame.display.set_mode((ANCHO, ALTO), pygame.FULLSCREEN)
pygame.display.set_caption("Sistema de Juego")

# Configuración de diseño
COLORES = {
    "fondo": (255, 255, 255),
    "primario": (0, 102, 204),
    "secundario": (173, 216, 230),
    "texto": (0, 0, 0),
    "error": (255, 0, 0),
    "inactivo": (200, 200, 200),
    "cerrar": (200, 50, 50),
    "cerrar_hover": (230, 70, 70)
}

FUENTE_TITULO = pygame.font.Font(None, int(ALTO/15))
FUENTE_NORMAL = pygame.font.Font(None, int(ALTO/25))
FUENTE_BOTON = pygame.font.Font(None, int(ALTO/22))
FUENTE_PEQ = pygame.font.Font(None, int(ALTO/35))

def dibujar_boton_cerrar(hover=False):
    tam = 30
    margen = 10
    rect = pygame.Rect(ANCHO - tam - margen, margen, tam, tam)
    color = COLORES["cerrar_hover"] if hover else COLORES["cerrar"]
    pygame.draw.line(screen, color, (rect.left + 8, rect.top + 8), (rect.right - 8, rect.bottom - 8), 3)
    pygame.draw.line(screen, color, (rect.right - 8, rect.top + 8), (rect.left + 8, rect.bottom - 8), 3)
    return rect

def dibujar_texto(texto, y, fuente=FUENTE_NORMAL, color=COLORES["texto"]):
    
    texto_surface = fuente.render(texto, True, color)
    rect = texto_surface.get_rect(center=(ANCHO//2, y))
    screen.blit(texto_surface, rect)

def dibujar_boton(y, texto, activo=True, ancho=None, alto=None):
    ancho = ancho or ANCHO//3.5
    alto = alto or ALTO//12
    color = COLORES["primario"] if activo else COLORES["inactivo"]
    rect = pygame.Rect(0, y, ancho, alto)
    rect.centerx = ANCHO//2
    pygame.draw.rect(screen, color, rect, border_radius=15)
    dibujar_texto(texto, rect.centery, FUENTE_BOTON, COLORES["fondo"])
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
        screen.fill(COLORES["fondo"])
        mouse_pos = pygame.mouse.get_pos()
        btn_cerrar = dibujar_boton_cerrar()
        if btn_cerrar.collidepoint(mouse_pos):
            dibujar_boton_cerrar(hover=True)
        
        dibujar_texto("Menú Principal", ALTO//5, FUENTE_TITULO, COLORES["primario"])
        boton_login = dibujar_boton(ALTO//2 - ALTO//8, "ACCEDER")[0]
        boton_registro = dibujar_boton(ALTO//2 + ALTO//16, "REGISTRARSE")[0]
        
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
        screen.fill(COLORES["fondo"])
        mouse_pos = pygame.mouse.get_pos()
        btn_cerrar = dibujar_boton_cerrar()
        if btn_cerrar.collidepoint(mouse_pos):
            dibujar_boton_cerrar(hover=True)
        
        dibujar_texto("Inicio de Sesión", ALTO//6, FUENTE_TITULO, COLORES["primario"])
        campos_rect = [
            pygame.Rect(ANCHO//4, ALTO//3, ANCHO//2, ALTO//15),
            pygame.Rect(ANCHO//4, ALTO//3 + ALTO//8, ANCHO//2, ALTO//15)
        ]
        
        for i, rect in enumerate(campos_rect):
            color = COLORES["primario"] if i == campo_activo else COLORES["secundario"]
            pygame.draw.rect(screen, color, rect, 2, border_radius=10)
            texto = campos[0] if i == 0 else "*" * len(campos[1])
            dibujar_texto(texto, rect.centery, FUENTE_NORMAL, COLORES["texto"])
        
        dibujar_texto("Correo electrónico:", campos_rect[0].top - ALTO//30, FUENTE_NORMAL)
        dibujar_texto("Contraseña:", campos_rect[1].top - ALTO//30, FUENTE_NORMAL)
        btn_volver = dibujar_boton(ALTO - ALTO//5, "Volver", ancho=ANCHO//4)[0]
        btn_siguiente, btn_activo = dibujar_boton(ALTO - ALTO//3.5, "Siguiente", all(campos), ancho=ANCHO//4)

        for event in pygame.event.get():
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
                    # Si el usuario empieza a escribir, borra el mensaje de error
                    if error_msg:
                        error_msg = ""

                    # Manejar entrada de texto
                    if event.key == pygame.K_BACKSPACE:
                        campos[campo_activo] = campos[campo_activo][:-1]
                    else:
                        campos[campo_activo] += event.unicode
                    
                    btn_activo = all(campos)

        # Mostrar el mensaje de error si existe
        if error_msg:
            dibujar_texto(error_msg, ALTO - ALTO//7, FUENTE_NORMAL, COLORES["error"])

        pygame.display.update()


def formulario_registro():
    campos = ["", "", ""]
    campo_activo = None
    error_msg = ""
    submitted = False
    start_y = ALTO // 6
    espacio_vertical = ALTO // 5
    espacio_extra = ALTO // 10
    
    # Posiciones ajustadas con espacio extra después de contraseña
    posiciones = [
        start_y,  # Correo
        start_y + espacio_vertical,  # Contraseña
        start_y + espacio_vertical + espacio_vertical + espacio_extra  # Usuario
    ]
    
    while True:
        screen.fill(COLORES["fondo"])
        mouse_pos = pygame.mouse.get_pos()
        btn_cerrar = dibujar_boton_cerrar()
        if btn_cerrar.collidepoint(mouse_pos):
            dibujar_boton_cerrar(hover=True)
        
        dibujar_texto("Registro de Usuario", ALTO//10, FUENTE_TITULO, COLORES["primario"])
        
        for i, pos_y in enumerate(posiciones):
            rect = pygame.Rect(ANCHO//4, pos_y, ANCHO//2, ALTO//12)
            color = COLORES["primario"] if i == campo_activo else COLORES["secundario"]
            pygame.draw.rect(screen, color, rect, 2, border_radius=10)
            texto = campos[i] if i != 1 else "*" * len(campos[i])
            dibujar_texto(texto, rect.centery, FUENTE_NORMAL, COLORES["texto"])
            
            # Etiquetas
            label_y = rect.top - ALTO//25
            dibujar_texto(["Correo:", "Contraseña:", "Usuario:"][i], label_y, FUENTE_NORMAL)
            
            # Mensajes de ayuda y errores
            if i == 1:
                ayudas = [
                    "Mínimo 6-10 caracteres",
                    "Al menos 1 mayúscula",
                    "Al menos 1 símbolo (!@#$%^&*())"
                ]
                y_ayuda = rect.bottom + 10
                for ayuda in ayudas:
                    dibujar_texto(ayuda, y_ayuda, FUENTE_PEQ, COLORES["texto"])
                    y_ayuda += 25
                
                if submitted:
                    errores = validar_password(campos[1])
                    if errores:
                        y_error = y_ayuda + 10
                        for error in errores:
                            dibujar_texto(error, y_error, FUENTE_PEQ, COLORES["error"])
                            y_error += 25
            
            elif i == 2:
                ayuda_y = rect.bottom + 10
                dibujar_texto("Solo letras, números y _", ayuda_y, FUENTE_PEQ, COLORES["texto"])
                
                if submitted:
                    error = validar_username(campos[2])
                    if error:
                        dibujar_texto(error, ayuda_y + 30, FUENTE_PEQ, COLORES["error"])
        
        # Botones con posición ajustada
        btn_volver_y = posiciones[-1] + espacio_vertical
        btn_siguiente_y = btn_volver_y + ALTO//10
        
        valido = all(campos) and not validar_password(campos[1]) and validar_username(campos[2]) is None
        btn_volver = dibujar_boton(btn_volver_y, "Volver", ancho=ANCHO//4)[0]
        btn_siguiente = dibujar_boton(btn_siguiente_y, "Siguiente", valido, ancho=ANCHO//4)[0]
        
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
                    campo_activo = next((i for i, pos in enumerate(posiciones) if pygame.Rect(ANCHO//4, pos, ANCHO//2, ALTO//12).collidepoint(event.pos)), None)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    menu_principal()
                elif campo_activo is not None:
                    campos[campo_activo] = campos[campo_activo][:-1] if event.key == pygame.K_BACKSPACE else campos[campo_activo] + event.unicode
                    error_msg = ""
        
        if error_msg:
            dibujar_texto(error_msg, btn_siguiente_y + ALTO//15, color=COLORES["error"])
        pygame.display.update()
import subprocess
def pantalla_juego(username):
    pygame.quit()  
    # sys.exit()  

    # Ejecuta el nuevo script
    comando = [
        "C:/Users/julia/AppData/Local/Microsoft/WindowsApps/python.exe",
        "C:/Users/julia/OneDrive/Documentos/Unal 1 semestre/Programación/Batalla naval/main_code/Batalla Naval - Juego/JuegoSonido.py",
    ]
    subprocess.run(comando)
    # while True:
        
    #     screen.fill(COLORES["fondo"])
    #     mouse_pos = pygame.mouse.get_pos()
    #     btn_cerrar = dibujar_boton_cerrar()
    #     if btn_cerrar.collidepoint(mouse_pos):
    #         dibujar_boton_cerrar(hover=True)
        
    #     dibujar_texto(f"¡Bienvenido, {username}!", ALTO//4, FUENTE_TITULO, COLORES["primario"])
    #     btn_volver = dibujar_boton(ALTO - ALTO//5, "Volver al Menú", ancho=ANCHO//3)[0]
        
    #     for event in pygame.event.get():
    #         if event.type == pygame.MOUSEBUTTONDOWN:
    #             if btn_cerrar.collidepoint(event.pos):
    #                 pygame.quit()
    #                 sys.exit()
    #             elif btn_volver.collidepoint(event.pos):
    #                 menu_principal()
    #         if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
    #             menu_principal()
    #     pygame.display.update()

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

if __name__ == "__main__":
    menu_principal()