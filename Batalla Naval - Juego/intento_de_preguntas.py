import pygame
import random
import os

# Configuración inicial
TILE_SIZE = 60
GRID_SIZE = 7
MARGIN = 40  # Espacio para etiquetas

WIDTH = TILE_SIZE * GRID_SIZE + MARGIN
HEIGHT = TILE_SIZE * GRID_SIZE + MARGIN

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Batalla Naval")

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
BUTTON_COLOR = (180, 180, 250)
BUTTON_BORDER_COLOR = BLACK

# Fuente para etiquetas y textos
font = pygame.font.SysFont(None, 30)

# Sistema de vidas global
lives = 3

# Definición de barcos (sin el barco de 1 celda → total 14 celdas)
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

# Generar posiciones de los barcos y obtener todas las celdas ocupadas (14 en total)
ships_positions = place_ships_randomly(GRID_SIZE, ships)
ship_cells = [cell for ship in ships_positions for cell in ship]

# ---------------------------------------------------------------------------
# ASIGNACIÓN DE PREGUNTAS POR CELDA (14 en total)
# ---------------------------------------------------------------------------
# Lista de respuestas correctas para cada pregunta
correct_answers = [
    "C", "A", "A", "A", "C", "B", "A", "A", "D", "B", "C", "B", "D", "B"
]

# Crear el pool de preguntas; se agrega el campo "num" para facilitar la creación de rutas
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

# Asignar las preguntas a cada celda (sin barajar para mantener la correspondencia)
question_data = {}
for i, cell in enumerate(ship_cells):
    question_data[cell] = all_questions[i]

# Inicializar diccionarios para controlar intentos y si la celda ya fue resuelta/bloqueada
attempts = {}
answered = {}
for cell in question_data:
    attempts[cell] = 0
    answered[cell] = False

# ---------------------------------------------------------------------------
# Funciones de dibujo e interacción
# ---------------------------------------------------------------------------
def draw_grid():
    for i in range(GRID_SIZE + 1):
        pygame.draw.line(screen, BLACK, (MARGIN + i * TILE_SIZE, MARGIN),
                         (MARGIN + i * TILE_SIZE, MARGIN + GRID_SIZE * TILE_SIZE))
        pygame.draw.line(screen, BLACK, (MARGIN, MARGIN + i * TILE_SIZE),
                         (MARGIN + GRID_SIZE * TILE_SIZE, MARGIN + i * TILE_SIZE))

def draw_labels():
    for col in range(GRID_SIZE):
        letter = chr(ord('A') + col)
        text = font.render(letter, True, BLACK)
        text_rect = text.get_rect(center=(MARGIN + col * TILE_SIZE + TILE_SIZE // 2, MARGIN // 2))
        screen.blit(text, text_rect)
    for row in range(GRID_SIZE):
        number = str(row + 1)
        text = font.render(number, True, BLACK)
        text_rect = text.get_rect(center=(MARGIN // 2, MARGIN + row * TILE_SIZE + TILE_SIZE // 2))
        screen.blit(text, text_rect)

def draw_ships(ships_positions):
    for ship in ships_positions:
        for (col, row) in ship:
            rect = pygame.Rect(MARGIN + col * TILE_SIZE, MARGIN + row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, BLUE, rect)

def show_question(image_path):
    screen.fill(WHITE)
    try:
        question_img = pygame.image.load(image_path)
    except Exception as e:
        print("Error al cargar la imagen:", e)
        return None
    img_rect = question_img.get_rect()
    scale_factor = 0.5
    new_width = int(img_rect.width * scale_factor)
    new_height = int(img_rect.height * scale_factor)
    question_img = pygame.transform.scale(question_img, (new_width, new_height))
    image_x = (WIDTH - new_width) // 2
    image_y = MARGIN
    screen.blit(question_img, (image_x, image_y))
    
    # Dibujar botones de opciones
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

def show_hint(hint_path):
    screen.fill(WHITE)
    try:
        hint_img = pygame.image.load(hint_path)
    except Exception as e:
        print("Error al cargar la pista:", e)
        return
    img_rect = hint_img.get_rect()
    scale_factor = 0.5
    new_width = int(img_rect.width * scale_factor)
    new_height = int(img_rect.height * scale_factor)
    hint_img = pygame.transform.scale(hint_img, (new_width, new_height))
    hint_rect = hint_img.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(hint_img, hint_rect)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type in [pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN]:
                waiting = False

def show_penultimate_message(image_path="Mensaje penultimo intento/Mensaje.jpg"):
    screen.fill(WHITE)
    try:
        penultimate_img = pygame.image.load(image_path)
    except Exception as e:
        print("Error al cargar la imagen del penúltimo intento:", e)
        return
    img_rect = penultimate_img.get_rect()
    scale_factor = 0.5
    new_width = int(img_rect.width * scale_factor)
    new_height = int(img_rect.height * scale_factor)
    penultimate_img = pygame.transform.scale(penultimate_img, (new_width, new_height))
    img_rect = penultimate_img.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(penultimate_img, img_rect)
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

def show_final_image(final_image_path):
    screen.fill(WHITE)
    try:
        final_img = pygame.image.load(final_image_path)
    except Exception as e:
        print("Error al cargar la imagen final:", e)
        return
    img_rect = final_img.get_rect()
    scale_factor = min((WIDTH - 2 * MARGIN) / img_rect.width, (HEIGHT - 2 * MARGIN) / img_rect.height, 1)
    new_width = int(img_rect.width * scale_factor)
    new_height = int(img_rect.height * scale_factor)
    final_img = pygame.transform.scale(final_img, (new_width, new_height))
    img_rect = final_img.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(final_img, img_rect)
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type in [pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN]:
                waiting = False

def show_life_loss_image(image_path):
    screen.fill(WHITE)
    try:
        img = pygame.image.load(image_path)
    except Exception as e:
        print("Error al cargar la imagen de derrota:", e)
        return
    img_rect = img.get_rect()
    scale_factor = min((WIDTH - 2 * MARGIN) / img_rect.width, (HEIGHT - 2 * MARGIN) / img_rect.height, 1)
    new_width = int(img_rect.width * scale_factor)
    new_height = int(img_rect.height * scale_factor)
    img = pygame.transform.scale(img, (new_width, new_height))
    img_rect = img.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(img, img_rect)
    pygame.display.flip()
    
    # Espera a que el usuario haga clic o presione una tecla para salir
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type in [pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN]:
                waiting = False

def show_feedback_images(image_paths):
    max_feedback_width = WIDTH - 2 * MARGIN
    max_feedback_height = HEIGHT - 2 * MARGIN
    for path in image_paths:
        screen.fill(WHITE)
        try:
            feedback_img = pygame.image.load(path)
        except Exception as e:
            print("Error al cargar la imagen de feedback:", e)
            continue
        img_rect = feedback_img.get_rect()
        scale_factor = min(max_feedback_width / img_rect.width, max_feedback_height / img_rect.height, 1)
        new_width = int(img_rect.width * scale_factor)
        new_height = int(img_rect.height * scale_factor)
        feedback_img = pygame.transform.scale(feedback_img, (new_width, new_height))
        img_rect = feedback_img.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(feedback_img, img_rect)
        pygame.display.flip()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type in [pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN]:
                    waiting = False

def show_simple_message(message):
    screen.fill(WHITE)
    text = font.render(message, True, BLACK)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, text_rect)
    pygame.display.flip()
    pygame.time.wait(2000)

def show_answer_message(answer):
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((200, 200, 200))
    screen.blit(overlay, (0, 0))
    box_width, box_height = 300, 100
    box_rect = pygame.Rect((WIDTH - box_width) // 2, (HEIGHT - box_height) // 2, box_width, box_height)
    pygame.draw.rect(screen, WHITE, box_rect)
    pygame.draw.rect(screen, BLACK, box_rect, 2)
    message = f"Haz seleccionado la opción {answer}"
    text_surface = font.render(message, True, BLACK)
    text_rect = text_surface.get_rect(center=box_rect.center)
    screen.blit(text_surface, text_rect)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type in [pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN]:
                waiting = False

# ---------------------------------------------------------------------------
# Bucle principal del juego
# ---------------------------------------------------------------------------
running = True
while running:
    screen.fill(WHITE)
    draw_grid()
    draw_labels()
    draw_ships(ships_positions)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if x >= MARGIN and y >= MARGIN and x < MARGIN + GRID_SIZE * TILE_SIZE and y < MARGIN + GRID_SIZE * TILE_SIZE:
                col = (x - MARGIN) // TILE_SIZE
                row = (y - MARGIN) // TILE_SIZE
                if any((col, row) in ship for ship in ships_positions) and not answered.get((col, row), False):
                    q_data = question_data.get((col, row))
                    if q_data:
                        user_answer = show_question(q_data["image"])
                        if user_answer:
                            if user_answer == q_data["correct"]:
                                show_feedback_images(q_data["feedback"])
                                answered[(col, row)] = True
                            else:
                                attempts[(col, row)] += 1
                                if attempts[(col, row)] == 1:
                                    show_hint(q_data["first_hint"])
                                elif attempts[(col, row)] == 2:
                                    show_penultimate_message()
                                elif attempts[(col, row)] == 3:
                                    choice = ask_use_life_dialog(lives)
                                    if choice == "Sí":
                                        if lives > 0:
                                            lives -= 1
                                            life_loss_image = f"Derrota vidas/{q_data['num']}.jpg"
                                            show_life_loss_image(life_loss_image)
                                            answered[(col, row)] = True
                                        else:
                                            show_simple_message("No te quedan vidas. Fin del juego.")
                                            running = False
                                    else:  # Usuario responde "No"
                                        final_image = f"Agotando los intentos/{q_data['num']}.jpg"
                                        show_final_image(final_image)
                                        show_simple_message("Gracias por jugar! Sigue intentando")
                                        running = False

    pygame.display.flip()
pygame.quit()
