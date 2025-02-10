import pygame
import math

# Initialize Pygame
HEIGHT = 700 # must be greater than 600
WIDTH = 1400 # must be greater than 1200
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ayo Game")

# Co-ordinates of the board
X = (WIDTH - 1129) / 2
Y = (HEIGHT - 448) / 2

# storing game images
board_image = pygame.image.load("assets\\ayo_board.png").convert_alpha()
bead_images = {}
for i in range(0, 22):
    bead_images[i] = pygame.image.load(f"assets\\ayo_bead_{i}.png").convert_alpha()

# image offsets for beads
offset_x = 28
offset_y = 25
delta_x = 181.5
delta_y = 233.5

# house circle radius
radii = 166

# define some colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# define font for the game
font = pygame.font.Font(None, 36)

# import some ayo_game logic
from ayo_game import *

# define function to render score
def render_scores(score):
    player0_score = font.render(f"Player 0: {score[0]}", True, BLACK)
    player1_score = font.render(f"Player 1: {score[1]}", True, BLACK)
    screen.blit(player0_score, (10, 10))
    screen.blit(player1_score, (10, 50))

# define function to render game status
def render_game_status(status):
    game_status = font.render(status, True, BLACK)
    rect = game_status.get_rect(center = (screen.get_width() // 2, Y - 46))
    screen.blit(game_status, rect)

# define function to render beads from a board state
def render_beads(board):
    for i in range(2):
        for j in range(6):
            screen.blit(bead_images[board[i][j]], (X + offset_x + j * delta_x, Y + offset_y + i * delta_y))

# define function to check if a position is within cell bounds
def cell(position):
    """
    return False if not in any cell
    return cell coords if in cell
    """
    for i, j in DISTRIBUTION_ORDER:
        lower_bound = (X + offset_x + j * delta_x, Y + offset_y + i * delta_y)
        upper_bound = (X + offset_x + j * delta_x + radii, Y + offset_y + i * delta_y + radii)
        if position[0] >= lower_bound[0] and position[1] >= lower_bound[1]:
            if position[0] <= upper_bound[0] and position[1] <= upper_bound[1]:
                return (i, j)
    
    return False

# define function to render instruction
def render_instruction():
    intrusction_title = font.render("Instruction", True, BLACK)
    instruction = font.render("""Player 0 plays from the top half of the board, while Player 1 plays from the lower half. Player 0 Plays first.""", True, BLACK)
    screen.blit(intrusction_title, (10, HEIGHT - 86))
    screen.blit(instruction, (10, HEIGHT - 46))

# define function to render board
def render_board():
    screen.blit(board_image, (X, Y))

# initialize ayo game
game = ayo_game()

# set white background
screen.fill(WHITE)

# render board
render_board()

# render beads from game board state
render_beads(game.board)

# render initial display score
render_scores(game.score)

# render initial game status
render_game_status("Player 0's Turn")

# Game loop
running = True
while running:
    # handling game exit
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    # continually listen for valid play 
    val = False
    mouse_buttons = pygame.mouse.get_pressed()
        # Get mouse position if right click
    if mouse_buttons[0]:
        mouse_pos = pygame.mouse.get_pos()
        val = cell(mouse_pos)
    
    # if valid play, draw simulation of distribution while updating scores
    if val != False and val in game.valid_positions():
        states = game.full_distribute(val, path = True)
        game.player = (game.player + 1) % 2

        # render new bead state and scores
        for i in range(len(states["boards"])):
            board_i = states["boards"][i]
            score_i = states["scores"][i]
            screen.fill(WHITE)
            render_board()
            render_instruction()
            render_beads(board_i)
            render_scores(score_i)
            render_game_status(f"Distributing beads from Player {game.player}'s choice")
            pygame.display.update()
            pygame.time.delay(1000)

        # render game background, board and instruction again 
        # to avoid overlapping of text
        screen.fill(WHITE)
        render_board()
        render_instruction()

        render_beads(game.board)
        render_scores(game.score)

        # render game status
        if game.terminal():
            win = np.argmax(game.score)
            lose = (win + 1) % 2
            diff = game.score[win] - game.score[lose]
            if game.score[win] > game.score[lose]:
                render_game_status(f"Player {win} wins by a margin of {diff} beads ({int(diff / 4)} houses)")
            else:
                render_game_status("Game ends in a draw")
        else:
            render_game_status(f"Player {game.player}'s Turn")
    
    pygame.display.flip()
    pygame.time.delay(30)

pygame.quit()