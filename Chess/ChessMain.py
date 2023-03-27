""" Main driver file for user input to handle user input and game states"""

import pygame as p
from Chess import ChessEngine, SmartMoveFinder

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

def loadImages():
    pieces = ["wP", "wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR",
               "bP", "bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False #Flag for when valid move is made
    animate = False
    loadImages()
    running = True
    sqSelected = ()
    playerClicks = [] #stores two tuples: [(6,4), (4,4)] for position
    gameOver = False
    playerOne = True #If human is white, then true else false
    playerTwo = False #Same as above but for black
    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():

            if e.type == p.QUIT:
                running = False

            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE

                    if sqSelected == (row, col): #undo action
                        sqSelected = ()
                        playerClicks = [] #restarts both variables

                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected) #append both first and second clicks

                    if len(playerClicks) == 2:
                        move = ChessEngine.Move(playerClicks[0],playerClicks[1],gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]

            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False
                if e.key == p.K_r:
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False

        #AI MOVE FINDER
        if not gameOver and not humanTurn:
            AIMove = SmartMoveFinder.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True


        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves, sqSelected)

        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, "Black wins by checkmate!")
            else:
                drawText(screen, "White wins by checkmate!")

        elif gs.staleMate:
            gameOver = True
            drawText(screen, "Stalemate!")

        clock.tick(MAX_FPS)
        p.display.flip()

'''
Highlights squares selected and moves for selected piece
'''
def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        row, col = sqSelected
        if gs.board[row][col][0] == ("w" if gs.whiteToMove else "b"):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('blue'))
            screen.blit(s, (col*SQ_SIZE, row*SQ_SIZE))
            s.fill(p.Color("yellow"))
            for move in validMoves:
                if move.startRow == row and move.startCol == col:
                    screen.blit(s, (SQ_SIZE * move.endCol, SQ_SIZE * move.endRow))


def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)

def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            color = colors[((row+column) % 2)]
            p.draw.rect(screen, color, p.Rect(column*SQ_SIZE,row*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPieces(screen, board):
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            piece = board[row][column]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(column*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))

'''
Animating the piece
'''
def animateMove(move, screen, board, clock):
    global colors
    coords = []
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 7 if (abs(dR) + abs(dC) < 6) else 4
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        row, col = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        if move.pieceCaptured != "--":
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        screen.blit(IMAGES[move.pieceMoved], p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def drawText(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    textObject = font.render(text, 0, p.Color("grey"))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color("black"))
    screen.blit(textObject, textLocation.move(2,2))

if __name__ == "__main__":
    main()