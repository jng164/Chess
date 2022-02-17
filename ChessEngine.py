"""This class is responsible for storing all the information about the current state of a chess game. It will also be responsible
for determining the valid moves at the current state. It will also keep a move log.
"""

class GameState():
	def __init__(self):
		#8x8 2D list, each element of the list has 2 characters
		#the first character represents the color 'b' or 'w'
		#the second character represents the piece 'K','Q','B','N','R','p'
		# "--" represents a blank space
		self.board = [
			["bR","bN","bB","bQ","bK","bB","bN","bR"],
			["bp","bp","bp","bp","bp","bp","bp","bp",],
			["--","--","--","--","--","--","--","--",],
			["--","--","--","--","--","--","--","--",],
			["--","--","--","--","--","--","--","--",],
			["--","--","--","--","--","--","--","--",],
			["wp","wp","wp","wp","wp","wp","wp","wp",],
			["wR","wN","wB","wQ","wK","wB","wN","wR"],

		]#subsitute to numpy arrays to gain efficiency, list of lists from white perspective
		self.whiteToMove = True
		self.movelog = []
		self.moveFunctions={'p':self.getPawnMoves, 'R':self.getRookMoves, 'N':self.getKnightMoves, 'B':self.getBishopMoves,'Q':self.getQueenMoves, 'K':self.getKingMoves}
		#track the king for pinning
		self.whiteKingLocation = (7,4)
		self.blackKingLocation = (0,4)
		self.checkMate = False
		self.staleMate = False

		#Takes a move as a parameter and executes it (separate function for castling, pawn promotion or en peasant)
	def makeMove(self, move):
		self.board[move.startRow][move.startCol] = "--"
		self.board[move.endRow][move.endCol] = move.pieceMoved
		self.movelog.append(move)#log the move so we can undo it later
		self.whiteToMove = not self.whiteToMove #swapp players
		#update king location
		if move.pieceMoved == 'wK':
			self.whiteKingLocation = (move.endRow, move.endCol)
		elif move.pieceMoved == 'bK':
			self.blackKingLocation = (move.endRow, move.endCol)



	"""Undo the last move made"""
	def undoMove(self):
		if len(self.movelog) != 0: #make sure that there is a move to undo
			move = self.movelog.pop()
			self.board[move.startRow][move.startCol] = move.pieceMoved
			self.board[move.endRow][move.endCol] = move.pieceCaptured#place new piece into the board
			self.whiteToMove = not self.whiteToMove #switch turns back
		#update king position
			if move.pieceMoved == 'wK':
				self.whiteKingLocation = (move.startRow, move.startCol)
			elif move.pieceMoved == 'bK':
				self.blackKingLocation = (move.startRow, move.startCol)

	""""def getValidMoves(self):
		return self.getAllPossibleMoves()"""

	"""All moves considering checks"""
	"""We will make the distinction between all possible moves and all valid moves. So the basic algorithm for our getValidMoves() method will be this:
-get all possible moves
- for each possible moves, check to see if it is a valid move by doing the following:
	- make the move
	- generate all possible moves for the opposing Player
 	- see if any of the moves attack your king
	- if your king is safe, it is a valid move and add it to a list
- retorn the list of valid moves only
"""
	
	def getValidMoves(self):
		#1) generate all possible moves
		moves = self.getAllPossibleMoves()
		#2) for each move, make the move
		for i in range(len(moves)-1, -1,-1):#when removing from a list go backwards through that list
			self.makeMove(moves[i])#this function switchs the turns
			#3) generate all oponent's move
		
			#4) for each of your opponent's moves, see if they attack your king
			self.whiteToMove = not self.whiteToMove
			if self.inCheck():#if after the move our king is still in check, that is not a valid move
				moves.remove(moves[i])#5) if they do attack your king, not a valid move


			self.whiteToMove = not self.whiteToMove
			self.undoMove()

		if len(moves)==0: #either checkmate or stalemate
			if self.inCheck():
				self.checkMate = True
			else:
				self.staleMate = True
		else:
			self.checkmate = False
			self.staleMate = False
		return moves

	"""Determine if the current player is in check"""
	def inCheck(self):
		if self.whiteToMove:
			return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])

		else:
			return self.squareUnderAttack(self.blackKingLocation[0],self.blackKingLocation[1])
	"""Determine if the enemy can attack the square row, col"""
	def squareUnderAttack(self,row,col):

		self.whiteToMove = not self.whiteToMove #switch to opponent's turn
		oppMoves = self.getAllPossibleMoves()
		self.whiteToMove = not self.whiteToMove#switch turn's back

		for move in oppMoves:#check if any move is attacking my location
			if move.endRow == row and move.endCol == col: #square under attack
				self.whiteToMove = not self.whiteToMove #switch turn back
				return True
		return False




	"""All moves without considering checks, we will consider all possible moves
	despite the king being or not being in check, after we have generated
	all valid moves, we will classify them with getValidMoves to see which ones the player
	can actually do"""
	def getAllPossibleMoves(self):
		moves = []
		for row in range(len(self.board)):#number of rows
			for col in range(len(self.board[row])):#number of cols in given row
				turn = self.board[row][col][0]
				if (turn == 'w' and self.whiteToMove) or (turn=='b' and not self.whiteToMove):
					piece = self.board[row][col][1]
					self.moveFunctions[piece](row,col,moves)#call the function depending on the piece

		return moves

	"""Get all the pawn moves for the pawn located at row, col and add these moves to the list"""
	"""White Pawns starts at row 6, Black pawn stars at row 2"""
	def getPawnMoves(self,row,col,moves):
		if self.whiteToMove: #white pawn move
			if self.board[row-1][col]=='--':#square pawn advance
				moves.append(Move((row,col),(row-1,col),self.board))
				if row==6 and self.board[row-2][col] == '--': #2 square pawn advance
					moves.append(Move((row,col),(row-2,col),self.board))
			if col-1 >= 0:#capture to the left
				if self.board[row-1][col-1][0] == 'b': #enemy piece to capture
					moves.append(Move((row,col),(row-1,col-1),self.board))
			if col+1 <= 7:#capture to the right
				if self.board[row-1][col+1][0] == 'b': #enemy piece to capture
					moves.append(Move((row,col),(row-1,col+1),self.board))

		else: #black pawn move
			if self.board[row+1][col]=='--':#square pawn advance
				moves.append(Move((row,col),(row+1,col),self.board))
				if row==1 and self.board[row+2][col] == '--': #2 square pawn advance
					moves.append(Move((row,col),(row+2,col),self.board))
			if col-1 >= 0:#capture to the right
				if self.board[row+1][col-1][0] == 'w': #enemy piece to capture
					moves.append(Move((row,col),(row+1,col-1),self.board))
			if col+1 <= 7:#capture to the left
				if self.board[row+1][col+1][0] == 'w': #enemy piece to capture
					moves.append(Move((row,col),(row+1,col+1),self.board))



		


		


	"""Get all the pawn moves for the rook located at row, col and add these moves to the list"""
	def getRookMoves(self,row,col,moves):
		#pass
		directions = ((-1,0),(0,-1),(1,0),(0,1)) #up,left,down,right
		enemyColor = "b" if self.whiteToMove else "w"
		for d in directions:
			for i in range(1,8):
				endRow = row + d[0]*i
				endCol = col + d[1]*i
				if 0<= endRow<8 and 0<=endCol <8: #on board
					endPiece = self.board[endRow][endCol]
					if endPiece == '--': #empty space
						moves.append(Move((row,col),(endRow,endCol),self.board))
					elif endPiece[0] == enemyColor: #enemy piece valid
						moves.append(Move((row,col),(endRow,endCol),self.board))
						break#otherwhise i could jump pieces
					else: #friendly piece invalid
						break


				else:#off board
					break


			

	def getKnightMoves(self,row,col,moves):
		knightMoves = ((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1))
		allyColor = "w" if self.whiteToMove else "b"
		for m in knightMoves:
			endRow = row + m[0]
			endCol = col + m[1]
			if 0 <= endRow <8 and 0<=endCol <8:
				endPiece = self.board[endRow][endCol]
				if endPiece[0] != allyColor: #not an ally piece (empty or enemy piece)
					moves.append(Move((row,col),(endRow,endCol),self.board))

	def getBishopMoves(self,row,col,moves):
		directions = ((-1,-1),(-1,1),(1,-1),(1,1))#4 diagonals
		enemyColor = "b" if self.whiteToMove else "w"
		for d in directions:
			for i in range(1,8):
				endRow = row + d[0]*i
				endCol = col + d[1]*i
				if 0<= endRow<8 and 0<=endCol <8: #on board
					endPiece = self.board[endRow][endCol]
					if endPiece == '--': #empty space
						moves.append(Move((row,col),(endRow,endCol),self.board))
					elif endPiece[0] == enemyColor: #enemy piece valid
						moves.append(Move((row,col),(endRow,endCol),self.board))
						break#otherwhise i could jump pieces
					else: #friendly piece invalid
						break


				else:#off board
					break

	def getQueenMoves(self,row,col,moves):
		self.getRookMoves(row,col,moves)
		self.getBishopMoves(row,col,moves)

	def getKingMoves(self,row,col,moves):
		kingMoves = ((-1,-1),(-1,0),(-1,1),(0,1),(0,-1),(1,-1),(1,0),(1,1))
		allyColor = "w" if self.whiteToMove else "b"
		for i in range(8):
			endRow = row + kingMoves[i][0]
			endCol = col + kingMoves[i][1]
			if 0<= endRow <8 and 0<= endCol < 8:
				endPiece = self.board[endRow][endCol]
				if endPiece[0] != allyColor: #not an ally piece (empty or enemy piece)
					moves.append(Move((row,col),(endRow,endCol),self.board))
		


class Move():

	#maps key to values
	# key: value
	rankstoRows = {"1":7,"2":6, "3":5, "4":4, "5":3, "6":2, "7":1, "8":0}
	rowstoRanks = {v: k for k, v in rankstoRows.items()}#reverse original dictionary
	filestoCols = {"a":0,"b":1, "c":2,"d":3,"e":4,"f":5,"g":6,"h":7}
	colstoFiles = {v: k for k, v in filestoCols.items()}

	def __init__(self,startSq, endSq, board):
		self.startRow = startSq[0]
		self.startCol = startSq[1]
		self.endRow = endSq[0]
		self.endCol = endSq[1]
		self.pieceMoved = board[self.startRow][self.startCol] 
		self.pieceCaptured = board[self.endRow][self.endCol]
		self.moveID = self.startRow*1000 + self.startCol*100 + self.endRow*10 + self.endCol #unique move ID
		#print(self.moveID)


	"""
	Override the equals method
	"""

	def __eq__(self,other):
		if isinstance(other,Move):
			return self.moveID == other.moveID
		return False

	def getChessNotation(self):
		"""
		you can add to make this like real chess notation
		"""
		return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)


	def getRankFile(self, row,col):
		return self.colstoFiles[col] + self.rowstoRanks[row]