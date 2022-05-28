import numpy as np



class gameBoard():
    def __init__(self):
        #pieces notation white: 1 black:2
        #pawn: 1 Rook: 2 Knight: 3 Bishop: 4 Queen: 5 King: 6
        #0 = empty
        self.board = np.array([[22, 23, 24, 25, 26, 24, 23, 22],
                               [21, 21, 21, 21, 21, 21, 21, 21],
                               [0,  0,  0,  0,  0,  0,  0,  0 ],
                               [0,  0,  0,  0,  0,  0,  0,  0 ],
                               [0,  0,  0,  0,  0,  0,  0,  0 ],
                               [0,  0,  0,  0,  0,  0,  0,  0 ],
                               [11, 11, 11, 11, 11, 11, 11, 11],
                               [12, 13, 14, 15, 16, 14, 13, 12]])

        self.board3 = np.array([[22, 0, 0, 0, 26, 0, 0, 22],
                               [0, 0, 0, 0, 0, 0, 0, 0],
                               [0,  0,  0,  0,  0,  0,  0,  0 ],
                               [0,  0,  0,  0,  0,  0,  0,  0 ],
                               [0,  0,  0,  0,  0,  0,  0,  0 ],
                               [0,  0,  0,  0,  0,  0,  0,  0 ],
                               [0, 0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 16, 0, 0, 0]])

        self.WhitesTurn = True
        self.MoveLog = np.array([])
        #self.MoveLog = []
        self.whiteKingPosition = (7, 4)
        self.blackKingPosition = (0, 4)
        self.checkmate = False
        self.stalemate = False
        self.inCheck = False
        self.pins = []
        self.checks = [] #pieces which put the king in check
        self.currentCastleRights = CastleRights(True, True, True, True)
        #annotation bqs: Black queen side bks: black king side wqs: white queen side wks: white king side
        #stores the castle rights for undoing a move
        self.CastleRightsLog = [CastleRights(self.currentCastleRights.bqs, self.currentCastleRights.bks,
                                            self.currentCastleRights.wqs, self.currentCastleRights.wks)]



#class for storing the castle rights
class CastleRights():
    def __init__(self, bqs, bks, wqs, wks):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs