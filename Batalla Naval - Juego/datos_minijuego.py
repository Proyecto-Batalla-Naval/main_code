# datos_minijuego.py

# Inicialmente, ship_cells se define como una lista vacía.
ship_cells = []

# El diccionario que asignará cada celda con una pregunta.
question_data = {}

def generar_preguntas(correct_answers):
    """
    Genera el diccionario question_data a partir de la lista ship_cells y la lista
    de respuestas correctas (correct_answers). Se espera que ship_cells ya esté llena.
    """
    global question_data
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
    
    question_data = {}
    for i, cell in enumerate(ship_cells):
        question_data[cell] = all_questions[i]
    return question_data
