import backend
import main
import numpy as np

#pieces notation white: 1 black:2
#pawn: 1 Rook: 2 Knight: 3 Bishop: 4 Queen: 5 King: 6
#0 = empty
#moveFunctions = {1: getPawnMoves, 2: getRookMoves, 3: getKnightMoves, 4: getBishopMoves, 5: getQueenMoves,
#         6: getKingMoves}

def makeMove(gs, Move): 
    gs.board[Move.rank_start][Move.file_start] = 0
    gs.board[Move.rank_end][Move.file_end] = Move.pieceMoved
    #change Turn
    gs.WhitesTurn = not gs.WhitesTurn
    #Pawn Promotion
    if int(str(Move.pieceMoved)[1]) == 1:
        if Move.rank_end == 0:
            gs.board[Move.rank_end][Move.file_end] = 15
        elif Move.rank_end == 7:
            gs.board[Move.rank_end][Move.file_end] = 25
    #update King position
    if int(str(Move.pieceMoved)[1]) == 6:
        #white
        if int(str(Move.pieceMoved)[0]) == 1:
            gs.whiteKingPosition = (Move.rank_end, Move.file_end)
        #black
        elif int(str(Move.pieceMoved)[0]) == 2:
            gs.blackKingPosition = (Move.rank_end, Move.file_end)
    #castling )
    if Move.isCastleMove: 
        if Move.file_end - Move.file_start == 2: #kingside
            gs.board[Move.rank_end][Move.file_end-1] = gs.board[Move.rank_end][Move.file_end+1]#move rook
            gs.board[Move.rank_end][Move.file_end+1] = 0
        else: #queenside
            gs.board[Move.rank_end][Move.file_end+1] = gs.board[Move.rank_end][Move.file_end-2]
            gs.board[Move.rank_end][Move.file_end-2] = 0
    #update castleRights
    updateCastlerights(gs, Move.pieceMoved, Move.pieceTaken, Move.rank_end, Move.file_end)
    #append castlerights to log
    gs.CastleRightsLog.append(backend.CastleRights(gs.currentCastleRights.bqs, gs.currentCastleRights.bks,
                                                gs.currentCastleRights.wqs, gs.currentCastleRights.wks))
    #append the move to MoveLog
    gs.MoveLog = np.append(gs.MoveLog, Move)
    #gs.MoveLog.append(Move) 


def undoMove(gs):
    if len(gs.MoveLog) != 0:
        #Move = gs.MoveLog.pop()
        Move = gs.MoveLog[-1]
        gs.MoveLog = np.delete(gs.MoveLog, -1)
        gs.board[Move.rank_start][Move.file_start] = Move.pieceMoved
        gs.board[Move.rank_end][Move.file_end] = Move.pieceTaken
        #change of color
        gs.WhitesTurn = not gs.WhitesTurn
        #update king position
        if int(str(Move.pieceMoved)[1]) == 6:
            #white
            if int(str(Move.pieceMoved)[0]) == 1:
                gs.whiteKingPosition = (Move.rank_start, Move.file_start)
            #black
            elif int(str(Move.pieceMoved)[0]) == 2:
                gs.blackKingPosition = (Move.rank_start, Move.file_start)
        #castling
        #undo castlerights
        gs.CastleRightsLog.pop()
        newRights = gs.CastleRightsLog[-1]
        gs.currentCastleRights = (backend.CastleRights(newRights.bqs, newRights.bks, newRights.wqs, newRights.wks))
        if Move.isCastleMove:
            #kingside Castling
            if Move.file_end - Move.file_start == 2:
                #move rook back
                gs.board[Move.rank_end][Move.file_end+1] = gs.board[Move.rank_end][Move.file_end-1]
                gs.board[Move.rank_end][Move.file_end-1] = 0
            #queenside
            else: 
                #move rook back
                gs.board[Move.rank_end][Move.file_end-2] = gs.board[Move.rank_end][Move.file_end+1]
                gs.board[Move.rank_end][Move.file_end+1] = 0
        gs.checkmate = False
        gs.stalemate = False
        #delete Move from Log
        

def getCastleMoves(gs, rank_start, file_start, moves):
    if squareUnderAttack(gs, rank_start,file_start):
        return moves
    if (gs.WhitesTurn and gs.currentCastleRights.wks) or (not gs.WhitesTurn and gs.currentCastleRights.bks):
        moves = getKingsideCastleMoves(gs, rank_start, file_start, moves)
    if (gs.WhitesTurn and gs.currentCastleRights.wqs) or (not gs.WhitesTurn and gs.currentCastleRights.bqs):
        moves = getQueensideCastleMoves(gs, rank_start, file_start, moves)
    return moves
    

def getKingsideCastleMoves(gs, rank_start, file_start, moves):
    if gs.board[rank_start][file_start+1] == 0 and gs.board[rank_start][file_start+2] == 0:
        if not squareUnderAttack(gs, rank_start, file_start+1) and not squareUnderAttack(gs, rank_start, file_start+2):
            #moves.append(MoveStored(gs, rank_start,file_start, rank_start, file_start+2, isCastleMove =True))
            moves = np.append(moves,MoveStored(gs, rank_start,file_start, rank_start, file_start+2, isCastleMove =True))
    return moves

def getQueensideCastleMoves(gs, rank_start, file_start, moves):
    if gs.board[rank_start][file_start-1] == 0 and gs.board[rank_start][file_start-2] == 0 and gs.board[rank_start][file_start-3] == 0:
        if not squareUnderAttack(gs, rank_start, file_start-1) and not squareUnderAttack(gs, rank_start, file_start-2):
            #moves.append(MoveStored(gs, rank_start,file_start, rank_start, file_start-2, isCastleMove =True))
            moves = np.append(moves, MoveStored(gs, rank_start,file_start, rank_start, file_start-2, isCastleMove =True) )
    return moves
#checks if the selected square is under attack 
#need ally color
def squareUnderAttack(gs, rank_start, file_start):
    gs.WhitesTurn = not gs.WhitesTurn
    oppMoves = getTheoreticalMoves(gs)
    gs.WhitesTurn = not gs.WhitesTurn
    for move in oppMoves:
        if move.rank_end == rank_start and move.file_end == file_start:
            return True
    return False


def getTheoreticalMoves(gs):
    #change this to nparray
    TheoreticalMoves = np.array([])
    for rank in range(8):
        for file in range(8):
            #whites turn
            if gs.WhitesTurn and gs.board[rank][file] < 20 and gs.board[rank][file] != 0: 
                #breakpoint()
                if gs.board[rank][file] == 11:
                    TheoreticalMoves = getPawnMoves(gs, rank, file, TheoreticalMoves)
                elif gs.board[rank][file] == 12:
                    TheoreticalMoves = getRookMoves(gs, rank, file, TheoreticalMoves)
                elif gs.board[rank][file] == 13:
                    TheoreticalMoves = getKnightMoves(gs, rank, file, TheoreticalMoves)
                elif gs.board[rank][file] == 14:
                    TheoreticalMoves = getBishopMoves(gs, rank, file, TheoreticalMoves)
                elif gs.board[rank][file] == 15:
                    TheoreticalMoves = getQueenMoves(gs, rank, file, TheoreticalMoves)
                elif gs.board[rank][file] == 16:
                    TheoreticalMoves = getKingMoves(gs, rank, file, TheoreticalMoves)



            #blacks turn
            elif not gs.WhitesTurn and gs.board[rank][file] > 20:
                if gs.board[rank][file] == 21:
                   TheoreticalMoves = getPawnMoves(gs, rank, file, TheoreticalMoves)
                elif gs.board[rank][file] == 22:
                    TheoreticalMoves =getRookMoves(gs, rank, file, TheoreticalMoves)
                elif gs.board[rank][file] == 23:
                    TheoreticalMoves =getKnightMoves(gs, rank, file, TheoreticalMoves)
                elif gs.board[rank][file] == 24:
                    TheoreticalMoves =getBishopMoves(gs, rank, file, TheoreticalMoves)
                elif gs.board[rank][file] == 25:
                    TheoreticalMoves =getQueenMoves(gs, rank, file, TheoreticalMoves)
                elif gs.board[rank][file] == 26:
                    TheoreticalMoves =getKingMoves(gs, rank, file, TheoreticalMoves)
    return TheoreticalMoves

def getLegalMoves(gs):
    #copies current Castle Rights so if King moves in checking King nothing happens
    tempCastleRights = backend.CastleRights(gs.currentCastleRights.bqs, gs.currentCastleRights.bks,
                                                gs.currentCastleRights.wqs, gs.currentCastleRights.wks)
    moves = np.array([])
    gs.inCheck, gs.pins, gs.checks = checkForPinsAndChecks(gs)
    if gs.WhitesTurn:
        position_rank, position_file = gs.whiteKingPosition
    else:
        position_rank, position_file = gs.blackKingPosition
    #King in Check
    if gs.inCheck:
        if len(gs.checks) == 1:
            moves = getTheoreticalMoves(gs)
            #block check
            check = gs.checks[0]
            check_rank = check[0]
            check_file = check[1]
            #enemy piece causing the check
            pieceChecking = gs.board[check_rank][check_file]
            #squares that pieces an move to
            validSquares = []
            #if knight capture it or move king
            if int(str(pieceChecking)[1]) == 3:
                validSquares = [(check_rank, check_file)]
            else: 
                for i in range(1, 8):
                    #check[2] and check[3] are the check directions
                    validSquare = (position_rank + check[2]*i, position_file + check[3] * i)
                    validSquares.append(validSquare)
                    #once you get to piece end checks
                    if validSquare[0] == check_rank and validSquare[1] == check_file:
                        break
            #deletes moves which are not legal
            #backwards iteration
            for i in range(len(moves)-1 , -1, -1):
                #move doesnt move king so it must block or capture
                if int(str(moves[i].pieceMoved)[1]) != 6:
                    #move doesnt block or capture
                    if not (moves[i].rank_end, moves[i].file_end) in validSquares:
                        #moves.remove(moves[i])
                        moves = np.delete(moves, i)
            gs.currentCastleRights = tempCastleRights
        #double check king has to move
        else:
            getKingMoves(gs, position_rank, position_file, moves)
    #all moves are fine
    else:
        moves = getTheoreticalMoves(gs)
        #get castle moves only possible if there is no check
        gs.currentCastleRights = tempCastleRights
        moves = getCastleMoves(gs, position_rank, position_file, moves)
    CheckmateandStalemate(gs, moves)
    return moves


def checkForPinsAndChecks(gs):
    pins = []
    checks =[]
    inCheck = False
    #whites turn
    if gs.WhitesTurn:
        enemyColor = 2
        allyColor = 1
        position_rank, position_file = gs.whiteKingPosition
    #blacks turn
    else:
        enemyColor = 1
        allyColor = 2
        position_rank, position_file = gs.blackKingPosition
    #checking from King location outward for pins and ckechs, pins get stored
    directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
    for j in range(len(directions)):
        d = directions[j]
        #reset possbile pin
        PossiblePin = ()
        for i in range(1, 8):
            end_rank = position_rank + d[0] * i
            end_file = position_file + d[1] * i
            if 0 <= end_rank < 8 and 0 <= end_file < 8:
                endPiece = gs.board[end_rank][end_file]
                if int(str(endPiece)[0]) == allyColor and int(str(endPiece)[1]) != 6:
                    #only first ally piece can be pinned
                    if PossiblePin == ():
                        PossiblePin = (end_rank, end_file, d[0], d[1])
                    #already second pin so no need to check for further pins
                    else:
                        break
                elif int(str(endPiece)[0]) == enemyColor:
                    #declaration of type of selected piece
                    #vertical + horizontal multiple squares: Queen and Rook
                    #vertical + horizontal single squares: Queen, King Rook
                    #diagonal multiple squares: Queen, Bishop 
                    #diagonal single squares: Queen, King, Bishop and Pawn
                    #pieces notation white: 1 black:2
                    #pawn: 1 Rook: 2 Knight: 3 Bishop: 4 Queen: 5 King: 6
                    type = int(str(endPiece)[1])
                    if (0 <= j <= 3 and type == 2) or (4 <= j <= 7 and type == 4) or (i == 1 and type == 1 and ((enemyColor == 1 and 6 <= j <= 7) or \
                        (enemyColor == 2 and 4<= j <= 5 ))) or (type == 5) or (i == 1 and type == 6):
                        #no pin so its check
                        if PossiblePin == ():
                            inCheck = True
                            checks.append((end_rank, end_file, d[0], d[1]))
                            break
                        ##allied piece is blocking check so pin
                        else:
                            pins.append(PossiblePin)
                    #enemy piece but not applying check
                    else:
                        break
            else:
                break
    #check for knights checks
    knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
    for m in knightMoves:
        end_rank = position_rank +m[0]
        end_file = position_file +m[1]
        if 0 <= end_rank < 8 and 0 <= end_file < 8:
            endPiece = gs.board[end_rank][end_file]
            if int(str(endPiece)[0]) == enemyColor and int(str(endPiece)[1]) == 3:
                inCheck = True
                checks.append((end_rank, end_file, m[0], m[1]))
    return inCheck, pins, checks

#checks if the game is over 
def CheckmateandStalemate(gs, moves):
    #no Moves left so it is game over
    if len(moves) == 0:
        if gs.inCheck:
            gs.checkmate = True
        elif not gs.inCheck:
            gs.stalemate = True 

#updates the current castlerights for the gamestate if Rook or king moves or is captured
def updateCastlerights(gs, pieceMoved, pieceCaptured, rank_start, file_start):
    #white King has moved
    if pieceMoved == 16:
        gs.currentCastleRights.wks = False
        gs.currentCastleRights.wqs = False
    #black King has moved
    elif pieceMoved == 26:
        gs.currentCastleRights.bks = False
        gs.currentCastleRights.bqs = False
    #white Rook
    elif pieceMoved == 12:
        if rank_start == 7:
            #Rook on the Queen side has moved
            if file_start == 0:
                gs.currentCastleRights.wqs = False
            #Rook on King side has moved
            elif file_start == 7:
                gs.currentCastleRights.wks = False
    #black Rook
    elif pieceMoved == 22:
        if rank_start == 0:
            #Rook on the Queen side has moved
            if file_start == 0:
                gs.currentCastleRights.bqs = False
            #Rook on King side has moved
            elif file_start == 7:
                gs.currentCastleRights.bks = False
    #if white rook is captured
    if pieceCaptured == 12:
        #Rook on the Queen side is captured
        if rank_start == 7:
            if file_start == 0:
                gs.currentCastleRights.wqs = False
            #Rook on the King side is captured
            elif file_start == 7:
                gs.currentCastleRights.wks = False
        #if black rook is captured
        elif pieceCaptured == 12:
            if rank_start == 0:
                if file_start == 0:
                    gs.currentCastleRights.bqs = False
                elif file_start == 7:
                    gs.currentCastleRights.bks = False




def getPawnMoves(gs, position_rank, position_file, TheoreticalMoves):
        #check is piece is pinned
        #breakpoint()
        piecePinned = False
        pinDirection = ()
        for i in range(len(gs.pins)-1, -1, -1):
            if gs.pins[i][0] == position_rank and gs.pins[i][1] == position_file:
                piecePinned = True
                pinDirection = (gs.pins[i][2], gs.pins[i][3])
                gs.pins.remove(gs.pins[i])
                break

        if gs.WhitesTurn: #white
            if gs.board[position_rank-1][position_file] ==0:
                if not piecePinned or pinDirection == (-1, 0):
                    #TheoreticalMoves.append(MoveStored(gs, position_rank, position_file, position_rank-1, position_file))
                    TheoreticalMoves = np.append(TheoreticalMoves, MoveStored(gs, position_rank, position_file, position_rank-1, position_file))
                    if position_rank == 6 and gs.board[position_rank-2][position_file] == 0:
                        #TheoreticalMoves.append(MoveStored(gs, position_rank, position_file , position_rank-2, position_file))
                        TheoreticalMoves = np.append(TheoreticalMoves, MoveStored(gs, position_rank, position_file , position_rank-2, position_file))
            if position_file-1 >=0: #captures to the left
                if int(str(gs.board[position_rank-1][position_file-1])[0]) == 2: 
                    if not piecePinned or pinDirection == (-1, -1):
                        #TheoreticalMoves.append(MoveStored(gs, position_rank,position_file,position_rank-1,position_file-1))
                        TheoreticalMoves = np.append(TheoreticalMoves, MoveStored(gs, position_rank,position_file,position_rank-1,position_file-1))
            if position_file+1 <= 7: #captures to the right
                if int(str(gs.board[position_rank-1][position_file+1])[0]) == 2:
                    if not piecePinned or pinDirection == (-1, 1):
                        #TheoreticalMoves.append(MoveStored(gs, position_rank,position_file,position_rank-1,position_file+1))
                        TheoreticalMoves = np.append(TheoreticalMoves, MoveStored(gs, position_rank,position_file,position_rank-1,position_file+1))

        if not gs.WhitesTurn and position_rank<7: #black
            if gs.board[position_rank+1][position_file] == 0:
                if not piecePinned or pinDirection == (1, 0):
                    #TheoreticalMoves.append(MoveStored(gs, position_rank,position_file, position_rank+1,position_file))
                    TheoreticalMoves = np.append(TheoreticalMoves,MoveStored(gs, position_rank,position_file, position_rank+1,position_file))
                    if position_rank == 1 and gs.board[position_rank+2][position_file] == 0:
                        #TheoreticalMoves.append(MoveStored(gs, position_rank,position_file,position_rank+2,position_file))
                        TheoreticalMoves = np.append(TheoreticalMoves,MoveStored(gs, position_rank,position_file,position_rank+2,position_file))
            if position_file-1 >=0: #captures to the left
                if int(str(gs.board[position_rank+1][position_file-1])[0]) == 1:
                    if not piecePinned or pinDirection == (1, -1): 
                        #TheoreticalMoves.append(MoveStored(gs, position_rank,position_file,position_rank+1,position_file-1))
                        TheoreticalMoves = np.append(TheoreticalMoves,MoveStored(gs, position_rank,position_file,position_rank+1,position_file-1))
            if position_file+1 <= 7: #captures to the right
                if int(str(gs.board[position_rank+1][position_file+1])[0]) == 1:
                    if not piecePinned or pinDirection == (1, 1):
                        #TheoreticalMoves.append(MoveStored(gs, position_rank,position_file,position_rank+1,position_file+1))
                        TheoreticalMoves = np.append(TheoreticalMoves,MoveStored(gs, position_rank,position_file,position_rank+1,position_file+1))
        return TheoreticalMoves
def getRookMoves(gs, position_rank, position_file, TheoreticalMoves): #for or while loop
        #check is piece is pinned
        piecePinned = False
        pinDirection = ()
        for i in range(len(gs.pins)-1, -1, -1):
            if gs.pins[i][0] == position_rank and gs.pins[i][1] == position_file:
                piecePinned = True
                pinDirection = (gs.pins[i][2], gs.pins[i][3])
                if int(str(gs.board[position_rank][position_file])[1]) != 5:
                    gs.pins.remove(gs.pins[i])
                break
        up = 1
        down = 1
        left = 1
        right = 1
        while gs.board[position_rank-up][position_file] == 0 and 0 <= position_rank - up <= 7: #up movement
            if not piecePinned or pinDirection == (-1, 0) or pinDirection == (1, 0):
                #TheoreticalMoves.append(MoveStored(gs,position_rank,position_file, position_rank-up,position_file))
                TheoreticalMoves = np.append(TheoreticalMoves,MoveStored(gs,position_rank,position_file, position_rank-up,position_file))
            up += 1  
        if 0 <= position_rank - up <= 7 and int(str(gs.board[position_rank][position_file])[0]) != int(str(gs.board[position_rank-up][position_file])[0]):
            if not piecePinned or pinDirection == (-1, 0) or pinDirection == (1, 0):
                #TheoreticalMoves.append(MoveStored(gs, position_rank,position_file, position_rank-up,position_file))
                TheoreticalMoves = np.append(TheoreticalMoves,MoveStored(gs, position_rank,position_file, position_rank-up,position_file))

        while 0 <= position_rank + down <= 7 and gs.board[position_rank+down][position_file] == 0: #down movement
            if not piecePinned or pinDirection == (-1, 0) or pinDirection == (1, 0):
                #TheoreticalMoves.append(MoveStored(gs,position_rank,position_file, position_rank+down,position_file))
                TheoreticalMoves = np.append(TheoreticalMoves,MoveStored(gs,position_rank,position_file, position_rank+down,position_file))
            down += 1  
        if 0 <= position_rank + down <= 7 and int(str(gs.board[position_rank][position_file])[0]) != int(str(gs.board[position_rank+down][position_file])[0]):
            if not piecePinned or pinDirection == (-1, 0) or pinDirection == (1, 0):
                #TheoreticalMoves.append(MoveStored(gs, position_rank,position_file, position_rank+ down,position_file))
                TheoreticalMoves = np.append(TheoreticalMoves,MoveStored(gs, position_rank,position_file, position_rank+ down,position_file))
        while gs.board[position_rank][position_file-left] == 0 and 0 <= position_file - left <= 7: #left movement
            if not piecePinned or pinDirection == (0, -1) or pinDirection == (0, 1):
                #TheoreticalMoves.append(MoveStored(gs, position_rank,position_file, position_rank,position_file-left))
                TheoreticalMoves = np.append(TheoreticalMoves,MoveStored(gs, position_rank,position_file, position_rank,position_file-left))
            left += 1  
        if 0 <= position_file - left <= 7 and int(str(gs.board[position_rank][position_file])[0]) != int(str(gs.board[position_rank][position_file-left])[0]):
            if not piecePinned or pinDirection == (0, -1) or pinDirection == (0, 1):
                #TheoreticalMoves.append(MoveStored(gs, position_rank,position_file, position_rank,position_file-left))
                TheoreticalMoves = np.append(TheoreticalMoves,MoveStored(gs, position_rank,position_file, position_rank,position_file-left))

        while 0 <= position_file + right <= 7 and gs.board[position_rank][position_file+right] == 0: #right movement
            if not piecePinned or pinDirection == (0, -1) or pinDirection == (0, 1):
                #TheoreticalMoves.append(MoveStored(gs ,position_rank,position_file, position_rank,position_file+right))
                TheoreticalMoves = np.append(TheoreticalMoves,MoveStored(gs ,position_rank,position_file, position_rank,position_file+right))
            right += 1  
        if 0 <= position_file + right <= 7 and int(str(gs.board[position_rank][position_file])[0]) != int(str(gs.board[position_rank][position_file+right])[0]):
            if not piecePinned or pinDirection == (0, -1) or pinDirection == (0, 1):
                #TheoreticalMoves.append(MoveStored(gs, position_rank,position_file, position_rank,position_file+right))
                TheoreticalMoves = np.append(TheoreticalMoves,MoveStored(gs, position_rank,position_file, position_rank,position_file+right))
        return TheoreticalMoves

def getKnightMoves(gs, position_rank, position_file, TheoreticalMoves):
    #check is piece is pinned
    piecePinned = False
    pinDirection = ()
    for i in range(len(gs.pins)-1, -1, -1):
        if gs.pins[i][0] == position_rank and gs.pins[i][1] == position_file:
            piecePinned = True
            gs.pins.remove(gs.pins[i])
            break

    if 7>= position_rank-2 >= 0: #UP
        if 0 <= position_file+1 <= 7: #right
            if int(str(gs.board[position_rank-2][position_file+1])[0]) != int(str(gs.board[position_rank][position_file])[0]):
                if not piecePinned:
                    #TheoreticalMoves.append(MoveStored(gs, position_rank,position_file, position_rank-2,position_file+1))
                    TheoreticalMoves = np.append(TheoreticalMoves,MoveStored(gs, position_rank,position_file, position_rank-2,position_file+1))
        if 0 <= position_file-1 <= 7: #left
            if int(str(gs.board[position_rank-2][position_file-1])[0]) != int(str(gs.board[position_rank][position_file])[0]):
                if not piecePinned:
                    #TheoreticalMoves.append(MoveStored(gs, position_rank,position_file, position_rank-2,position_file-1))
                    TheoreticalMoves = np.append(TheoreticalMoves,MoveStored(gs, position_rank,position_file, position_rank-2,position_file-1))

    if 7>= position_rank+2 >= 0: #DOWN
        if 0<= position_file+1 <= 7: #right
            if int(str(gs.board[position_rank+2][position_file+1])[0]) != int(str(gs.board[position_rank][position_file])[0]):
                if not piecePinned:
                    #TheoreticalMoves.append(MoveStored(gs, position_rank,position_file, position_rank+2,position_file+1))
                    TheoreticalMoves = np.append(TheoreticalMoves,MoveStored(gs, position_rank,position_file, position_rank+2,position_file+1))
        if 0 <= position_file-1 <= 7: #left
            if int(str(gs.board[position_rank+2][position_file-1])[0]) != int(str(gs.board[position_rank][position_file])[0]):
                if not piecePinned:
                    #TheoreticalMoves.append(MoveStored(gs, position_rank,position_file, position_rank+2,position_file-1))
                    TheoreticalMoves = np.append(TheoreticalMoves,MoveStored(gs, position_rank,position_file, position_rank+2,position_file-1))

    if 7>= position_file+2 >= 0: #RIGHT
        if 0 <= position_rank-1 <= 7: #up
            if int(str(gs.board[position_rank-1][position_file+2])[0]) != int(str(gs.board[position_rank][position_file])[0]):
                if not piecePinned:
                    #TheoreticalMoves.append(MoveStored(gs, position_rank,position_file, position_rank-1,position_file+2))
                    TheoreticalMoves = np.append(TheoreticalMoves,MoveStored(gs, position_rank,position_file, position_rank-1,position_file+2))
        if 0 <= position_rank+1 <= 7: #down
            if int(str(gs.board[position_rank+1][position_file+2])[0]) != int(str(gs.board[position_rank][position_file])[0]):
                if not piecePinned:
                    #TheoreticalMoves.append(MoveStored(gs, position_rank,position_file, position_rank+1,position_file+2))
                    TheoreticalMoves = np.append(TheoreticalMoves,MoveStored(gs, position_rank,position_file, position_rank+1,position_file+2))

    if 7>= position_file-2 >= 0: #LEFT
        if 0 <= position_rank-1 <= 7: #up
            if int(str(gs.board[position_rank-1][position_file-2])[0]) != int(str(gs.board[position_rank][position_file])[0]):
                if not piecePinned:
                    #TheoreticalMoves.append(MoveStored(gs, position_rank,position_file, position_rank-1,position_file-2))
                    TheoreticalMoves = np.append(TheoreticalMoves,MoveStored(gs, position_rank,position_file, position_rank-1,position_file-2))
        if 0 <= position_rank+1 <= 7: #down
            if int(str(gs.board[position_rank+1][position_file-2])[0]) != int(str(gs.board[position_rank][position_file])[0]):
                if not piecePinned:
                    #TheoreticalMoves.append(MoveStored(gs, position_rank,position_file, position_rank+1,position_file-2))
                    TheoreticalMoves = np.append(TheoreticalMoves,MoveStored(gs, position_rank,position_file, position_rank+1,position_file-2))
    return TheoreticalMoves

def getBishopMoves(gs, position_rank, position_file, TheoreticalMoves):
    #check is piece is pinned
    piecePinned = False
    pinDirection = ()
    for i in range(len(gs.pins)-1, -1, -1):
        if gs.pins[i][0] == position_rank and gs.pins[i][1] == position_file:
            piecePinned = True
            pinDirection = (gs.pins[i][2], gs.pins[i][3])
            gs.pins.remove(gs.pins[i])
            break
    up = 1
    down = 1
    left = 1
    right = 1
    while 0 <= position_rank - up <= 7 and 0 <= position_file - left <= 7 and gs.board[position_rank-up][position_file-left] == 0: #up+left movement
        if not piecePinned or pinDirection == (-1, -1) or pinDirection == (1, 1):
            #TheoreticalMoves.append(MoveStored(gs, position_rank,position_file, position_rank-up,position_file-left))
            TheoreticalMoves = np.append(TheoreticalMoves,MoveStored(gs, position_rank,position_file, position_rank-up,position_file-left))
        up += 1  
        left += 1
    if 0 <= position_rank - up <= 7 and 0 <= position_file - left <= 7 and int(str(gs.board[position_rank][position_file])[0]) != int(str(gs.board[position_rank-up][position_file-left])[0]):
        if not piecePinned or pinDirection == (-1, -1) or pinDirection == (1, 1):
            #TheoreticalMoves.append(MoveStored(gs, position_rank,position_file, position_rank-up,position_file-left))
            TheoreticalMoves = np.append(TheoreticalMoves,MoveStored(gs, position_rank,position_file, position_rank-up,position_file-left))
    up = 1
    left = 1 

    while 0 <= position_rank - up <= 7 and 0 <= position_file + right <= 7 and gs.board[position_rank-up][position_file+right] == 0: #up+right movement
        if not piecePinned or pinDirection == (1, -1) or pinDirection == (-1, 1):
            #TheoreticalMoves.append(MoveStored(gs, position_rank,position_file, position_rank-up,position_file+right))
            TheoreticalMoves = np.append(TheoreticalMoves,MoveStored(gs, position_rank,position_file, position_rank-up,position_file+right))
        up += 1  
        right += 1
    if 0 <= position_rank - up <= 7 and 0 <= position_file + right <= 7 and int(str(gs.board[position_rank][position_file])[0]) != int(str(gs.board[position_rank-up][position_file+right])[0]):
        if not piecePinned or pinDirection == (1, -1) or pinDirection == (-1, 1):
            #TheoreticalMoves.append(MoveStored(gs, position_rank,position_file, position_rank-up,position_file+right))
            TheoreticalMoves = np.append(TheoreticalMoves,MoveStored(gs, position_rank,position_file, position_rank-up,position_file+right))
    up = 1
    right = 1 

    while 0 <= position_rank + down <= 7 and 0 <= position_file + right <= 7 and gs.board[position_rank+down][position_file+right] == 0: #down+right movement
        if not piecePinned or pinDirection == (-1, -1) or pinDirection == (1, 1):
            #TheoreticalMoves.append(MoveStored(gs ,position_rank,position_file, position_rank+down,position_file+right))
            TheoreticalMoves = np.append(TheoreticalMoves,MoveStored(gs ,position_rank,position_file, position_rank+down,position_file+right))
        down += 1  
        right += 1
    if 0 <= position_rank + down <= 7 and 0 <= position_file + right <= 7 and int(str(gs.board[position_rank][position_file])[0]) != int(str(gs.board[position_rank+down][position_file+right])[0]):
        if not piecePinned or pinDirection == (1, 1) or pinDirection == (-1, -1):
            #TheoreticalMoves.append(MoveStored(gs, position_rank,position_file, position_rank+down,position_file+right))
            TheoreticalMoves = np.append(TheoreticalMoves,MoveStored(gs, position_rank,position_file, position_rank+down,position_file+right))
    down = 1
    right = 1 

    while 0 <= position_rank + down <= 7 and 0 <= position_file - left <= 7 and gs.board[position_rank+down][position_file-left] == 0: #down+left movement
        if not piecePinned or pinDirection == (-1, 1) or pinDirection == (1, -1):
            #TheoreticalMoves.append(MoveStored(gs, position_rank,position_file, position_rank+down,position_file-left))
            TheoreticalMoves = np.append(TheoreticalMoves,MoveStored(gs, position_rank,position_file, position_rank+down,position_file-left))
        down += 1  
        left += 1
    if 0 <= position_rank + down <= 7 and 0 <= position_file - left <= 7 and int(str(gs.board[position_rank][position_file])[0]) != int(str(gs.board[position_rank+down][position_file-left])[0]):
        if not piecePinned or pinDirection == (-1, 1) or pinDirection == (1, -1):
            #TheoreticalMoves.append(MoveStored(gs, position_rank,position_file, position_rank+down,position_file-left))
            TheoreticalMoves = np.append(TheoreticalMoves,MoveStored(gs, position_rank,position_file, position_rank+down,position_file-left))
    down = 1
    left = 1 
    return TheoreticalMoves

def getQueenMoves(gs, position_rank, position_file, TheoreticalMoves): 
    TheoreticalMoves = getRookMoves(gs, position_rank, position_file, TheoreticalMoves)
    TheoreticalMoves = getBishopMoves(gs, position_rank, position_file, TheoreticalMoves) 
    return TheoreticalMoves

def getKingMoves(gs, position_rank, position_file, TheoreticalMoves):
    rankMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
    fileMoves = (-1,  0, 1,-1, 1, -1, 0, 1)
    allyColor = 1 if gs.WhitesTurn else 2
    for i in range(8):
        end_rank = position_rank +rankMoves[i]
        end_file = position_file +fileMoves[i]
        if 0 <= end_rank < 8 and 0 <= end_file < 8:
            endPiece = gs.board[end_rank][end_file]
            #not ally piece
            if int(str(endPiece)[0]) != allyColor:
                if allyColor == 1:
                    gs.whiteKingPosition = (end_rank, end_file)
                else: 
                    gs.blackKingPosition = (end_rank, end_file)
                inCheck, pins, checks = checkForPinsAndChecks(gs)
                if not inCheck:
                    #TheoreticalMoves.append(MoveStored(gs, position_rank,position_file, end_rank, end_file))
                    TheoreticalMoves = np.append(TheoreticalMoves,MoveStored(gs, position_rank,position_file, end_rank, end_file))
                #places king back to original location
                if allyColor == 1:
                    gs.whiteKingPosition = (position_rank, position_file)
                else:
                    gs.blackKingPosition = (position_rank, position_file)
    return TheoreticalMoves
    

class MoveStored():
    def __init__(self, gs, rank_start, file_start, rank_end, file_end, isCastleMove = False):
        self.pieceMoved = gs.board[rank_start][file_start]
        self.pieceTaken = gs.board[rank_end][file_end]
        self.file_start = file_start
        self.file_end = file_end
        self.rank_start = rank_start
        self.rank_end = rank_end
        self.moveID = self.rank_start *1000 + self.file_start * 100 + self.rank_end * 10 + self.file_end
        self.isCastleMove = isCastleMove



    #make it possible to compare generated moves and clicked ones
    def __eq__(self,other):
        if isinstance(other, MoveStored):
            return self.moveID == other.moveID
        return False

        
