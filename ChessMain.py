#Main driven file. Responsible for handling user input and output

import pygame as pg
from ChessEngine import *

pg.init()

pg.display.set_caption("Chess")#titol window

WIDTH, HEIGHT = 512,512
DIMENSION = 8#dimensions chess board
SQ_SIZE = HEIGHT//DIMENSION
MAX_FPS = 15
IMAGES = {}

BROWN = (205,133,63)
LIGHT_BROWN = (255,248,220)



"""load images, intialize global dictionary of images
"""
def load_Images():
	pieces= ["wp","wR","wN","wB","wK","wQ","bp","bR","bN","bB","bK","bQ"]
	for piece in pieces:
		IMAGES[piece] = pg.transform.scale(pg.image.load("images/" + piece+".png"), (SQ_SIZE,SQ_SIZE))

	#we can accees and image by sayin "IMAGES['wp']"


"""
Responsible for all the graphics within a current game state
"""
def drawGameState(WIN,gs):
	drawBoard(WIN) #draw squares on the board
	drawPieces(WIN, gs.board) #draw pieces on squares

"""
Draw the squares on the board Top left square is always light.
"""

def drawBoard(WIN):
	colors = [LIGHT_BROWN, BROWN]
	for row in range(DIMENSION):
		for col in range(DIMENSION):
			color = colors[((row+col)%2)]
			pg.draw.rect(WIN,color, pg.Rect(col*SQ_SIZE,row*SQ_SIZE, SQ_SIZE,SQ_SIZE))





"""
Draw the pieces on the board using the current GameState.board
"""
def drawPieces(WIN, board):
	for row in range(DIMENSION):
		for col in range(DIMENSION):
			piece = board[row][col]
			
			if piece != "--": #not empty space
				piece_rect = pg.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE,SQ_SIZE)
				WIN.blit(IMAGES[piece], piece_rect)



#Main driver for our code. This will handle user input and updating graphics

def main():

	WIN = pg.display.set_mode((WIDTH,HEIGHT))

	clock = pg.time.Clock()
	WIN.fill(pg.Color("white"))
	gs = GameState()
	validMoves = gs.getValidMoves()
	moveMade = False #flag variable for when a move is made, when the user has moved, we should generate another set of valid moves

	load_Images()#only do this once

	run = True
	sqSelected = ()#square selecteed initially, keep track of the last click of the user (row,col)
	playerClicks = []#keep track of the player clicks (two tupples: [(6,4),(4,4)])

	while run:

		clock.tick(MAX_FPS)

		for event in pg.event.get():
			if event.type == pg.QUIT:
				run = False



			#mouse handler
			elif event.type == pg.MOUSEBUTTONDOWN:
				location = pg.mouse.get_pos() #x,y location of mouse
				col = location[0]//SQ_SIZE
				row = location[1]//SQ_SIZE
				if sqSelected == (row,col): #the user clicked the same square twice
					sqSelected = ()#deselect
					playerClicks = []#clear player clicks
				else:
					sqSelected = (row,col)
					playerClicks.append(sqSelected)#append for both 1st and 2nd clicks

				if len(playerClicks) == 2: #after 2nd click
					move = Move(playerClicks[0], playerClicks[1], gs.board)
					print(move.getChessNotation())
					if move in validMoves:
						moveMade = True
						gs.makeMove(move)

						sqSelected = ()#reset user clicks
						playerClicks = []
					else:
						playerClicks=[sqSelected]

			#key handlers
			elif event.type == pg.KEYDOWN:
				if event.key == pg.K_z: #undo when 'z' is pressed
					gs.undoMove()
					moveMade = True
					
		if moveMade:
			validMoves = gs.getValidMoves()
			moveMade = False



		drawGameState(WIN,gs)
		

		pg.display.update()
	pg.quit()#quit pygame close the window



if __name__ == "__main__": #we only run the game when we run this file 
	main()
