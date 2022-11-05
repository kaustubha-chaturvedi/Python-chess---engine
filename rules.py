class GameState():
    def __init__(self):
        self.board=[
            ["bR","bN","bB","bQ","bK","bB","bN","bR"],
            ["bP","bP","bP","bP","bP","bP","bP","bP"],
            ["<>","<>","<>","<>","<>","<>","<>","<>"],
            ["<>","<>","<>","<>","<>","<>","<>","<>"],
            ["<>","<>","<>","<>","<>","<>","<>","<>"],
            ["<>","<>","<>","<>","<>","<>","<>","<>"],
            ["wP","wP","wP","wP","wP","wP","wP","wP"],
            ["wR","wN","wB","wQ","wK","wB","wN","wR"]
        ]
        self.whiteToMove=True
        self.moveLog=[]
        self.checkmate=False
        self.stalemate=False
        self.moveFunctions = {
            "P":self.getPawnMoves,"R":self.getRookMoves,
            "N":self.getKnightMoves,"B":self.getBishopMoves,
            "Q":self.getQueenMoves,"K":self.getKingMoves
        }
        self.whiteKingLocation=(7,4)
        self.blackKingLocation=(0,4)
        self.inCheck=False
        self.pins=[]
        self.checks=[]
        self.enpassantPossible = ()
        self.enpassantPossibleLog = [self.enpassantPossible]
        self.currentCastlingRight = CastleRights(True,True,True,True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks,
                                self.currentCastlingRight.bks,self.currentCastlingRight.wqs,
                                self.currentCastlingRight.bqs)]

    def makeMove(self,move):
        self.board[move.startRow][move.startCol] = "<>"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.startRow,move.startCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.startRow,move.startCol)
        
        if move.promotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "Q"
        
        if move.enpassant:
            self.board[move.startRow][move.endCol] = "<>"

        if move.pieceMoved[1] == "P" and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.startRow+move.endRow)//2,move.startCol)
        else:
            self.enpassantPossible = ()
        
        if move.castle:
            if move.endCol - move.startCol == 2:
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1]
                self.board[move.endRow][move.endCol+1] = "<>"
            else:
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2]
                self.board[move.endRow][move.endCol-2] = "<>"

        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks,
                                self.currentCastlingRight.bks,self.currentCastlingRight.wqs,
                                self.currentCastlingRight.bqs))
        self.enpassantPossibleLog.append(self.enpassantPossible)
   
    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.endRow,move.endCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.endRow,move.endCol)
            if move.enpassant:
                self.board[move.endRow][move.endCol] = "<>"
                self.board[move.startRow][move.endCol] = move.pieceCaptured
            
            self.enpassantPossibleLog.pop()
            self.enpassantPossible = self.enpassantPossibleLog[-1]
            self.castleRightsLog.pop()  
            self.currentCastlingRight = CastleRights(self.castleRightsLog[-1].wks,
                                self.castleRightsLog[-1].bks,self.castleRightsLog[-1].wqs,
                                self.castleRightsLog[-1].bqs)

            if move.castle:
                if move.endCol - move.startCol == 2:
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = "<>"
                else:
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol+1] = "<>"
            
            self.checkmate = False
            self.stalemate = False
    
    def getValidMoves(self):
        moves = []
        self.inCheck,self.pins,self.checks = self.checkForPinsAndChecks()
        kingRow = self.whiteKingLocation[0] if self.whiteToMove else self.blackKingLocation[0]
        kingCol = self.whiteKingLocation[1] if self.whiteToMove else self.blackKingLocation[1]
        if self.inCheck:
            if len(self.checks) == 1:
                moves = self.getAllPossibleMoves()
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []
                if pieceChecking[1] == "N":
                    validSquares = [(checkRow,checkCol)]
                else:
                    for i in range(1,8):
                        validSquare = (kingRow + check[2]*i,kingCol + check[3]*i)
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break
                for i in range(len(moves)-1,-1,-1):
                    if moves[i].pieceMoved[1] != "K":
                        if not (moves[i].endRow,moves[i].endCol) in validSquares:
                            moves.remove(moves[i])
            else:
                self.getKingMoves(kingRow,kingCol,moves)
        else:
            moves = self.getAllPossibleMoves()
        self.getCastleMoves(kingRow,kingCol,moves)

        if len(moves) == 0:
            if self.inCheck:
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        return moves 
    
    def getAllPossibleMoves(self):
        moves = []
        for r in range(8):
            for c in range(8):
                turn = self.board[r][c][0]
                if (turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r,c,moves)
        return moves

    def getPawnMoves(self, row, col, moves):
        piecePinned = False
        pin = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pin = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        moveTurn = -1 if self.whiteToMove else 1
        startRow = 6 if self.whiteToMove else 1
        enemy = "b" if self.whiteToMove else "w"
        kingRow, kingCol = self.whiteKingLocation if self.whiteToMove else self.blackKingLocation

        if self.board[row + moveTurn][col] == "<>":  # 1 square pawn advance
            if not piecePinned or pin == (moveTurn, 0):
                moves.append(Move((row, col), (row + moveTurn, col), self.board))
                if row == startRow and self.board[row + 2 * moveTurn][col] == "<>":  # 2 square pawn advance
                    moves.append(Move((row, col), (row + 2 * moveTurn, col), self.board))
        if col - 1 >= 0:  # capture to the left
            if not piecePinned or pin == (moveTurn, -1):
                if self.board[row + moveTurn][col - 1][0] == enemy:
                    moves.append(Move((row, col), (row + moveTurn, col - 1), self.board))
                if (row + moveTurn, col - 1) == self.enpassantPossible:
                    attack = block = False
                    if kingRow == row:  # king is left of the pawn
                        rangeLeft = range(kingCol + 1, col - 1) if kingCol < col else range(kingCol - 1, col, -1)
                        rangeRight = range(col + 1, 8) if kingCol < col else range(col - 2, -1, -1)
                        for i in rangeLeft:
                            if self.board[row][i] != "<>":
                                block = True
                        for i in rangeRight:
                            square = self.board[row][i]
                            if square[0] == enemy and (square[1] == "R" or square[1] == "Q"):
                                attack = True
                            elif square != "<>":
                                block = True
                    if not attack or block:
                        moves.append(Move((row, col), (row + moveTurn, col - 1), self.board, enpassant=True))
        if col + 1 <= 7:  # capture to the right
            if not piecePinned or pin == (moveTurn, +1):
                if self.board[row + moveTurn][col + 1][0] == enemy:
                    moves.append(Move((row, col), (row + moveTurn, col + 1), self.board))
                if (row + moveTurn, col + 1) == self.enpassantPossible:
                    attack = block = False
                    if kingRow == row:
                        rangeLeft = range(kingCol + 1, col) if kingCol < col else range(kingCol - 1, col + 1, -1)
                        rangeRight = range(col + 2, 8) if kingCol < col else range(col - 1, -1, -1)
                        for i in rangeLeft:
                            if self.board[row][i] != "<>":
                                block = True
                        for i in rangeRight:
                            square = self.board[row][i]
                            if square[0] == enemy and (square[1] == "R" or square[1] == "Q"):
                                attack = True
                            elif square != "<>":
                                block = True
                    if not attack or block:
                        moves.append(Move((row, col), (row + moveTurn, col + 1), self.board, enpassant=True))

    def getRookMoves(self,r,c,moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2],self.pins[i][3])
                if self.board[r][c][1] != "Q":
                    self.pins.remove(self.pins[i])
                break
        directions = ((-1,0),(0,-1),(1,0),(0,1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1,8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0],-d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "<>":
                            moves.append(Move((r,c),(endRow,endCol),self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r,c),(endRow,endCol),self.board))
                            break
                        else:
                            break
                else:
                    break

    def updateCastleRights(self,move):
        if move.pieceCaptured == "wR":
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.wks = False
        elif move.pieceCaptured == "bR":
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.bks = False

        if move.pieceMoved == "wK":
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == "bK":
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.bks = False

    def getBishopMoves(self,r,c,moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2],self.pins[i][3])
                if self.board[r][c][1] != "Q":
                    self.pins.remove(self.pins[i])
                break
        direction = ((-1,-1),(-1,1),(1,-1),(1,1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in direction:
            for i in range(1,8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0],-d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "<>":
                            moves.append(Move((r,c),(endRow,endCol),self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r,c),(endRow,endCol),self.board))
                            break
                        else:
                            break
                else:
                    break

    def getKnightMoves(self,r,c,moves):
        piecePinned = False
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break
        kM=[(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]
        for m in kM:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != self.board[r][c][0]:
                        moves.append(Move((r,c),(endRow,endCol),self.board))

    def getQueenMoves(self,r,c,moves):
        self.getBishopMoves(r,c,moves)
        self.getRookMoves(r,c,moves)

    def squareUnderAttack(self,r,c):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False

    def getKingMoves(self,r,c,moves):
        rowM = (-1,-1,-1,0,0,1,1,1)
        colM = (-1,0,1,-1,1,-1,0,1)
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + rowM[i]
            endCol = c + colM[i]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    if allyColor == "w":
                        self.whiteKingLocation = (endRow,endCol)
                    else:
                        self.blackKingLocation = (endRow,endCol)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                    if allyColor == "w":
                        self.whiteKingLocation = (r,c)
                    else:
                        self.blackKingLocation = (r,c)
    
    def getCastleMoves(self,r,c,moves):
        if self.squareUnderAttack(r,c):
            return
        if (self.whiteToMove and self.currentCastlingRight.wks) or \
            (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r,c,moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or \
            (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(r,c,moves)

    def getKingsideCastleMoves(self,r,c,moves):
        if self.board[r][c+1] == "<>" and self.board[r][c+2] == "<>":
            if not self.squareUnderAttack(r,c+1) and not self.squareUnderAttack(r,c+2):
                moves.append(Move((r,c),(r,c+2),self.board,castle=True))
    
    def getQueensideCastleMoves(self,r,c,moves):
        if self.board[r][c-1] == "<>" and self.board[r][c-2] == "<>" and self.board[r][c-3] == "<>":
            if not self.squareUnderAttack(r,c-1) and not self.squareUnderAttack(r,c-2):
                moves.append(Move((r,c),(r,c-2),self.board,castle=True))

    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        inCheck = False
        enemyColor = "b" if self.whiteToMove else "w"
        allyColor = "w" if self.whiteToMove else "b"
        startRow = self.whiteKingLocation[0] if self.whiteToMove else self.blackKingLocation[0]
        startCol = self.whiteKingLocation[1] if self.whiteToMove else self.blackKingLocation[1]
        #check outward from king for pins and checks, keep track of pins
        directions = ((-1,0),(0,-1),(1,0),(0,1),(-1,-1),(-1,1),(1,-1),(1,1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()
            for i in range(1,8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != "K":
                        if possiblePin == ():
                            possiblePin = (endRow,endCol,d[0],d[1])
                        else:
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        if (0 <= j <= 3 and type == "R") \
                            or (4 <= j <= 7 and type == "B") \
                            or (type == "Q") or (i == 1 and type == "K") \
                            or (type == "P" and ((enemyColor == "w" and 6 <= j <= 7) \
                            or (enemyColor == "b" and 4 <= j <= 5))) :

                            if possiblePin == ():
                                inCheck = True
                                checks.append((endRow,endCol,d[0],d[1]))
                                break
                            else:
                                pins.append(possiblePin)
                                break
                        else:
                            break
                else:
                    break
        #check for knight checks
        kM=[(-1,-2),(-2,-1),(-2,1),(-1,2),(1,-2),(2,-1),(2,1),(1,2)]
        for m in kM:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == "N":
                    inCheck = True
                    checks.append((endRow,endCol,m[0],m[1]))
        #pawn checks
        pM=[(-1,-1),(-1,1)] if enemyColor == "b" else [(1,-1),(1,1)]
        for m in pM:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == "P":
                    inCheck = True
                    checks.append((endRow,endCol,m[0],m[1]))
        return inCheck, pins, checks
   
class Move():
    pieceToMove = {
                    "wP":"P","wR":"R","wN":"N","wB":"B","wK":"K","wQ":"Q",
                    "bP":"P","bR":"r","bN":"n","bB":"b","bK":"k","bQ":"q"
                    }
    rowsToRanks = {7:'1',6:'2',5:'3',4:'4',3:'5',2:'6',1:'7',0:'8'}
    colsToFiles = {0:'a',1:'b', 2:'c',3:'d',4:'e',5:'f',6:'g',7:'h'}

    def __init__(self,startSq,endSq,board,enpassant=False,castle=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.promotion = (self.pieceMoved == "wP" and self.endRow == 0) or \
                                (self.pieceMoved == "bP" and self.endRow == 7)
        self.enpassant = enpassant
        self.castle = castle
        if self.enpassant:
            self.pieceCaptured = "wP" if self.pieceMoved == "bP" else "bP"        
        self.moveID = self.startRow*1000+self.startCol*100+self.endRow*10+self.endCol

    def __eq__(self,other):
        if isinstance(other,Move):
            return self.moveID == other.moveID    
        return False
            
    def getRankFile(self,r,c):
        return self.colsToFiles[c]+self.rowsToRanks[r]

    def __str__(self):
        if self.castle:
            return "O-O" if self.endCol == 6 else "O-O-O"
        endSquare = self.getRankFile(self.endRow,self.endCol)
        if self.pieceCaptured != "<>":
            if self.pieceMoved[1] == "P":
                return self.colsToFiles[self.startCol]+"X"+endSquare
            return (self.pieceMoved[1] if self.pieceMoved[0]=="w" else self.pieceMoved[1].lower())+"X"+endSquare
        else:
            if self.pieceMoved[1] == "P":
                return endSquare
            return (self.pieceMoved[1] if self.pieceMoved[0]=="w" else self.pieceMoved[1].lower())+endSquare
        
    

class CastleRights():
    def __init__(self,wks,bks,wqs,bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs
    