import random  # for generating random numbers
import sys  # We will use sys.exit to exit the program
import pygame
from pygame.locals import *  # basic import statement for pygame

# Global variable for the game
FPS = 32
SCREENWIDTH = 289
SCREENHEIGHT = 511
'''
Pygame represents images as Surface objects. The display.set_mode() function creates a new Surface object that represents the actual displayed graphics. 
Any drawing you do to this Surface will become visible on the monitor.
'''
SCREEN = pygame.display.set_mode(
    (SCREENWIDTH, SCREENHEIGHT))  # initialize screen or window for display
GROUNDY = SCREENHEIGHT * 0.8  # base of the screen which will be displayed
GAME_SPRITES = {}  # place all sprites here which we are gonna use in game
GAME_SOUNDS = {}  # place all sounds here which we are gonna use in game
PLAYER = 'gallery/sprites/bird.png'
BACKGROUND = 'gallery/sprites/background.png'
PIPE = 'gallery/sprites/pipe.png'


def welcomeScreen():
    '''
    Shows welcome image on screen
    '''
    playerx = int(SCREENWIDTH/5)
    playery = int((SCREENHEIGHT-GAME_SPRITES['player'].get_height())/2)
    messagex = int((SCREENWIDTH-GAME_SPRITES['message'].get_width())/2)
    messagey = int(0)
    basex = 0
    while True:
        for event in pygame.event.get():
            # if user clicks on close button, close the game
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            # if user press space or up key, start the game
            elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                return

            else:
                SCREEN.blit(GAME_SPRITES['background'], (0, 0))
                SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))
                SCREEN.blit(GAME_SPRITES['message'], (messagex, messagey))
                SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))
                pygame.display.update()
                FPSCLOCK.tick(FPS)


def mainGame():
    playerx = int(SCREENWIDTH/5)
    playery = int(SCREENHEIGHT/2)
    basex = 0
    score = 0  # score variable to keep track of the score of player

    # create two new pipe coordinate for bliting
    # get a pair of pipe with random position
    newPipe1 = getRandomPipe()  
    # get another pipe with random position but different than last one
    newPipe2 = getRandomPipe()

    # list of upper pipes
    upperPipes = [
        {'x': SCREENWIDTH+200, 'y': newPipe1[0]['y']},
        {'x': SCREENWIDTH+200+(SCREENWIDTH/2), 'y': newPipe2[0]['y']}
    ]
    # list of lower pipes
    lowerPipes = [
        {'x': SCREENWIDTH+200, 'y': newPipe1[1]['y']},
        {'x': SCREENWIDTH+200+(SCREENWIDTH/2), 'y': newPipe2[1]['y']}
    ]

    pipeVelX = -4  # velocity of pipe with which they will come to left of the screen

    playerVelY = -9  # velocity to make player fall
    playerMaxVelY = 10  # maximum velocity that player can reach
    playerMinVelY = -8  # minimum velocity that player can reach
    playerAccY = 1  #

    playerFlapAccv = -8  # velocity while flapping
    playerFlapped = False  # it is true only when bird is flapping

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery > 0:
                    playerVelY = playerFlapAccv
                    playerFlapped = True
                    print(playerVelY)
                GAME_SOUNDS['wing'].play()

        # this will return True if player is crashed
        crashTest = isCollide(playerx, playery, upperPipes, lowerPipes)
        if crashTest:
            return

        # check for score
        playerMidPos = playerx + GAME_SPRITES['player'].get_width()/2
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + GAME_SPRITES['pipes'][0].get_width()/2
            if pipeMidPos <= playerMidPos < pipeMidPos+4: # range in which player score will increase by one and pipeMidPos == playerMidPos is not working issue not known currently
                score += 1
                print(f'Your score is {score}')
                GAME_SOUNDS['point'].play()

        if playerVelY < playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY

        if playerFlapped:
            playerFlapped = False
        playerHeight = GAME_SPRITES['player'].get_height()
        playery = playery + min(playerVelY, GROUNDY-playerHeight-playery)

        # moving pipes to left position
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            upperPipe['x'] += pipeVelX
            lowerPipe['x'] += pipeVelX
        # add a new pipe when first one is about to go out of screen
        if 0 < upperPipes[0]['x'] < 5:
            newPipe = getRandomPipe() # now we will get a pipe which will have distance of x=10 from last pipe
            upperPipes.append(newPipe[0])
            lowerPipes.append(newPipe[1]) 
        # if pipe is out of screen remove it
        if upperPipes[0]['x'] < - (GAME_SPRITES['pipes'][0].get_width()):
            upperPipes.pop(0)
            lowerPipes.pop(0)

        # lets blit our sprites on screen
        SCREEN.blit(GAME_SPRITES['background'], (0, 0))
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(GAME_SPRITES['pipes'][0],
                        (upperPipe['x'], upperPipe['y']))
            SCREEN.blit(GAME_SPRITES['pipes'][1],
                        (lowerPipe['x'], lowerPipe['y']))

        SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))
        SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))
        myDigits = [int(x) for x in str(score)]
        width = 0
        for digit in myDigits:
            width += GAME_SPRITES['numbers'][digit].get_width()
        XoffSet = (SCREENWIDTH-width)/2
        for digit in myDigits:
            SCREEN.blit(GAME_SPRITES['numbers'][digit],
                        (XoffSet, SCREENHEIGHT*0.12))
            XoffSet += GAME_SPRITES['numbers'][digit].get_width()

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def isCollide(playerx, playery, upperPipes, lowerPipes):
    if playery < 0 or playery >= GROUNDY - 50:
        GAME_SOUNDS['hit'].play()
        return True

    for pipe in upperPipes:
        pipeHeight = GAME_SPRITES['pipes'][0].get_height()
        if playery < pipeHeight + pipe['y'] and (abs(playerx-pipe['x']) < GAME_SPRITES['pipes'][0].get_width()):
            GAME_SOUNDS['hit'].play()
            return True

    for pipe in lowerPipes:
        if playery + GAME_SPRITES['player'].get_height() > pipe['y'] and (abs(playerx-pipe['x']) < GAME_SPRITES['pipes'][0].get_width()):
            GAME_SOUNDS['hit'].play()
            return True
    return False


def getRandomPipe():
    pipex = SCREENWIDTH + 10
    offset = int(SCREENHEIGHT/3)
    # to generate lower pipe such that it will always remain offest height
    lowerPipeY = offset + \
        random.randint(0, SCREENHEIGHT - GAME_SPRITES['base'].get_height() - (1.2*offset)) # 1.2*offset is added so that lower pipe doesn't disapper in the base
    # below the top and from there we will generate a random number to the base of the game
    upperPipeY = GAME_SPRITES['pipes'][0].get_height() - lowerPipeY + offset
    return [{'x': pipex, 'y': -(upperPipeY)}, {'x': pipex, 'y': lowerPipeY}]


if __name__ == '__main__':
    # This will be the main point from where game will start
    pygame.init()  # initialize all modules of pygame
    # create an object to help track time later we will use clock.tick() function to control the FPS of game as it will set for how many sec a frame will run
    FPSCLOCK = pygame.time.Clock()
    # it will set the caption of screen
    pygame.display.set_caption('Flappy Bird by Cosmo')
    GAME_SPRITES['numbers'] = (
        pygame.image.load('gallery/sprites/0.png').convert_alpha(),
        pygame.image.load('gallery/sprites/1.png').convert_alpha(),
        pygame.image.load('gallery/sprites/2.png').convert_alpha(),
        pygame.image.load('gallery/sprites/3.png').convert_alpha(),
        pygame.image.load('gallery/sprites/4.png').convert_alpha(),
        pygame.image.load('gallery/sprites/5.png').convert_alpha(),
        pygame.image.load('gallery/sprites/6.png').convert_alpha(),
        pygame.image.load('gallery/sprites/7.png').convert_alpha(),
        pygame.image.load('gallery/sprites/8.png').convert_alpha(),
        pygame.image.load('gallery/sprites/9.png').convert_alpha()
    )

    GAME_SPRITES['message'] = pygame.image.load(
        'gallery/sprites/message.png').convert_alpha()
    GAME_SPRITES['base'] = pygame.image.load(
        'gallery/sprites/base.png').convert_alpha()
    GAME_SPRITES['pipes'] = (
        pygame.transform.rotate(pygame.image.load(PIPE).convert_alpha(), 180),
        pygame.image.load(PIPE).convert_alpha()
    )
    GAME_SPRITES['background'] = pygame.image.load(BACKGROUND).convert()
    GAME_SPRITES['player'] = pygame.image.load(PLAYER).convert_alpha()

    # game sounds
    GAME_SOUNDS['die'] = pygame.mixer.Sound('gallery/audio/die.mp3')
    GAME_SOUNDS['hit'] = pygame.mixer.Sound('gallery/audio/hit.mp3')
    GAME_SOUNDS['point'] = pygame.mixer.Sound('gallery/audio/point.wav')
    GAME_SOUNDS['swoosh'] = pygame.mixer.Sound('gallery/audio/swoosh.mp3')
    GAME_SOUNDS['wing'] = pygame.mixer.Sound('gallery/audio/wing.wav')

    while True:
        welcomeScreen()
        mainGame()
