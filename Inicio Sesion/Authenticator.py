import firebase_admin
from firebase_admin import credentials, db, auth
import pygame
import re
import sys

# Configurar Firebase
cred = credentials.Certificate(r"C:\Users\julia\OneDrive\Documentos\bookstoreproject-8b4f0-firebase-adminsdk-2eymv-b7972991ba (1).json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://bookstoreproject-8b4f0-default-rtdb.firebaseio.com/'
})

# Inicializar Pygame
pygame.init()
screen = pygame.display.set_mode((1000, 700))
pygame.display.set_caption("Sistema de Juego")

# Configuración de diseño
COLORES = {
    "fondo": (255, 255, 255),
    "primario": (0, 102, 204),
    "secundario": (173, 216, 230),
    "texto": (0, 0, 0),
    "error": (255, 0, 0),
    "inactivo": (200, 200, 200)
}

FUENTE_TITULO = pygame.font.Font(None, 48)
FUENTE_NORMAL = pygame.font.Font(None, 36)
FUENTE_BOTON = pygame.font.Font(None, 42)

def dibujar_texto(texto, y, fuente=FUENTE_NORMAL, color=COLORES["texto"]):
    texto_surface = fuente.render(texto, True, color)
    rect = texto_surface.get_rect(center=(screen.get_width()//2, y))
    screen.blit(texto_surface, rect)

def dibujar_boton(y, texto, activo=True, ancho=400, alto=60):
    color = COLORES["primario"] if activo else COLORES["inactivo"]
    rect = pygame.Rect(0, y, ancho, alto)
    rect.centerx = screen.get_width()//2
    pygame.draw.rect(screen, color, rect, border_radius=15)
    dibujar_texto(texto, rect.centery, FUENTE_BOTON, COLORES["fondo"])
    return rect, activo

def validar_password(password):
    if len(password) < 6 or len(password) > 10:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[!@#$%^&*()]', password):
        return False
    return True

def validar_username(username):
    return len(username) >= 3 and re.match(r'^\w+$', username)

# Menú principal
def menu_principal():
    while True:
        screen.fill(COLORES["fondo"])
        dibujar_texto("Menú Principal", 100, FUENTE_TITULO, COLORES["primario"])
        
        boton_login = dibujar_boton(300, "ACCEDER")[0]
        boton_registro = dibujar_boton(400, "REGISTRARSE")[0]
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if boton_login.collidepoint(event.pos):
                    formulario_login()
                elif boton_registro.collidepoint(event.pos):
                    formulario_registro()
        
        pygame.display.update()

# Formulario de Login
def formulario_login():
    campos = ["", ""]  # email, contraseña
    campo_activo = None
    error_msg = ""
    btn_siguiente_activo = False
    
    while True:
        screen.fill(COLORES["fondo"])
        dibujar_texto("Inicio de Sesión", 100, FUENTE_TITULO, COLORES["primario"])
        
        # Campos
        email_rect = pygame.Rect(300, 200, 400, 50)
        pass_rect = pygame.Rect(300, 300, 400, 50)
        
        # Dibujar campos
        for i, rect in enumerate([email_rect, pass_rect]):
            color = COLORES["primario"] if i == campo_activo else COLORES["secundario"]
            pygame.draw.rect(screen, color, rect, 2, border_radius=5)
            texto = campos[0] if i == 0 else "*" * len(campos[1])
            dibujar_texto(texto, rect.centery, FUENTE_NORMAL, COLORES["texto"])
        
        # Etiquetas
        dibujar_texto("Correo electrónico:", 180, FUENTE_NORMAL)
        dibujar_texto("Contraseña:", 280, FUENTE_NORMAL)
        
        # Botones
        btn_volver = dibujar_boton(500, "Volver", True, 200, 40)[0]
        btn_siguiente, btn_activo = dibujar_boton(400, "Siguiente", all(campos))
        
        # Manejo de eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_volver.collidepoint(event.pos):
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
                    except:
                        error_msg = "Usuario no encontrado"
                else:
                    for i, rect in enumerate([email_rect, pass_rect]):
                        if rect.collidepoint(event.pos):
                            campo_activo = i
                            break
                    else:
                        campo_activo = None
                        
            if event.type == pygame.KEYDOWN and campo_activo is not None:
                if event.key == pygame.K_BACKSPACE:
                    campos[campo_activo] = campos[campo_activo][:-1]
                else:
                    campos[campo_activo] += event.unicode
                
                btn_activo = all(campos)
        
        if error_msg:
            dibujar_texto(error_msg, 450, color=COLORES["error"])
        
        pygame.display.update()

# Formulario de Registro
def formulario_registro():
    campos = ["", "", ""]  # email, password, username
    campo_activo = None
    error_msg = ""
    btn_activo = False
    
    while True:
        screen.fill(COLORES["fondo"])
        dibujar_texto("Registro de Usuario", 100, FUENTE_TITULO, COLORES["primario"])
        
        # Campos
        rects = [pygame.Rect(300, y, 400, 50) for y in [200, 300, 400]]
        valido = all(campos) and validar_password(campos[1]) and validar_username(campos[2])
        
        for i, rect in enumerate(rects):
            color = COLORES["primario"] if i == campo_activo else COLORES["secundario"]
            pygame.draw.rect(screen, color, rect, 2, border_radius=5)
            texto = campos[i] if i != 1 else "*" * len(campos[i])
            dibujar_texto(texto, rect.centery, FUENTE_NORMAL, COLORES["texto"])
        
        dibujar_texto("Correo electrónico:", 180, FUENTE_NORMAL)
        dibujar_texto("Contraseña (6-10 caracteres, 1 mayúscula, 1 especial):", 280, FUENTE_NORMAL)
        dibujar_texto("Nombre de usuario:", 380, FUENTE_NORMAL)
        
        btn_volver = dibujar_boton(600, "Volver", True, 200, 40)[0]
        btn_siguiente, btn_activo = dibujar_boton(500, "Siguiente", valido)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_volver.collidepoint(event.pos):
                    menu_principal()
                elif btn_siguiente.collidepoint(event.pos) and btn_activo:
                    try:
                        ref = db.reference("usuarios")
                        if ref.order_by_child("username").equal_to(campos[2]).get():
                            error_msg = "Nombre de usuario ya existe"
                            continue
                            
                        user = auth.create_user(
                            email=campos[0],
                            password=campos[1]
                        )
                        ref.child(user.uid).set({
                            "email": campos[0],
                            "username": campos[2],
                            "password": campos[1]
                        })
                        pantalla_juego(campos[2])
                    except Exception as e:
                        error_msg = str(e)
                else:
                    for i, rect in enumerate(rects):
                        if rect.collidepoint(event.pos):
                            campo_activo = i
                            break
                    else:
                        campo_activo = None
                        
            if event.type == pygame.KEYDOWN and campo_activo is not None:
                if event.key == pygame.K_BACKSPACE:
                    campos[campo_activo] = campos[campo_activo][:-1]
                else:
                    campos[campo_activo] += event.unicode
                
                if campo_activo == 1 and not validar_password(campos[1]):
                    error_msg = "Contraseña inválida"
                elif campo_activo == 2 and not validar_username(campos[2]):
                    error_msg = "Usuario inválido (solo letras y números)"
                else:
                    error_msg = ""
        
        if error_msg:
            dibujar_texto(error_msg, 550, color=COLORES["error"])
        
        pygame.display.update()

# Nueva pantalla de juego modificada
def pantalla_juego(username):
    while True:
        screen.fill(COLORES["fondo"])
        
        # Mensaje de bienvenida personalizado
        dibujar_texto(f"Hola, {username}!", 100, FUENTE_TITULO, COLORES["primario"])
        
        # Botón de iniciar partida
        btn_iniciar = dibujar_boton(250, "Iniciar partida")[0]
        
        # Botón Volver
        btn_volver = dibujar_boton(350, "Volver", True, 200, 40)[0]
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_volver.collidepoint(event.pos):
                    menu_principal()
                elif btn_iniciar.collidepoint(event.pos):
                    pass  # Lógica para iniciar el juego
        
        pygame.display.update()

# Iniciar aplicación
menu_principal()