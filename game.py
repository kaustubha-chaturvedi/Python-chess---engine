import pygame as p
from const import *

def drawGameState(screen,gs,validMoves,sqSelected):
    drawBoard(screen)
    highlightSquares(screen,gs,validMoves,sqSelected)
    highlightLastMove(screen,gs)
    drawPieces(screen,gs.board)

def drawBoard(screen):
    for r in range(DIMENSION):
        for c in range(DIMENSION):

            color = COLORS['lightBg'] if (r+c)%2==0 else COLORS['darkBg']
            p.draw.rect(surface=screen,color=color,rect=p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))
            if c==0:
                textObject = font.render(str(8-r),1,p.Color(COLORS['lightBg'] if (r+c)%2==1 else COLORS['darkBg']))
                textLocation = (5, 5 + r * SQ_SIZE)
                screen.blit(textObject,textLocation)
            if r==7:
                textObject = font.render(chr(c+97),1,p.Color(COLORS['lightBg'] if (r+c)%2==1 else COLORS['darkBg']))
                textLocation = (c * SQ_SIZE + SQ_SIZE - textObject.get_width()-5, HEIGHT - textObject.get_height() - 5)
                screen.blit(textObject,textLocation)

def highlightSquares(screen,gs,validMoves,sqSelected):
    if sqSelected != ():
        r,c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            s = p.Surface((SQ_SIZE,SQ_SIZE))
            s.set_alpha(100)
            s.fill(COLORS['darkTrace'])
            screen.blit(s,(c*SQ_SIZE,r*SQ_SIZE))
            s.fill(COLORS['lightTrace'])
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s,(move.endCol*SQ_SIZE,move.endRow*SQ_SIZE))

def highlightLastMove(screen,gs):
    if len(gs.moveLog) > 0:
        lastMove = gs.moveLog[-1]
        s = p.Surface((SQ_SIZE,SQ_SIZE))
        s.set_alpha(100)
        s.fill(COLORS['moves'])
        screen.blit(s,(lastMove.endCol*SQ_SIZE,lastMove.endRow*SQ_SIZE))
        s.fill(COLORS['moves'])
        screen.blit(s,(lastMove.startCol*SQ_SIZE,lastMove.startRow*SQ_SIZE))

def drawPieces(screen,board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "<>":
                img_center=c*SQ_SIZE+SQ_SIZE//2,r*SQ_SIZE+SQ_SIZE//2
                screen.blit(IMAGES[piece],IMAGES[piece].get_rect(center=img_center))

def animateMove(move,screen,board,clock):
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 5
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    p.mixer.Sound.play(captureSound) if move.pieceCaptured != "<>" else p.mixer.Sound.play(moveSound)
    for frame in range(frameCount + 1):
        r,c = (move.startRow + dR*frame/frameCount,move.startCol + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen,board)
        color = COLORS['lightBg'] if (move.endRow+move.endCol)%2==0 else COLORS['darkBg']
        img_center=c*SQ_SIZE+SQ_SIZE//2,r*SQ_SIZE+SQ_SIZE//2
        p.draw.rect(screen,color,p.Rect(move.endCol*SQ_SIZE,move.endRow*SQ_SIZE,SQ_SIZE,SQ_SIZE))
        if move.pieceCaptured != "<>":
            screen.blit(IMAGES[move.pieceCaptured],IMAGES[move.pieceCaptured].get_rect(center=img_center))
        if move.pieceMoved != "<>":
            screen.blit(IMAGES[move.pieceMoved],IMAGES[move.pieceMoved].get_rect(center=img_center))
        p.display.flip()
        clock.tick(60)

def darwEndGameText(screen,text):
    global endSound
    if endSound:
        p.mixer.Sound.play(winSound)if 'checkmate' in text else p.mixer.Sound.play(drawSound)
        endSound = False
    textObject = p.font.SysFont('Arial',32,True,False).render(text,1,p.Color("Black"))
    textLocation = p.Rect(0,0,WIDTH,HEIGHT).move(WIDTH/2-textObject.get_width()/2,HEIGHT/2-textObject.get_height()/2)
    screen.blit(textObject,textLocation.move(2,2))
