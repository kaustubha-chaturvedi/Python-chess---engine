from multiprocessing import Process,Queue
import pygame as p,rules,brain
from const import *
from game import *

def main():
    screen = p.display.set_mode((WIDTH,HEIGHT))
    clock = p.time.Clock()
    p.display.set_caption("Chess")
    screen.fill(p.Color(COLORS['lightBg']))
    gs = rules.GameState()
    loadImages()
    running = True
    sqSelected = ()
    validMoves = gs.getValidMoves()
    moveMade = False
    animate = False
    playerClicks = []
    gameOver = False
    playAsWhite = True
    brainThinking = False
    moveUndone = False
    moveFinderProcess = None
    while running:
        humanTurn = (gs.whiteToMove and playAsWhite) or (not gs.whiteToMove and not playAsWhite)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos()
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected == (row,col) or col >=8:
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row,col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2 and humanTurn:
                        move = rules.Move(playerClicks[0],playerClicks[1],gs.board)
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
                if e.key == p.K_z and not gameOver and humanTurn:
                    gs.undoMove()
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False
                    if brainThinking:
                        moveFinderProcess.terminate()
                        brainThinking = False
                    moveUndone = True

                if e.key == p.K_r and gameOver:
                    gs = rules.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
                    if brainThinking:
                        moveFinderProcess.terminate()
                        brainThinking = False
                    moveUndone = True

        if not gameOver and not humanTurn and not moveUndone:
            if not brainThinking:
                brainThinking = True
                returnQueue = Queue()
                move_finder_process = Process(target=brain.makeMove, args=(gs, validMoves, returnQueue))
                move_finder_process.start()

            if not move_finder_process.is_alive():
                autoMove = returnQueue.get()
                if autoMove is None:
                    autoMove = brain.randomMove(validMoves)
                gs.makeMove(autoMove)
                moveMade = True
                animate = True
                brainThinking = False


        if moveMade:
            if animate:animateMove(gs.moveLog[-1],screen,gs.board,clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
            moveUndone = False

        drawGameState(screen,gs,validMoves,sqSelected)
        
        if gs.checkmate or gs.stalemate:
            gameOver = True
            darwEndGameText(screen,"Stalemate" if gs.stalemate else \
                "Black wins by checkmate" if gs.whiteToMove \
             else "White wins by checkmate")
        
        clock.tick(MAX_FPS)
        p.display.flip()


if __name__ == "__main__":
    main()