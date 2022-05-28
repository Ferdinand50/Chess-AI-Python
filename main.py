import numpy as np
import pygame as p
from pygame.constants import KEYDOWN, MOUSEBUTTONDOWN
import backend
import movement
import AImoves



#bugg alpha beta pruning is not working correct

#initialize pygame
p.init()

#setup the pygame window
WIDTH, HEIGHT = 600, 600
CHESSFIELD_DIMENSION = WIDTH // 8
FPS = 20
p.display.set_caption("Chess")
#color board
WHITE =(220, 220, 180)
DARKGREEN =(60, 155, 50)
imagesPieces = {}
#convertion of gameboard array
stringsToInt = {"wP":11,"wR":12,"wN":13,"wB":14,"wQ":15,"wK":16,
                "bP":21,"bR":22,"bN":23,"bB":24,"bQ":25,"bK":26, "empty":0}
IntToStrings = {v: k for k, v in stringsToInt.items()}


#handeling the chess game
#drawing pieces and board
def main():
    p.init()
    WIN = p.display.set_mode((WIDTH, HEIGHT))
    load_pieces()
    run = True
    #2D list for storing start and end square
    lastSquareSelected = {}
    MoveSelected = []
    gs = backend.gameBoard()
    LegalMoves = movement.getLegalMoves(gs)
    clock = p.time.Clock()
    MoveMade = False
    gameover = False
    WhiteHuman = True
    BlackHuman = False
    #loop through events which occur
    while run:
        humanTurn = (gs.WhitesTurn and WhiteHuman) or (not gs.WhitesTurn and BlackHuman)
        for event in p.event.get():
            # quits the game
            if event.type == p.QUIT:
                run = False
            #mouseclicks -> move
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    #only can make moves if game is not over or players turn
                    if not gameover and humanTurn:
                            #mouseclick position
                            mx, my = p.mouse.get_pos()
                            #square from 0 - 7
                            rank_square = my // CHESSFIELD_DIMENSION
                            file_square = mx // CHESSFIELD_DIMENSION
                            #first click is only possible for piece of own color
                            if (gs.WhitesTurn and len(MoveSelected) == 0 and int(str(gs.board[rank_square][file_square])[0]) == 1) or len(MoveSelected) != 0 or (not gs.WhitesTurn and len(MoveSelected) == 0 and int(str(gs.board[rank_square][file_square])[0]) == 2):
                                #double click is not possible
                                if (rank_square, file_square) == lastSquareSelected:
                                    print("double click")
                                    MoveSelected = []
                                    lastSquareSelected = {}
                                else:
                                    lastSquareSelected = (rank_square, file_square)
                                    #cant select empty squares as start as position
                                    if gs.board[rank_square][file_square] != 0 or len(MoveSelected) == 1:
                                        MoveSelected.append(lastSquareSelected)
                                        #selected piece changes
                                        if len(MoveSelected) == 2 and int(str(gs.board[rank_square][file_square])[0]) == int(str(gs.board[MoveSelected[0][0]][MoveSelected[0][1]])[0]):
                                            MoveSelected.pop(0)
                                            lastSquareSelected = MoveSelected[0]
                                    #move initialized through two clicks
                                    if len(MoveSelected) == 2:
                                        Move = movement.MoveStored(gs, MoveSelected[0][0], MoveSelected[0][1], MoveSelected[1][0], MoveSelected[1][1])
                                        for i in range(len(LegalMoves)):
                                            if Move == LegalMoves[i]:
                                                movement.makeMove(gs, LegalMoves[i])
                                                #if gs.WhitesTurn:
                                                    #print("whites turn")
                                                #elif not gs.WhitesTurn:
                                                    #print("blacks turn")
                                                lastSquareSelected = {}
                                                MoveSelected = []
                                                MoveMade = True
                                        if not MoveMade:
                                            MoveSelected = []  
            
            #undoMove
            if event.type == p.KEYDOWN:
                if event.key == p.K_z:
                    if len(gs.MoveLog) > 0:
                        print("undoMove")
                        movement.undoMove(gs)
                        LegalMoves = movement.getLegalMoves(gs)
                #resets the game
                elif event.key == p.K_r:
                    gs = backend.gameBoard()
                    LegalMoves= movement.getLegalMoves(gs)
                    lastSquareSelected = {} 
                    MoveSelected = []
                    MoveMade = False
                    gameover = False
        
        #AI Moves
        if not gameover and not humanTurn:
            #LegalMoves = movement.getLegalMoves(gs)
            AImove = AImoves.returnOpponentsMove(gs, LegalMoves)
            #AImove =AImoves.getRandomMove(gs, LegalMoves)
            #AImove = AImoves.TwoLayerSearch(gs,LegalMoves)
            if AImove is not None:
                movement.makeMove(gs, AImove)
                #gs.MoveLog.append(AImove)
                gs.MoveLog= np.append(gs.MoveLog, AImove)
                MoveMade = True
            else:
                print("move is none")
                # AImove = AImoves.getRandomMove(gs, LegalMoves)
                # movement.makeMove(gs, AImove)
                # gs.MoveLog= np.append(gs.MoveLog, AImove)
                # MoveMade = True

        if MoveMade:
            LegalMoves = movement.getLegalMoves(gs)
            MoveMade = False
            gameover = False
        drawGame(WIN, gs, lastSquareSelected, LegalMoves, gs.MoveLog)

        if gs.checkmate:
            gameover = True
            if gs.WhitesTurn:
                drawGameText(WIN, "Black wins by Checkmate")
            else:
                drawGameText(WIN, "White wins by Checkmate")
        elif gs.stalemate:
            gameover = True
            drawGameText(WIN, "Stalemate")

        


        #setup Framerate
        clock.tick(FPS)
        p.display.flip()


        
    p.quit()
#draws the game
def drawGame(WIN, gs, lastSquareSelected, LegalMoves, MoveLog):
    draw_board(WIN)
    drawHighlights(WIN, gs, lastSquareSelected, LegalMoves, MoveLog)
    draw_pieces(WIN, gs)
    


#draws the game board
# row = rank
# column = file
def draw_board(WIN):
    colors = [p.Color(WHITE), p.Color(DARKGREEN)]
    for rank in range(8):
        for file in range(8):
            color = colors[((rank+file)% 2 )]
            p.draw.rect(WIN, color, p.Rect(file*CHESSFIELD_DIMENSION, rank*CHESSFIELD_DIMENSION, CHESSFIELD_DIMENSION, CHESSFIELD_DIMENSION))


def draw_pieces(WIN, gs):
    for rank in range(8):
        for file in range(8):
            piece_name = IntToStringconverter(gs.board[rank][file])
            if piece_name != "empty":
                WIN.blit(imagesPieces[piece_name], p.Rect(file * CHESSFIELD_DIMENSION, rank * CHESSFIELD_DIMENSION, CHESSFIELD_DIMENSION, CHESSFIELD_DIMENSION))

def drawHighlights(WIN, gs, lastSquareSelected, LegalMoves, MoveLog):
    #piece selected
    square = p.Surface((CHESSFIELD_DIMENSION, CHESSFIELD_DIMENSION))
    square.set_alpha(100)
    square.fill(p.Color("blue"))
    if lastSquareSelected != {}:
        rank, file = lastSquareSelected
        #hiughlight legal moves
        if gs.board[rank][file] != 0:
            if (gs.WhitesTurn and int(str(gs.board[rank][file])[0]) == 1) or (not gs.WhitesTurn and int(str(gs.board[rank][file])[1])):
                WIN.blit(square, (file*CHESSFIELD_DIMENSION, rank*CHESSFIELD_DIMENSION))
                for move in LegalMoves:
                    if move.rank_start == rank and move.file_start == file:
                        square.fill(p.Color("yellow"))
                        WIN.blit(square, (move.file_end*CHESSFIELD_DIMENSION, move.rank_end*CHESSFIELD_DIMENSION))
    #highlight last piece moved
    if len(MoveLog) != 0:
        lastMove = MoveLog[len(MoveLog)-1]
        #color
        square.fill(p.Color("orange"))
        #starting position
        WIN.blit(square, (lastMove.file_start*CHESSFIELD_DIMENSION, lastMove.rank_start*CHESSFIELD_DIMENSION))
        #end position
        WIN.blit(square, (lastMove.file_end*CHESSFIELD_DIMENSION, lastMove.rank_end*CHESSFIELD_DIMENSION))
        


def drawGameText(WIN, gametext):
    font = p.font.SysFont("Helvitca", 32, True, False)
    #render text
    text = font.render(gametext, 0, (255,0 ,0))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 -text.get_width()/2, HEIGHT/2 - text.get_height()/2)
    #show text
    WIN.blit(text, textLocation)



def IntToStringconverter(piece_number):
    return IntToStrings[piece_number]
  


#load images of pieces
def load_pieces():
    #pieces notation white: 1 black:2
    #pawn: 1 Rook: 2 Knight: 3 Bishop: 4 Queen: 5 King: 6
    #0 = empty
    pieces = ["wP", "wR", "wN", "wB", "wQ", "wK", "bP", "bR", "bN", "bB", "bQ", "bK"]
    for piece in pieces:
        imagesPieces[piece] = p.transform.smoothscale(p.image.load("images/" + piece + ".png"), (CHESSFIELD_DIMENSION, CHESSFIELD_DIMENSION))

        


#runs main
if __name__ == "__main__":
    main()







