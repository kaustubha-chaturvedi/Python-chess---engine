import random
from const import *

def randomMove(validMoves):
    return random.choice(validMoves)

def makeMove(gs, validMoves,returnQueue):
    global nextMove
    nextMove = None
    random.shuffle(validMoves)
    negaMaxAB(gs,validMoves,DEPTH,-CHECKMATE,CHECKMATE,1 if gs.whiteToMove else -1)
    returnQueue.put(nextMove) 


def negaMaxAB(gs,validMoves,depth,alpha,beta,turn):
    global nextMove
    if depth==0:
        return turn*eval(gs)
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        score = -negaMaxAB(gs,gs.getValidMoves(),depth-1,-beta,-alpha,-turn)
        if score>maxScore:
            maxScore = score
            if depth == DEPTH: nextMove = move
        gs.undoMove()
        alpha = max(alpha,score)
        if alpha>=beta:
            break
    return maxScore

def eval(gs):
    if gs.checkmate:
        if gs.whiteToMove:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif gs.stalemate:
        return STALEMATE
    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            piece = gs.board[row][col]
            if piece != "<>":
                piecePositionScore = 0
                if piece[1] != "K":
                    piecePositionScore = piecePositionScores[piece][row][col]
                if piece[0] == "w":
                    score += pieceScore[piece[1]] + piecePositionScore
                if piece[0] == "b":
                    score -= pieceScore[piece[1]] + piecePositionScore

    return score