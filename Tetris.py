#John Tran. Justin Dixon, John Paul Ordanza
#March 29, 2021
#Code based on: https://www.techwithtim.net/tutorials/game-development-with-python/tetris-pygame/tutorial-4/
#The purpose of this program is to recreate a simple version of the game Tetris. Our version combines features of classic tetris along with some of the features of modern tetris.

import pygame
import random
import time
import copy

pygame.font.init()

# GLOBALS VARS
s_width = 800
s_height = 700
play_width = 300  # meaning 300 // 10 = 30 width per block
play_height = 600  # meaning 600 // 20 = 30 height per block
block_size = 30

top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height

#Our addition: Setting the frequency at which pieces can shift sideways or down when holding keys.
MOVESIDEWAYSFREQ = 0.15
MOVEDOWNFREQ = 0.1

#Our addition: Set FPS.
FPS = 60

# SHAPE FORMATS

#Our addition: Changed starting rotation of I pieces.
S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['.....',
      '.....',
      '0000.',
      '.....',
      '.....'],
     ['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

#Lists of shapes and shape colors.
shapes = [S, Z, I, O, J, L, T]
shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]
# index 0 - 6 represent shape

#Class to define attributes of each tetris piece.
class Piece(object):  # *
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0

#Function to draw 10 by 20 grid filled with black squares.
def create_grid(locked_pos={}):  # *
    grid = [[(0,0,0) for _ in range(10)] for _ in range(20)]

    #Loop to update the colors of the grid with the colors of the tetris pieces that have been locked in place.
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_pos:
                c = locked_pos[(j,i)]
                grid[i][j] = c
    return grid


def convert_shape_format(shape):
    positions = []
    #Determine which rotation the shape is in (according to element number in the list for each shape.) Uses modulus to ensure the number is never greater than the index numbers of the list.
    format = shape.shape[shape.rotation % len(shape.shape)]

    #Loop to convert the shape from the format full of 0 and . to coordinate positions.
    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((shape.x + j, shape.y + i))

#Our addition: Fixed bug where while piece is off screen, can cause game over by adjusting vertical displacement. Spawns the shape partly out of the top of the screen and partly inside the grid.
    for i, pos in enumerate(positions):
        positions[i] = (pos[0] -2 , pos[1] - 3)

    return positions


def valid_space(shape, grid):
    #List of accepted positions (any space that is black in the grid).
    accepted_pos = [[(j, i) for j in range(10) if grid[i][j] == (0,0,0)] for i in range(20)]
    #Flatten list to obtain list full of tuples as elements. Each tuple represents x and y coordinates.
    accepted_pos = [j for sub in accepted_pos for j in sub]

    formatted = convert_shape_format(shape)

    #Compares the coordinates of the shape(formatted variable) with the avaliable positions (accepted_pos). If it is not in accepted_pos, it is an invalid space.
    for pos in formatted:
        if pos not in accepted_pos:
            #Since piece begins off-screen, check if valid if > -1.
            if pos[1] > -1:
                return False
    return True

#Function to check if the player has lost based on the y coordinate position of a piece.
def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True

    return False

#Function to randomly choose a piece from the list of shapes.
def get_shape():
    return Piece(5, 0, random.choice(shapes))

#Function to draw text at the middle of the screen.
def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont("comicsans", size, bold=True)
    label = font.render(text, 1, color)

    surface.blit(label, (top_left_x + play_width /2 - (label.get_width()/2), top_left_y + play_height/2 - label.get_height()/2))

#Function to draw grid lines on the grid.
def draw_grid(surface, grid):
    sx = top_left_x
    sy = top_left_y

    for i in range(len(grid)):
        pygame.draw.line(surface, (128,128,128), (sx, sy + i*block_size), (sx+play_width, sy+ i*block_size)) #horizontal lines
        for j in range(len(grid[i])):
            pygame.draw.line(surface, (128, 128, 128), (sx + j*block_size, sy),(sx + j*block_size, sy + play_height)) #vertical lines

#Function to clear rows when full by checking if there are any black spaces in a row (if there are none, that means the line is filled).
def clear_rows(grid, locked):
    inc = 0
    for i in range(len(grid)-1, -1, -1):
        row = grid[i]
        if (0,0,0) not in row:
            inc += 1
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j,i)]
                except:
                    continue

#Clear rows function deletes a row from the grid. Redraw the row, then shift all the blocks from above the row down.
    if inc > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)

    return inc

#Function to draw the preview of the next shape. Draws the shape by using the same loop as convert_shape_format.
def draw_next_shape(shape, surface):
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Next Shape', 1, (255,255,255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height/2 - 100
    format = shape.shape[shape.rotation % len(shape.shape)]

#Draw the shape the same way the convert shape format function does it.
    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, shape.color, (sx + j*block_size, sy + i*block_size, block_size, block_size), 0)

    surface.blit(label, (sx + 10, sy - 30))

#Our addition: Function to draw text.
def draw_text(text, size, x, y, surface):
    font = pygame.font.SysFont('comicsans', size)
    label = font.render(text, 1, (255,255,255))
    surface.blit(label,(x,y))

#Our addition: Drawing held piece.
def draw_held_piece(shape, surface):
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Hold', 1, (255,255,255))

    sx = top_left_x - play_width/2
    sy = top_left_y + play_height/2 - 100

    if held_piece != "":
        format = shape.shape[shape.rotation % len(shape.shape)]

#Draw the shape the same way the convert shape format function does it.
        for i, line in enumerate(format):
            row = list(line)
            for j, column in enumerate(row):
                if column == '0':
                    pygame.draw.rect(surface, shape.color, (sx + j*block_size - 40, sy + i*block_size, block_size, block_size), 0)

    surface.blit(label, (sx + 10, sy - 30))

#Function to update the high score of the player after the player finishes a game.
def update_score(nscore):
    score = max_score()

    with open('scores.txt', 'w') as f:
        if int(score) > nscore:
            f.write(str(score))
        else:
            f.write(str(nscore))

#Function to display high score.
def max_score():
    with open('scores.txt', 'r') as f:
        lines = f.readlines()
        score = lines[0].strip()

    return score

#Function to draw the main window along with the other important game elements such as the grid, scores, and number of cleared lines.
def draw_window(surface, grid, score=0, last_score = 0, level = 0):
    surface.fill((0, 0, 0))

    pygame.font.init()
    font = pygame.font.SysFont('comicsans', 60)
    label = font.render('Tetris', 1, (255, 255, 255))

    surface.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2), 30))

    # current score
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Score: ' + str(score), 1, (255,255,255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height/2 - 100

    surface.blit(label, (sx + 20, sy + 160))

    # last score
    label = font.render('High Score: ' + last_score, 1, (255,255,255))

    sx = top_left_x - 225
    sy = top_left_y + 200

    surface.blit(label, (sx + 20, sy + 160))

    #Our addition: Level
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Level: ' + str(level), 1, (255,255,255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height/2 - 25

    surface.blit(label, (sx + 20, sy + 160))

    #Drawing the grid and border.
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (top_left_x + j*block_size, top_left_y + i*block_size, block_size, block_size), 0)

    pygame.draw.rect(surface, (255, 0, 0), (top_left_x, top_left_y, play_width, play_height), 5)

    draw_grid(surface, grid)

#Main game loop
def main(win):
    #Variables prior to game intialization.
    global clock, held_piece
    last_score = max_score()
    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    score = 0

    clearedlines = 0
    lastFallTime = time.time()
    level, fallFreq = calculateLevelAndFallFreq(clearedlines)

    switch = False
    held_piece =""
    flag = 0

    num_cleared = 0

# Our addition: Play our own trap remix version of the tetris theme. Since Replit cannot play audio, the code should be commented out when using Replit.
    try:
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load("tetris.mp3")
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play()
    except:
        pass

#Our addition: New variables to handle holding key inputs and limiting how much movement each piece can go through per second.
    lastMoveDownTime = time.time()
    lastMoveSidewaysTime = time.time()
    movingDown = False
    movingLeft = False
    movingRight = False

    #Game loop when the game is running.
    while run:
        #Create the grid, set the fps, and set the variable for the ghost piece.
        grid = create_grid(locked_positions)
        clock.tick(FPS)
        ghost_piece = copy.deepcopy(current_piece)
        ghost_piece.color = (90,90,90)

        #Our addition: adjusted fall speed calculations so pieces fall faster based on number of cleared lines.
        #Piece drops at a set frequency. The fall frequency changes based on the number of cleared lines.
        if time.time() - lastFallTime > fallFreq:
            level, fallFreq = calculateLevelAndFallFreq(clearedlines)
            current_piece.y += 1
            lastFallTime = time.time()
            if not(valid_space(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1
                pygame.event.clear()
                change_piece = True
                flag = 0

        #Our addition: Allowing player to hold pieces. The swapped current piece will spawn at the top of the screen.
        if switch:
            if held_piece == "":
                held_piece,current_piece = current_piece,held_piece
                current_piece = next_piece
                next_piece = get_shape()
                switch = False
            else:
                held_piece,current_piece = current_piece,held_piece
                current_piece.x = 5
                current_piece.y = 1
                switch = False

        #Check player inputs, including if the player decides to quit.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()

#Our addition: Enabling holding down keys by setting True and False flags based on when the key is pressed and released.
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    movingLeft = False
                if event.key == pygame.K_RIGHT:
                    movingRight = False
                if event.key == pygame.K_DOWN:
                    movingDown = False

#Our addition: Allow for holding the key down to allow pieces to be moved quicker.
#Pressing key moves the piece once. Holding it sets a variable that will continously move the piece in the desired direction until the key is released, setting the variable back to false.

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    movingLeft = True
                    movingRight = False
                    lastMoveSidewaysTime = time.time()
                    if not(valid_space(current_piece, grid)):
                        current_piece.x += 1
                if event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    movingLeft = False
                    movingRight = True
                    lastMoveSidewaysTime = time.time()
                    if not(valid_space(current_piece, grid)):
                        current_piece.x -= 1
                if event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    movingDown = True
                    lastMoveDownTime = time.time()
                    if not(valid_space(current_piece, grid)):
                        current_piece.y -= 1 

#Our addition: Added wall kicking. When rotating and there is no space, the piece will attempt to move right, then left. If both fail, the rotation fails.
#Fixed bug: I piece glitching through wall when wall kicking. Adjusted x coordinate movement to fix.
                if event.key == pygame.K_UP:
                    current_piece.rotation += 1
                    if not(valid_space(current_piece,grid)):
                        current_piece.x += 1
                        if not(valid_space(current_piece,grid)):
                            current_piece.x -= 2
                            if not(valid_space(current_piece,grid)):
                                current_piece.x += 1
                                current_piece.rotation -= 1

#Our addition: Allow rotation the opposite direction. Added wall kicking. When rotating and there is no space, the piece will attempt to move right, then left. If both fail, the rotation fails.
                if event.key == pygame.K_z:
                    current_piece.rotation -= 1
                    if not(valid_space(current_piece,grid)):
                        current_piece.x += 1
                        if not(valid_space(current_piece,grid)):
                            current_piece.x -= 2
                            if not(valid_space(current_piece,grid)):
                                current_piece.x += 1
                                current_piece.rotation += 1

#Our addition: Added ability to hard drop (instantly send pieces to bottom)
#Our addition: Fixed bug where multiple key presses could result in piece locking in place when no block is underneath by clearing event queue.
                if event.key == pygame.K_SPACE:
                  movingLeft = False
                  movingRight = False
                  movingDown = False
                  pygame.event.clear()
                  while (valid_space(current_piece, grid)):
                      current_piece.y += 1
                  if not (valid_space(current_piece, grid)):
                      current_piece.y -= 1
                      pygame.event.clear()
                  if valid_space(current_piece, grid):
                      pass
                  else:
                      change_piece = True
                      flag = 0

#Our addition: Added pause screen.
                if event.key == pygame.K_ESCAPE:
                    pause()

#Our addition: Key for holding. Restricts holding so the player can only press it once, then must place the current piece before a piece can be held again.
                if event.key == pygame.K_c:
                    if flag == 0:
                        flag = 1  
                        switch = True 

                if event.key == pygame.K_p:
                    controls()

#Our addition: Allowing constant movement of pieces left, right, and down with a amount of times the action can be performed per second limit set to slow down piece movement.
        if (movingLeft or movingRight) and time.time() - lastMoveSidewaysTime > MOVESIDEWAYSFREQ:
            if movingLeft and valid_space(current_piece, grid):
                current_piece.x -= 1
                if not(valid_space(current_piece, grid)):
                    current_piece.x += 1
            elif movingRight and valid_space(current_piece, grid):
                current_piece.x += 1
                if not(valid_space(current_piece, grid)):
                    current_piece.x -= 1
            lastMoveSidewaysTime = time.time()

#Check for holding down (soft dropping).
        if movingDown and time.time() - lastMoveDownTime > MOVEDOWNFREQ and valid_space(current_piece, grid):
            current_piece.y += 1
            if not(valid_space(current_piece, grid)):
                current_piece.y -= 1
            lastMoveDownTime = time.time()

#Our addition: Ghost piece placement. The placement of the ghost piece is similar to the code of hard dropping a piece, except the piece is not locked.
        while ghost_piece.y<21 and (valid_space(ghost_piece, grid)):
            ghost_piece.y += 1
        if not (valid_space(ghost_piece, grid)):
            ghost_piece.y -= 1                           

#Our addition: Added ghost piece (preview for where piece will land).
        shape_pos = convert_shape_format(current_piece)
        ghost_pos = convert_shape_format(ghost_piece)

#Drawing the ghost piece on the grid.
        for i in range(len(ghost_pos)):
            x, y = ghost_pos[i]
            if y > -1:
                grid[y][x] = ghost_piece.color

#Drawing the current piece on the grid.
        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color

#Loop to lock piece into place, then change the current piece to the next piece and grab a new next piece.
        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            num_cleared+= clear_rows(grid, locked_positions)

            #Our addition: changed score to increase based on number of cleared lines at one time.
            #fixed bug causing lines that should not be cleared to be cleared.
        if num_cleared == 1:
            score += 40
            clearedlines += 1
            num_cleared = 0
        elif num_cleared == 2:
            score += 100
            clearedlines += 2
            num_cleared = 0
        elif num_cleared == 3:
            score += 300
            clearedlines += 3
            num_cleared = 0
        elif num_cleared == 4:
            score += 1200
            clearedlines += 4
            num_cleared = 0

#Drawing all the necessary game elements and updating the scrren each loop.
        draw_window(win, grid, score, last_score, level)
        draw_next_shape(next_piece, win)
        draw_held_piece(held_piece,win)
        pygame.display.update()
        clock.tick(FPS)

#Our addition: Returns to main menu after game over.
#Game over screen.
        if check_lost(locked_positions):
            draw_text_middle(win, "Game Over", 80, (255,255,255))
            pygame.display.update()
            pygame.time.delay(2000)
            pygame.event.clear()
            run = False
            update_score(score)
            main_menu(win)

#Function for main menu.
def main_menu(win):  # *
    run = True
    while run:
        win.fill((0,0,0))
        draw_text_middle(win, 'Press Any Key To Play', 60, (255,255,255))
        draw_text('Press p For Controls', 50, 230, 475, win)
        bg = pygame.image.load('bg.png')
        win.blit(bg,(0,0))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    controls()
                else:
                    main(win)

    pygame.display.quit()

#Our addition: Calculation for fall speed based on number of cleared lines. Level increases for every 10 cleared lines.
def calculateLevelAndFallFreq(clearedlines):
    level = int(clearedlines/10)
    fallFreq = 0.27 - (level*0.02)
    return level, fallFreq

#Function to check for key presses. Used for pause screen to allow user to resume gameplay.
def checkForKeyPress():
    for event in pygame.event.get([pygame.KEYDOWN,pygame.KEYUP]):
        if event.type == pygame.KEYUP:
            continue
        return event.key
    return None
        
#Our addition: Function for pause screen.
def pause():
    win.fill((0,0,0))
    draw_text_middle(win, 'Press Any Key To Resume', 60, (255,255,255))
    draw_text('Paused', 100, 275, 275, win)
    pygame.display.update()
    while checkForKeyPress() == None:
        pygame.display.update()
        clock.tick()

#Our addition: Function for controls screen.
def controls():
    win.fill((0,0,0))
    draw_text('Press Any Key To Exit', 50, 230, 500, win)
    im = pygame.image.load('controls.jpg')
    win.blit(im,(220,200))
    pygame.display.update()
    while checkForKeyPress() == None:
        pygame.display.update()
  
#Setting the window size, caption, and intializing the game with the main menu.
win = pygame.display.set_mode((s_width, s_height))
pygame.display.set_caption('Tetris')
main_menu(win)