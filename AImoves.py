import backend
import main
import movement
import numpy as np
import random
#efficency improvements
#1. Keep track of all pieces so there is no need to loop all the time

DEPTH = 3


#score for the pieces
#King has a score of 0 since it will be never be captured practically
StrToPieceScore ={"Pawn":1, "Rook":5, "Knight":3, "Bishop":3, "Queen":9, "King":0}
STALEMATE = 0
CHECKMATE = 500
#conversion from pieces names strings into int of pieces
#pawn: 1 Rook: 2 Knight: 3 Bishop: 4 Queen: 5 King: 6
stringsToInt = {"Pawn":1,"Rook":2,"Knight":3,"Bishop":4,"Queen":5,"King":6}
IntToStrings = {v: k for k, v in stringsToInt.items()}

def IntToStringconverter(piece_number):
    return IntToStrings[piece_number]

def PieceNameToPieceScoreconverter(piece_name):
    return StrToPieceScore[piece_name]



#takes all Legal moves and gamestate 
#evaluates legal moves
#select best legal moves and returns it to main
def returnOpponentsMove(gs, LegalMoves):
    global bestMove
    bestMove = None
    #AlphaBeta(gs, DEPTH, LegalMoves, -2000, 2000)
    findMoveNegaMaxAlphaBeta(gs, LegalMoves, DEPTH, -2000, 2000, 1 if gs.WhitesTurn else -1)
    return bestMove


def recursiveSearchTest(gs, DEPTH, FirstIteration, max_Score, LegalMoves):
    breakpoint()
    if not FirstIteration:
        #changes Turn so best possible Move from opponent can be calculated
        gs.WhitesTurn = not gs.WhitesTurn
        #get legal moves for the best move made by the opponent
        LegalMoves = movement.getLegalMoves(gs)
    #recorsion continues as long as  DEPTH is more than zero
    if DEPTH != 0:
        for move in LegalMoves:
            movement.makeMove(gs, move)
            recursiveSearchTest(gs, DEPTH - 1, FirstIteration, max_Score, LegalMoves)
            movement.undoMove(gs)
    #end of DEPTH is reached evaluation of the board
    if DEPTH == 0:
        #changes Color back
        gs.WhitesTurn = not gs.WhitesTurn
        turnMuliplier = 1 if gs.WhitesTurn  else -1
        if gs.checkmate:
            currentScore = CHECKMATE
        #if stalemate is possible score will set to neutral, there move will be only made if own score is worse than 0
        elif gs.stalemate:
            currentScore = STALEMATE
        else:
            #score the current made move
            currentScore = turnMuliplier * returnScore(gs)
        if currentScore > max_Score:
            max_Score = currentScore
            bestMove = move
        return bestMove
        
def TwoLayerSearch(gs,LegalMoves):
    blackMaxScore = -CHECKMATE
    turnMuliplier = 1 if gs.WhitesTurn  else -1
    #black moves
    for move in LegalMoves:
        movement.makeMove(gs, move)
        #important so legal moves from origin are not getting overrided
        #change color so legal moves for the other color can be made
        LegalMovesOpponent = movement.getLegalMoves(gs)
        whiteMaxScore = -CHECKMATE
        #white moves
        for OpponentMove in LegalMovesOpponent:
            turnMuliplier = 1 
            movement.makeMove(gs, OpponentMove)
            #evaluate
            if gs.checkmate:
                currentScore = CHECKMATE
            #if stalemate is possible score will set to neutral, there move will be only made if own score is worse than 0
            elif gs.stalemate:
                currentScore = STALEMATE
            else:
                #score the current made move
                currentScore = turnMuliplier * returnScore(gs)
            if currentScore > whiteMaxScore:
                whiteMaxScore = currentScore
                #I NEED TO USE WHITE BEST MOVE?
                whiteBestMove = OpponentMove
            movement.undoMove(gs)
        #sort all children
        turnMuliplier = -1 
        if blackMaxScore < turnMuliplier *whiteMaxScore:
            blackMaxScore = turnMuliplier *whiteMaxScore
            bestBlackMove = move
        movement.undoMove(gs) 
    return bestBlackMove



def MinMax(gs, DEPTH, LegalMoves):
    #turn multiplier for MinMax
    turnMuliplier = 1 if gs.WhitesTurn  else -1
    #is in the beginning negative so a better MaxMinScore can be found

    #this needs to be fixxed
    MaxMinScore = -CHECKMATE
    #evaluate board
    if DEPTH == 0:
        #positive if white negative if black
        if gs.checkmate:
            currentScore = CHECKMATE * turnMuliplier
        #if stalemate is possible score will set to neutral, there move will be only made if own score is worse than 0
        elif gs.stalemate:
            currentScore = STALEMATE
        else:
            #score the current made move
            currentScore = turnMuliplier * returnScore(gs)
        #sorts highest possible score in current legal moves
        #a good move is positive for white and black all the time
        if currentScore > MaxMinScore:
            MaxMinScore = currentScore
        return MaxMinScore
    #whites layer
    if gs.WhitesTurn:
        MaxScore = -CHECKMATE
        LegalMoves = movement.getLegalMoves(gs)
        for move in LegalMoves:
            movement.makeMove(gs, move)
            Score = turnMuliplier * MinMax(gs, DEPTH-1, LegalMoves)
            if Score > MaxScore:
                MaxScore = Score
                bestMove = move
            movement.undoMove(gs)
        return MaxScore
    #blacks layer
    if not gs.WhitesTurn:
        MinScore = CHECKMATE
        LegalMoves = movement.getLegalMoves(gs)
        for move in LegalMoves:
            movement.makeMove(gs, move)
            #turn Multiplyer needs to be removed
            Score = turnMuliplier * MinMax(gs, DEPTH-1, LegalMoves)
            if Score > MinScore:
                MinScore = Score
                bestMove = move
            movement.undoMove(gs)
        return bestMove


def MinMax2(gs, depth, LegalMoves):
    #breakpoint()
    #using global for best move
    global bestMove
    #turn multiplier for MinMax
    turnMuliplier = 1 #if gs.WhitesTurn  else -1
    #evaluate board
    if depth == 0:
        #positive if white negative if black
        if gs.checkmate:
            currentScore = CHECKMATE * turnMuliplier
        #if stalemate is possible score will set to neutral, there move will be only made if own score is worse than 0
        elif gs.stalemate:
            currentScore = STALEMATE
        else:
            #score the current made move
            currentScore =  turnMuliplier * returnScore(gs)
        #returns score of current node
        return currentScore


    #whites layer
    if gs.WhitesTurn:
        MaxScore = -CHECKMATE
        LegalMoves = movement.getLegalMoves(gs)
        for move in LegalMoves:
            movement.makeMove(gs, move)
            Score = MinMax2(gs, depth-1, LegalMoves)
            if Score > MaxScore:
                MaxScore = Score
                if depth == DEPTH:
                    bestMove = move
            movement.undoMove(gs)
        return MaxScore
    #blacks layer
    if not gs.WhitesTurn:
        MinScore = CHECKMATE
        LegalMoves = movement.getLegalMoves(gs)
        for move in LegalMoves:
            movement.makeMove(gs, move)
            #turn Multiplyer needs to be removed
            Score = MinMax2(gs, depth-1, LegalMoves)
            if Score < MinScore:
                MinScore = Score
                if depth == DEPTH:
                    bestMove = move
            movement.undoMove(gs)
        return  MinScore
#for child in position it should be move in legal moves
#make move and undo move

def findMoveNegaMaxAlphaBeta(gs, LegalMoves, depth, alpha, beta, turnMultiplier):
    global bestMove#, counter
    #counter += 1
    if depth == 0:
        #positive if white negative if black
        if gs.checkmate:
            currentScore = CHECKMATE * turnMultiplier
            print("checkmate2")
        #if stalemate is possible score will set to neutral, there move will be only made if own score is worse than 0
        elif gs.stalemate:
            currentScore = STALEMATE
            print("stalemate2")
        else:
            #score the current made move
            currentScore =  turnMultiplier * returnScore(gs)
        #returns score of current node
        return currentScore
    
    maxScore = -CHECKMATE
    for move in LegalMoves:
        movement.makeMove(gs, move)
        LegalMoves = movement.getLegalMoves(gs)
        score = -findMoveNegaMaxAlphaBeta(gs, LegalMoves, depth-1,-beta, -alpha, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                bestMove = move
        movement.undoMove(gs)
        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore

def AlphaBeta(gs, depth, LegalMoves, alpha, beta):
    #breakpoint()
    #using global for best move
    global bestMove
    #turn multiplier for MinMax
    turnMuliplier = 1 #if gs.WhitesTurn  else -1
    #evaluate board
    if depth == 0:
        #positive if white negative if black
        if gs.checkmate:
            currentScore = CHECKMATE * turnMuliplier
            print("checkmate2")
        #if stalemate is possible score will set to neutral, there move will be only made if own score is worse than 0
        elif gs.stalemate:
            currentScore = STALEMATE
            print("stalemate2")
        else:
            #score the current made move
            currentScore =  turnMuliplier * returnScore(gs)
        #returns score of current node
        return currentScore


    #whites layer
    if gs.WhitesTurn:
        MaxScore = -CHECKMATE
        LegalMoves = movement.getLegalMoves(gs)
        for move in LegalMoves:
            movement.makeMove(gs, move)
            if depth <2 :
                #add in check here
                movement.CheckmateandStalemate(gs, LegalMoves)
            Score = AlphaBeta(gs, depth-1, LegalMoves, beta, alpha)
            if Score >= MaxScore:
                MaxScore = Score
                if depth == DEPTH:
                    bestMove = move
            movement.undoMove(gs)
            if MaxScore > alpha:
                alpha = MaxScore
            if alpha >= beta:
                break

        return MaxScore
    #blacks layer
    if not gs.WhitesTurn:
        MinScore = CHECKMATE
        LegalMoves = movement.getLegalMoves(gs)
        for move in LegalMoves:
            movement.makeMove(gs, move)
            if depth <2:
                #add in check here
                movement.CheckmateandStalemate(gs, LegalMoves)
            #turn Multiplyer needs to be removed
            Score = AlphaBeta(gs, depth-1, LegalMoves, beta, alpha)
            if Score <= MinScore:
                MinScore = Score
                if depth == DEPTH:
                    bestMove = move
            movement.undoMove(gs)
            if MinScore > alpha:
                alpha = MinScore
            if alpha >= beta:
                break

        return  MinScore
#for child in position it should be move in legal moves
#make move and undo move






#return score of current gameboard
#white wants a positive score, black wants a negative score
def returnScore(gs):
    score = 0
    white_score = 0
    black_score = 0
    POSITION_WEIGHT = 0.1
    #evaluate the board
    for rank in range(8):
        for file in range(8):
            #white pieces
            if int(str(gs.board[rank][file])[0]) == 1:
                piece_name = IntToStringconverter(int(str(gs.board[rank][file])[1]))
                piece_score = PieceNameToPieceScoreconverter(piece_name)
                #position
                if piece_name == "Pawn":
                    position_score = whitePawnMap[rank][file]
                if piece_name == "Rook":
                    position_score = whiteRookMap[rank][file]
                if piece_name == "Knight":
                    position_score = whiteKnightMap[rank][file]
                if piece_name == "Bishop":
                    position_score = whiteBishopMap[rank][file]
                if piece_name == "Queen":
                    position_score = whiteQueenMap[rank][file]
                if piece_name == "King":
                    position_score = whiteKingMap[rank][file]
                white_score = white_score + piece_score + position_score * POSITION_WEIGHT
            #black pieces
            elif int(str(gs.board[rank][file])[0]) == 2:
                piece_name = IntToStringconverter(int(str(gs.board[rank][file])[1]))
                piece_score = PieceNameToPieceScoreconverter(piece_name)
                #position
                if piece_name == "Pawn":
                    position_score = blackPawnMap[rank][file]
                if piece_name == "Rook":
                    position_score = blackRookMap[rank][file]
                if piece_name == "Knight":
                    position_score = blackKnightMap[rank][file]
                if piece_name == "Bishop":
                    position_score = blackBishopMap[rank][file]
                if piece_name == "Queen":
                    position_score = blackQueenMap[rank][file]
                if piece_name == "King":
                    position_score = blackKingMap[rank][file]
                black_score = black_score + piece_score  + position_score * POSITION_WEIGHT
    score = white_score - black_score
    return score


#scoring Maps
#Pawn want to advance and also protect King Side
blackPawnMap =np.array  ([[0,  0,  0,  0,  0,  0,  0,  0 ],
                        [1,  0,  1,  0,  0,  1,  0,  1 ],
                        [1,  2,  1,  1,  1,  1,  2,  1 ],
                        [3,  3,  3,  4,  4,  3,  3,  3 ],
                        [5,  5,  5,  6,  6,  5,  5,  5 ],
                        [7,  7,  7,  7,  7,  7,  7,  7 ],
                        [9,  9,  9,  9,  9,  9,  9,  9 ],
                        [3,  3,  3,  3,  3,  3,  3,  3 ]])


whitePawnMap =np.array([[3,  3,  3,  3,  3,  3,  3,  3 ],
                    [9,  9,  9,  9,  9,  9,  9,  9 ],
                    [7,  7,  7,  7,  7,  7,  7,  7 ],
                    [5,  5,  5,  6,  6,  5,  5,  5 ],
                    [3,  3,  3,  4,  4,  3,  3,  3 ],
                    [1,  2,  1,  1,  1,  1,  2,  1 ],
                    [1,  0,  1,  0,  0,  1,  0,  1 ],
                    [0,  0,  0,  0,  0,  0,  0,  0 ]])

blackRookMap =np.array([[0,  0,  0,  2,  1,  4,  0,  0 ],
                        [2,  2,  2,  2,  2,  2,  2,  2 ],
                        [0,  0,  0,  0,  0,  0,  0,  0 ],
                        [0,  0,  0,  0,  0,  0,  0,  0 ],
                        [0,  0,  0,  0,  0,  0,  0,  0 ],
                        [0,  0,  0,  0,  0,  0,  0,  0 ],
                        [5,  5,  5,  5,  5,  5,  5,  5 ],
                        [2,  2,  2,  2,  2,  2,  2,  2 ]])

whiteRookMap =np.array([[2,  2,  2,  2,  2,  2,  2,  2 ],
                        [5,  5,  5,  5,  5,  5,  5,  5 ],
                        [0,  0,  0,  0,  0,  0,  0,  0 ],
                        [0,  0,  0,  0,  0,  0,  0,  0 ],
                        [0,  0,  0,  0,  0,  0,  0,  0 ],
                        [0,  0,  0,  0,  0,  0,  0,  0 ],
                        [2,  2,  2,  2,  2,  2,  2,  2 ],
                        [0,  0,  0,  2,  1,  4,  0,  0 ]])

blackKnightMap=np.array([[0,  0,  0,  0,  0,  0,  0,  0 ],
                         [1,  1,  1,  1,  1,  1,  1,  1 ],
                         [1,  2,  2,  2,  2,  2,  2,  1 ],
                         [1,  2,  3,  3,  3,  3,  2,  1 ],
                         [1,  2,  3,  3,  3,  3,  2,  1 ],
                         [1,  2,  2,  2,  2,  2,  2,  1 ],
                         [1,  1,  1,  1,  1,  1,  1,  1 ],
                         [0,  0,  0,  0,  0,  0,  0,  0 ]])

whiteKnightMap=np.array([[0,  0,  0,  0,  0,  0,  0,  0 ],
                         [1,  1,  1,  1,  1,  1,  1,  1 ],
                         [1,  2,  2,  2,  2,  2,  2,  1 ],
                         [1,  2,  3,  3,  3,  3,  2,  1 ],
                         [1,  2,  3,  3,  3,  3,  2,  1 ],
                         [1,  2,  2,  2,  2,  2,  2,  1 ],
                         [1,  1,  1,  1,  1,  1,  1,  1 ],
                         [0,  0,  0,  0,  0,  0,  0,  0 ]])


blackBishopMap =np.array([[0,  0,  0,  0,  0,  0,  0,  0 ],
                        [0,  0,  0,  1,  1,  0,  0,  0 ],
                        [2,  1,  1,  2,  2,  1,  1,  2 ],
                        [1,  1,  5,  3,  3,  5,  1,  1 ],
                        [1,  4,  3,  3,  3,  3,  4,  1 ],
                        [4,  2,  2,  2,  2,  2,  2,  4 ],
                        [1,  1,  1,  1,  1,  1,  1,  1 ],
                        [1,  1,  1,  1,  1,  1,  1,  1 ]])


whiteBishopMap =  np.array([[1,  1,  1,  1,  1,  1,  1,  1 ],
                            [1,  1,  1,  1,  1,  1,  1,  1 ],
                            [4,  2,  2,  2,  2,  2,  2,  4 ],
                            [1,  4,  3,  3,  3,  3,  4,  1 ],
                            [1,  1,  5,  3,  3,  5,  1,  1 ],
                            [2,  1,  1,  2,  2,  1,  1,  2 ],
                            [0,  0,  0,  1,  1,  0,  0,  0 ],
                            [0,  0,  0,  0,  0,  0,  0,  0 ]])


blackQueenMap=np.array([[0,  0,  0,  0,  0,  0,  0,  0 ],
                        [1,  1,  1,  1,  1,  1,  1,  1 ],
                        [2,  1,  1,  2,  2,  1,  1,  2 ],
                        [1,  1,  5,  3,  3,  5,  1,  1 ],
                        [1,  4,  3,  3,  3,  3,  4,  1 ],
                        [4,  2,  2,  2,  2,  2,  2,  4 ],
                        [5,  5,  5,  5,  5,  5,  5,  5 ],
                        [3,  3,  3,  3,  3,  3,  3,  3 ]])


whiteQueenMap=np.array([[3,  3,  3,  3,  3,  3,  3,  3 ],
                        [5,  5,  5,  5,  5,  5,  5,  5 ],
                        [4,  2,  2,  2,  2,  2,  2,  4 ],
                        [1,  4,  3,  3,  3,  3,  4,  1 ],
                        [1,  1,  5,  3,  3,  5,  1,  1 ],
                        [2,  1,  1,  2,  2,  1,  1,  2 ],
                        [1,  1,  1,  1,  1,  1,  1,  1 ],
                        [0,  0,  0,  0,  0,  0,  0,  0 ]])


blackKingMap =np.array([[1,  0,  3,  0,  0,  2,  4,  2 ],
                        [0,  1,  0,  0,  0,  1,  1,  1 ],
                        [0,  0,  0,  0,  0,  0,  0,  0 ],
                        [0,  0,  0,  0,  0,  0,  0,  0 ],
                        [0,  0,  0,  0,  0,  0,  0,  0 ],
                        [0,  0,  0,  0,  0,  0,  0,  0 ],
                        [0,  0,  0,  0,  0,  0,  0,  0 ],
                        [0,  0,  0,  0,  0,  0,  0,  0 ]])


whiteKingMap =np.array([[0,  0,  0,  0,  0,  0,  0,  0 ],
                        [0,  0,  0,  0,  0,  0,  0,  0 ],
                        [0,  0,  0,  0,  0,  0,  0,  0 ],
                        [0,  0,  0,  0,  0,  0,  0,  0 ],
                        [0,  0,  0,  0,  0,  0,  0,  0 ],
                        [0,  0,  0,  0,  0,  0,  0,  0 ],
                        [0,  1,  0,  0,  0,  1,  1,  1 ],
                        [1,  0,  3,  0,  0,  2,  4,  2 ]])





def getRandomMove(gs, LegalMoves):
    a = 0
    #no moves possible
    if len(LegalMoves) == 0:
        return None
    elif len(LegalMoves) == 1:
        return LegalMoves[0]
    if len(LegalMoves) > a:   
        while a<3:
            if len(LegalMoves) > a:
                a = a+1
            if len(LegalMoves) > 0:
                randomNumber = random.randrange(0, len(LegalMoves)-1)
                #move = LegalMoves[randomNumber]
                move = LegalMoves[a]
                movement.makeMove(gs, move)
                #movement.undoMove(gs)
                return LegalMoves[randomNumber]

    

def getRandomMove2(gs, LegalMoves):
    if len(LegalMoves) > 1:
        randomNumber = random.randrange(0, len(LegalMoves)-1)
        movement.makeMove(gs, LegalMoves[randomNumber])
        movement.undoMove(gs)
        return LegalMoves[randomNumber]
    #no moves possible
    elif len(LegalMoves) == 0:
        return None
    # just one move is possible
    else:
        return LegalMoves[0]


    


def evaluatePieces():
    pass



def evaluatePosition():
    pass


