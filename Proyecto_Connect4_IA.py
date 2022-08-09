import numpy as np
import random
import pygame
import sys
import math

BLUE = (0,0,255)
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
YELLOW = (255,255,0)

CONTEO_FILA = 6
CONTEO_COLUMNA = 7

JUGADOR = 0
IA = 1

EMPTY = 0
PIEZA_JUGADOR = 1
PIEZA_IA = 2

LONGITUD_VENTANA = 4

#esta funcion crea el tablero del conecta 4
def crear_tablero():
	tablero = np.zeros((CONTEO_FILA,CONTEO_COLUMNA))
	return tablero

#esta funcion
def colocar_pieza(tablero, fil, col, pieza):
	tablero[fil][col] = pieza

def ubicacion_valida(tablero, col):
	return tablero[CONTEO_FILA-1][col] == 0

def siguiente_fila_disponible(tablero, col):
	for r in range(CONTEO_FILA):
		if tablero[r][col] == 0:
			return r

def ver_tablero(tablero):
	print(np.flip(tablero, 0))

def ultima_jugada_para_ganar(tablero, pieza):
	# Check horizontal locations for win
	for c in range(CONTEO_COLUMNA-3):
		for r in range(CONTEO_FILA):
			if tablero[r][c] == pieza and tablero[r][c+1] == pieza and tablero[r][c+2] == pieza and tablero[r][c+3] == pieza:
				return True

	# Check vertical locations for win
	for c in range(CONTEO_COLUMNA):
		for r in range(CONTEO_FILA-3):
			if tablero[r][c] == pieza and tablero[r+1][c] == pieza and tablero[r+2][c] == pieza and tablero[r+3][c] == pieza:
				return True

	# Check positively sloped diaganols
	for c in range(CONTEO_COLUMNA-3):
		for r in range(CONTEO_FILA-3):
			if tablero[r][c] == pieza and tablero[r+1][c+1] == pieza and tablero[r+2][c+2] == pieza and tablero[r+3][c+3] == pieza:
				return True

	# Check negatively sloped diaganols
	for c in range(CONTEO_COLUMNA-3):
		for r in range(3, CONTEO_FILA):
			if tablero[r][c] == pieza and tablero[r-1][c+1] == pieza and tablero[r-2][c+2] == pieza and tablero[r-3][c+3] == pieza:
				return True




def evaluar_ventana(ventana, pieza):
	puntaje = 0

	opp_piece = PIEZA_JUGADOR
	if pieza == PIEZA_JUGADOR:
		opp_piece = PIEZA_IA

	if ventana.count(pieza) == 4:
		puntaje += 100
	elif ventana.count(pieza) == 3 and ventana.count(EMPTY) == 1:
		puntaje += 5
	elif ventana.count(pieza) == 2 and ventana.count(EMPTY) == 2:
		puntaje += 2

	if ventana.count(opp_piece) == 3 and ventana.count(EMPTY) == 1:
		puntaje -= 4

	return puntaje

def posicion_puntaje(tablero, pieza):
	puntaje = 0

	## Score center column
	center_array = [int(i) for i in list(tablero[:, CONTEO_COLUMNA//2])]
	center_count = center_array.count(pieza)
	puntaje += center_count * 3

	## Score Horizontal
	for r in range(CONTEO_FILA):
		row_array = [int(i) for i in list(tablero[r,:])]
		for c in range(CONTEO_COLUMNA-3):
			ventana = row_array[c:c+LONGITUD_VENTANA]
			puntaje += evaluar_ventana(ventana, pieza)

	## Score Vertical
	for c in range(CONTEO_COLUMNA):
		col_array = [int(i) for i in list(tablero[:,c])]
		for r in range(CONTEO_FILA-3):
			ventana = col_array[r:r+LONGITUD_VENTANA]
			puntaje += evaluar_ventana(ventana, pieza)

	## Score posiive sloped diagonal
	for r in range(CONTEO_FILA-3):
		for c in range(CONTEO_COLUMNA-3):
			ventana = [tablero[r+i][c+i] for i in range(LONGITUD_VENTANA)]
			puntaje += evaluar_ventana(ventana, pieza)

	for r in range(CONTEO_FILA-3):
		for c in range(CONTEO_COLUMNA-3):
			ventana = [tablero[r+3-i][c+i] for i in range(LONGITUD_VENTANA)]
			puntaje += evaluar_ventana(ventana, pieza)

	return puntaje

def minimax(tablero, depth, alpha, beta, maximizingPlayer):
	ubicaiones_validas = obtener_ubicaciones(tablero)
	is_terminal = es_el_nodo_final(tablero)
	if depth == 0 or is_terminal:
		if is_terminal:
			if ultima_jugada_para_ganar(tablero, PIEZA_IA):
				return (None, 100000000000000)
			elif ultima_jugada_para_ganar(tablero, PIEZA_JUGADOR):
				return (None, -10000000000000)
			else: # Game is over, no more valid moves
				return (None, 0)
		else: # Depth is zero
			return (None, posicion_puntaje(tablero, PIEZA_IA))
	if maximizingPlayer:
		value = -math.inf
		column = random.choice(ubicaiones_validas)
		for col in ubicaiones_validas:
			fil = siguiente_fila_disponible(tablero, col)
			b_copy = tablero.copy()
			colocar_pieza(b_copy, fil, col, PIEZA_IA)
			new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
			if new_score > value:
				value = new_score
				column = col
			alpha = max(alpha, value)
			if alpha >= beta:
				break
		return column, value

	else: # Minimizing player
		value = math.inf
		column = random.choice(ubicaiones_validas)
		for col in ubicaiones_validas:
			fil = siguiente_fila_disponible(tablero, col)
			b_copy = tablero.copy()
			colocar_pieza(b_copy, fil, col, PIEZA_JUGADOR)
			new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
			if new_score < value:
				value = new_score
				column = col
			beta = min(beta, value)
			if alpha >= beta:
				break
		return column, value

def es_el_nodo_final(tablero):
	return ultima_jugada_para_ganar(tablero, PIEZA_JUGADOR) or ultima_jugada_para_ganar(tablero, PIEZA_IA) or len(obtener_ubicaciones(tablero)) == 0

def obtener_ubicaciones(tablero):
	ubicaiones_validas = []
	for col in range(CONTEO_COLUMNA):
		if ubicacion_valida(tablero, col):
			ubicaiones_validas.append(col)
	return ubicaiones_validas

def obtener_la_mejor_jugada(tablero, pieza):

	ubicaiones_validas = obtener_ubicaciones(tablero)
	best_score = -10000
	best_col = random.choice(ubicaiones_validas)
	for col in ubicaiones_validas:
		fil = siguiente_fila_disponible(tablero, col)
		temp_board = tablero.copy()
		colocar_pieza(temp_board, fil, col, pieza)
		puntaje = posicion_puntaje(temp_board, pieza)
		if puntaje > best_score:
			best_score = puntaje
			best_col = col
	return best_col

def dibujar_tablero(tablero):
	for c in range(CONTEO_COLUMNA):
		for r in range(CONTEO_FILA):
			pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
			pygame.draw.circle(screen, WHITE, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
	
	for c in range(CONTEO_COLUMNA):
		for r in range(CONTEO_FILA):
			if tablero[r][c] == PIEZA_JUGADOR:
				pygame.draw.circle(screen, RED, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
			elif tablero[r][c] == PIEZA_IA:
				pygame.draw.circle(screen, YELLOW, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
	pygame.display.update()

tablero = crear_tablero()
ver_tablero(tablero)
game_over = False

pygame.init()

SQUARESIZE = 90

width = CONTEO_COLUMNA * SQUARESIZE
height = (CONTEO_FILA+1) * SQUARESIZE

size = (width, height)

RADIUS = int(SQUARESIZE/2 - 4)

screen = pygame.display.set_mode(size)
dibujar_tablero(tablero)
pygame.display.update()

myfont = pygame.font.SysFont("monospace", 75)

turn = random.randint(JUGADOR, IA)

while not game_over:

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()

		if event.type == pygame.MOUSEMOTION:
			pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
			posx = event.pos[0]
			if turn == JUGADOR:
				label = myfont.render("RED TURN", 1, RED)
				screen.blit(label, (100, 10))

		pygame.display.update()

		if event.type == pygame.MOUSEBUTTONDOWN:
			pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
			#print(event.pos)
			# Ask for Player 1 Input
			if turn == JUGADOR:
				label = myfont.render("YELLOW TURN", 1, YELLOW)
				screen.blit(label, (40, 10))
				posx = event.pos[0]
				col = int(math.floor(posx/SQUARESIZE))

				if ubicacion_valida(tablero, col):
					fil = siguiente_fila_disponible(tablero, col)
					colocar_pieza(tablero, fil, col, PIEZA_JUGADOR)

					if ultima_jugada_para_ganar(tablero, PIEZA_JUGADOR):
						pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
						label = myfont.render("RED WINS!!", 1, RED)
						screen.blit(label, (40,10))
						game_over = True

					turn += 1
					turn = turn % 2

					ver_tablero(tablero)
					dibujar_tablero(tablero)


	# # Ask for Player 2 Input
	if turn == IA and not game_over:

		#col = random.randint(0, CONTEO_COLUMNA-1)
		#col = pick_best_move(tablero, PIEZA_IA)    Alpha     Beta
		col, minimax_score = minimax(tablero, 5, -math.inf, math.inf, True)

		if ubicacion_valida(tablero, col):
			#pygame.time.wait(500)
			fil = siguiente_fila_disponible(tablero, col)
			colocar_pieza(tablero, fil, col, PIEZA_IA)

			if ultima_jugada_para_ganar(tablero, PIEZA_IA):
				pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
				label = myfont.render("YELLOW WINS!!", 1, YELLOW)
				screen.blit(label, (30,10))
				game_over = True

			ver_tablero(tablero)
			dibujar_tablero(tablero)

			turn += 1
			turn = turn % 2

	if game_over:
		pygame.time.wait(6000)