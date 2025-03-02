import pygame
import random
import firebase_admin
from firebase_admin import credentials, db
import os

# --------------------- CONFIGURACIÓN DE FIREBASE ---------------------
cred = credentials.Certificate(r"C:\Users\danim\Downloads\bookstoreproject-8b4f0-firebase-adminsdk-2eymv-b7972991ba.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://bookstoreproject-8b4f0-default-rtdb.firebaseio.com/"
})

# --------------------- CONFIGURACIÓN INICIAL ---------------------
TILE_SIZE = 60
GRID_SIZE = 7
MARGIN = 80  # Espacio para etiquetas y vidas

WIDTH = TILE_SIZE * GRID_SIZE + MARGIN
HEIGHT = TILE_SIZE * GRID_SIZE + MARGIN

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Batalla Naval")

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
HIT_COLOR = (255, 0, 0)       # Rojo para respuesta correcta
MISS_COLOR = (128, 128, 128)  # Gris para agua
BUTTON_COLOR = (180, 180, 250)
BUTTON_BORDER_COLOR = BLACK

# Fuente
font = pygame.font.SysFont(None, 30)

# Vidas globales
lives = 3

# Número máximo de tiros
MAX_SHOTS = 25
shots = 0  # Contador de tiros realizados

# Tiempo máximo en segundos (5 minutos)
max_time = 300  # 300 segundos = 5 minutos
start_ticks = pygame.time.get_ticks()  # Tiempo de inicio en milisegundos
total_pause_time = 0  # Tiempo total en pausa (en milisegundos)

# Cargar imagen del corazón
heart_path = "corazoncito.png"
try:
    heart_img = pygame.image.load(heart_path)
    heart_img = pygame.transform.scale(heart_img, (30, 30))
except Exception as e:
    print("Error al cargar la imagen de corazón:", e)
    heart_img = None

# --------------------- GENERACIÓN DE BARCOS (ubicación oculta) ---------------------
# Definición de barcos (total de 14 celdas ocupadas)
ships = [4, 3, 3, 2, 2]

def get_neighbors(cell, grid_size):
    (col, row) = cell
    neighbors = []
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            new_col = col + dx
            new_row = row + dy
            if 0 <= new_col < grid_size and 0 <= new_row < grid_size:
                neighbors.append((new_col, new_row))
    return neighbors

def place_ships_randomly(grid_size, ship_sizes):
    blocked = set()
    ships_positions = []
    for ship_size in ship_sizes:
        placed = False
        while not placed:
            orientation = random.choice(['H', 'V'])
            if orientation == 'H':
                row = random.randint(0, grid_size - 1)
                col = random.randint(0, grid_size - ship_size)
                ship_coords = [(col + i, row) for i in range(ship_size)]
            else:
                row = random.randint(0, grid_size - ship_size)
                col = random.randint(0, grid_size - 1)
                ship_coords = [(col, row + i) for i in range(ship_size)]
            if any(coord in blocked for coord in ship_coords):
                continue
            for coord in ship_coords:
                for neighbor in get_neighbors(coord, grid_size):
                    blocked.add(neighbor)
            ships_positions.append(ship_coords)
            placed = True
    return ships_positions

# Generar posiciones de los barcos y obtener todas las celdas ocupadas (no se dibujarán)
ships_positions = place_ships_randomly(GRID_SIZE, ships)
ship_cells = [cell for ship in ships_positions for cell in ship]
print("Ship cells (ocultos) usados para asignación:", ship_cells)

# --------------------- ASIGNACIÓN DE PREGUNTAS ---------------------
correct_answers = [
    "C", "A", "A", "A", "C", "B", "A", "A", "D", "B", "C", "B", "D", "B"
]

# Crear el pool de preguntas; cada pregunta tiene un "num" único.
all_questions = []
for i in range(1, len(ship_cells) + 1):
    q = {
        "num": i,
        "image": f"Preguntas batalla naval/Pregunta{i}.jpg",
        "correct": correct_answers[i-1],
        "feedback": [f"Respuesta correcta/{i}.jpg"],
        "first_hint": f"Pistas primer intento fallido/{i}.jpg"
    }
    all_questions.append(q)

def subir_preguntas_a_firebase(preguntas):
    ref_preguntas = db.reference("Preguntas")
    ref_preguntas.set(preguntas)
    print("Preguntas subidas correctamente a Firebase.")

subir_preguntas_a_firebase(all_questions)

def obtener_preguntas():
    ref = db.reference("Preguntas")
    preguntas = ref.get()
    if preguntas is None:
        print("No hay preguntas en Firebase. ¿Subiste los datos correctamente?")
        return {}
    print("Preguntas obtenidas de Firebase:", preguntas)
    return preguntas

preguntas_firebase = obtener_preguntas()

# Asignar preguntas a las celdas de barcos (clave: tupla (col, row))
question_data = {}
for i, cell in enumerate(ship_cells):
    question_data[cell] = {
        "num": i + 1,
        "image": f"Preguntas batalla naval/Pregunta{i+1}.jpg",
        "correct": correct_answers[i],
        "feedback": [f"Respuesta correcta/{i+1}.jpg"],
        "first_hint": f"Pistas primer intento fallido/{i+1}.jpg"
    }

print("\nDiccionario de preguntas con coordenadas:", question_data)

# --------------------- VARIABLES PARA ESTADO DE CELDAS ---------------------
# Celdas clickeadas: guardaremos el color a dibujar (rojo o gris)
clicked_cells = {}
# Para celdas con pregunta, controlamos intentos y si ya se respondió correctamente
attempts = {cell: 0 for cell in question_data}
answered = {cell: False for cell in question_data}

# --------------------- FUNCIONES DE DIBUJO E INTERACCIÓN ---------------------
def draw_lives():
    if heart_img:
        spacing = 5
        for i in range(lives):
            x = 10 + i * (heart_img.get_width() + spacing)
            y = 10
            screen.blit(heart_img, (x, y))
    else:
        text = font.render(f"Vidas: {lives}", True, BLACK)
        screen.blit(text, (10, 10))

def draw_shots():
    shot_text = font.render(f"Tiros: {shots}/{MAX_SHOTS}", True, BLACK)
    screen.blit(shot_text, (10, 45))

def draw_timer():
    # Calcula el tiempo transcurrido sin contar las pausas
    elapsed = (pygame.time.get_ticks() - start_ticks - total_pause_time) / 1000  # en segundos
    remaining = max_time - elapsed
    if remaining < 0:
        remaining = 0
    minutes = int(remaining // 60)
    seconds = int(remaining % 60)
    timer_text = font.render(f"Tiempo: {minutes:02d}:{seconds:02d}", True, BLACK)
    screen.blit(timer_text, (WIDTH - timer_text.get_width() - 10, 10))

def draw_stop_button():
    # Botón "Detener" en la parte superior central (fuera del área de la cuadrícula)
    button_width = 100
    button_height = 30
    x = (WIDTH - button_width) // 2
    y = 10
    stop_rect = pygame.Rect(x, y, button_width, button_height)
    pygame.draw.rect(screen, BUTTON_COLOR, stop_rect, border_radius=8)
    pygame.draw.rect(screen, BUTTON_BORDER_COLOR, stop_rect, 2, border_radius=8)
    text = font.render("Detener", True, BLACK)
    text_rect = text.get_rect(center=stop_rect.center)
    screen.blit(text, text_rect)
    return stop_rect

def draw_grid():
    for i in range(GRID_SIZE + 1):
        pygame.draw.line(screen, BLACK, (MARGIN, MARGIN + i * TILE_SIZE),
                         (MARGIN + GRID_SIZE * TILE_SIZE, MARGIN + i * TILE_SIZE))
        pygame.draw.line(screen, BLACK, (MARGIN + i * TILE_SIZE, MARGIN),
                         (MARGIN + i * TILE_SIZE, MARGIN + GRID_SIZE * TILE_SIZE))

def draw_labels():
    for col in range(GRID_SIZE):
        letter = chr(ord('A') + col)
        text = font.render(letter, True, BLACK)
        text_rect = text.get_rect(center=(MARGIN + col * TILE_SIZE + TILE_SIZE // 2, MARGIN - 20))
        screen.blit(text, text_rect)
    for row in range(GRID_SIZE):
        number = str(row + 1)
        text = font.render(number, True, BLACK)
        text_rect = text.get_rect(center=(MARGIN - 20, MARGIN + row * TILE_SIZE + TILE_SIZE // 2))
        screen.blit(text, text_rect)

def draw_clicked_cells():
    for (col, row), color in clicked_cells.items():
        rect = pygame.Rect(MARGIN + col * TILE_SIZE, MARGIN + row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)

def show_image(image_path, message=None):
    screen.fill(WHITE)
    try:
        img = pygame.image.load(image_path)
    except Exception as e:
        print("Error al cargar la imagen:", e)
        return
    img_rect = img.get_rect()
    scale_factor = min((WIDTH - 2 * MARGIN) / img_rect.width,
                       (HEIGHT - 2 * MARGIN) / img_rect.height, 1)
    new_width = int(img_rect.width * scale_factor)
    new_height = int(img_rect.height * scale_factor)
    img = pygame.transform.scale(img, (new_width, new_height))
    img_rect = img.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(img, img_rect)
    if message:
        text = font.render(message, True, BLACK)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        screen.blit(text, text_rect)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type in [pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN]:
                waiting = False

def show_feedback_images(image_paths):
    for path in image_paths:
        show_image(path)

def show_hint(hint_path):
    show_image(hint_path)

def show_penultimate_message(image_path="Mensaje penultimo intento/Mensaje.jpg"):
    show_image(image_path)

def show_final_image(final_image_path):
    show_image(final_image_path)

def show_life_loss_image(image_path):
    show_image(image_path)

def show_simple_message(message):
    screen.fill(WHITE)
    text = font.render(message, True, BLACK)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, text_rect)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type in [pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN]:
                waiting = False

def ask_use_life_dialog(current_lives):
    screen.fill(WHITE)
    message = f"¿Deseas gastar una vida? (Tienes {current_lives} vidas)"
    text = font.render(message, True, BLACK)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
    screen.blit(text, text_rect)
    button_width = 80
    button_height = 40
    spacing = 40
    start_x = (WIDTH - (2 * button_width + spacing)) // 2
    button_y = HEIGHT // 2
    yes_rect = pygame.Rect(start_x, button_y, button_width, button_height)
    no_rect = pygame.Rect(start_x + button_width + spacing, button_y, button_width, button_height)
    pygame.draw.rect(screen, BUTTON_COLOR, yes_rect, border_radius=8)
    pygame.draw.rect(screen, BUTTON_COLOR, no_rect, border_radius=8)
    pygame.draw.rect(screen, BUTTON_BORDER_COLOR, yes_rect, 2, border_radius=8)
    pygame.draw.rect(screen, BUTTON_BORDER_COLOR, no_rect, 2, border_radius=8)
    yes_text = font.render("Sí", True, BLACK)
    no_text = font.render("No", True, BLACK)
    screen.blit(yes_text, yes_text.get_rect(center=yes_rect.center))
    screen.blit(no_text, no_text.get_rect(center=no_rect.center))
    pygame.display.flip()
    choice = None
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if yes_rect.collidepoint(pos):
                    choice = "Sí"
                    waiting = False
                elif no_rect.collidepoint(pos):
                    choice = "No"
                    waiting = False
    return choice

def ask_stop_confirmation():
    # Función similar a los diálogos anteriores para confirmar si el usuario quiere detener el juego
    global total_pause_time
    pause_start = pygame.time.get_ticks()
    screen.fill(WHITE)
    message = "¿Estás seguro que deseas detener el juego?"
    text = font.render(message, True, BLACK)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
    screen.blit(text, text_rect)
    button_width = 80
    button_height = 40
    spacing = 40
    start_x = (WIDTH - (2 * button_width + spacing)) // 2
    button_y = HEIGHT // 2
    yes_rect = pygame.Rect(start_x, button_y, button_width, button_height)
    no_rect = pygame.Rect(start_x + button_width + spacing, button_y, button_width, button_height)
    pygame.draw.rect(screen, BUTTON_COLOR, yes_rect, border_radius=8)
    pygame.draw.rect(screen, BUTTON_COLOR, no_rect, border_radius=8)
    pygame.draw.rect(screen, BUTTON_BORDER_COLOR, yes_rect, 2, border_radius=8)
    pygame.draw.rect(screen, BUTTON_BORDER_COLOR, no_rect, 2, border_radius=8)
    yes_text = font.render("Sí", True, BLACK)
    no_text = font.render("No", True, BLACK)
    screen.blit(yes_text, yes_text.get_rect(center=yes_rect.center))
    screen.blit(no_text, no_text.get_rect(center=no_rect.center))
    pygame.display.flip()
    choice = None
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if yes_rect.collidepoint(pos):
                    choice = "Sí"
                    waiting = False
                elif no_rect.collidepoint(pos):
                    choice = "No"
                    waiting = False
    # Si se decide retomar, actualizar total_pause_time para que el tiempo no cuente durante la pausa.
    if choice == "No":
        pause_end = pygame.time.get_ticks()
        total_pause_time += (pause_end - pause_start)
    return choice

def show_question(image_path):
    screen.fill(WHITE)
    try:
        question_img = pygame.image.load(image_path)
    except Exception as e:
        print("Error al cargar la imagen de la pregunta:", e)
        return None
    img_rect = question_img.get_rect()
    scale_factor = 0.5
    new_width = int(img_rect.width * scale_factor)
    new_height = int(img_rect.height * scale_factor)
    question_img = pygame.transform.scale(question_img, (new_width, new_height))
    image_x = (WIDTH - new_width) // 2
    image_y = MARGIN + 10
    screen.blit(question_img, (image_x, image_y))
    
    # Botones de opciones
    button_width = 50
    button_height = 50
    spacing = 20
    options = ['A', 'B', 'C', 'D']
    total_width = len(options) * button_width + (len(options) - 1) * spacing
    start_x = (WIDTH - total_width) // 2
    button_y = image_y + new_height + 30

    option_buttons = {}
    for i, option in enumerate(options):
        rect = pygame.Rect(start_x + i * (button_width + spacing), button_y, button_width, button_height)
        option_buttons[option] = rect
        pygame.draw.rect(screen, BUTTON_COLOR, rect, border_radius=8)
        pygame.draw.rect(screen, BUTTON_BORDER_COLOR, rect, 2, border_radius=8)
        text_surface = font.render(option, True, BLACK)
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)
    
    pygame.display.flip()
    selected_option = None
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                for option, rect in option_buttons.items():
                    if rect.collidepoint(mouse_pos):
                        selected_option = option
                        waiting = False
                        break
    return selected_option

# --------------------- BUCLE PRINCIPAL DEL JUEGO ---------------------
running = True
while running:
    screen.fill(WHITE)
    draw_grid()
    draw_labels()
    draw_clicked_cells()
    draw_lives()
    draw_shots()
    draw_timer()
    stop_button_rect = draw_stop_button()  # Dibujar el botón "Detener"
    
    # Verificar si se agotó el tiempo
    elapsed = (pygame.time.get_ticks() - start_ticks - total_pause_time) / 1000  # en segundos
    if elapsed >= max_time:
        show_simple_message("Agotaste el tiempo")
        running = False
        break
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            # Si se presionó el botón "Detener"
            if stop_button_rect.collidepoint(mouse_pos):
                choice = ask_stop_confirmation()
                if choice == "Sí":
                    show_simple_message("Haz salido del juego")
                    running = False
                    break
                # Si dice "No", se retoma sin hacer más cosas en este click
                continue

            # Verificar que el click esté dentro de la cuadrícula
            if mouse_pos[0] >= MARGIN and mouse_pos[1] >= MARGIN and mouse_pos[0] < MARGIN + GRID_SIZE * TILE_SIZE and mouse_pos[1] < MARGIN + GRID_SIZE * TILE_SIZE:
                col = (mouse_pos[0] - MARGIN) // TILE_SIZE
                row = (mouse_pos[1] - MARGIN) // TILE_SIZE
                clicked_cell = (col, row)
                print("Celda clickeada:", clicked_cell)
                
                # Si ya se hizo click en la celda, se ignora (no se cuenta tiro)
                if clicked_cell in clicked_cells:
                    continue

                # Incrementar contador de tiros
                shots += 1
                print("Tiros:", shots)
                if shots >= MAX_SHOTS:
                    show_simple_message("Agotaste el número de tiros")
                    running = False
                    break
                
                # Si la celda pertenece a un barco (tiene asignada pregunta)
                if clicked_cell in question_data:
                    if not answered.get(clicked_cell, False):
                        q_data = question_data[clicked_cell]
                        user_answer = show_question(q_data["image"])
                        print("Respuesta del usuario:", user_answer)
                        if user_answer:
                            if user_answer == q_data["correct"]:
                                show_feedback_images(q_data["feedback"])
                                clicked_cells[clicked_cell] = HIT_COLOR
                                answered[clicked_cell] = True
                                print("Respuesta correcta. Celda marcada en rojo:", clicked_cell)
                            else:
                                attempts[clicked_cell] += 1
                                print("Intento", attempts[clicked_cell], "en celda", clicked_cell)
                                if attempts[clicked_cell] == 1:
                                    show_hint(q_data["first_hint"])
                                elif attempts[clicked_cell] == 2:
                                    show_penultimate_message()
                                elif attempts[clicked_cell] == 3:
                                    if lives <= 0:
                                        show_simple_message("Te has quedado sin vidas. Reinicia el juego.")
                                        running = False
                                        break
                                    choice = ask_use_life_dialog(lives)
                                    if choice == "Sí":
                                        lives -= 1
                                        life_loss_image = f"Derrota vidas/{q_data['num']}.jpg"
                                        show_life_loss_image(life_loss_image)
                                        clicked_cells[clicked_cell] = HIT_COLOR
                                        answered[clicked_cell] = True
                                        print("Se gastó una vida. Celda marcada en rojo:", clicked_cell)
                                        if lives <= 0:
                                            show_simple_message("Te has quedado sin vidas. Reinicia el juego.")
                                            running = False
                                            break
                                    else:
                                        final_image = f"Agotando los intentos/{q_data['num']}.jpg"
                                        show_final_image(final_image)
                                        show_simple_message("Derrota. Gracias por jugar!")
                                        running = False
                                        break
                else:
                    # Si la celda no pertenece a un barco (agua), se marca de gris
                    clicked_cells[clicked_cell] = MISS_COLOR

    pygame.display.flip()

pygame.quit()
