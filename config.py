import pygame
# initialize game screen
GAME_WIDTH = 600
GAME_HEIGHT = 600
PANEL_WIDTH = 400

TRUE_SCREEN = (GAME_WIDTH + PANEL_WIDTH, GAME_HEIGHT)

# Define cell size
CELL_SIZE = 20

# Game color
PANEL_COLOR = "white"
GRID_COLOR = (56, 50, 24)
FRUIT_COLOR = (255, 87, 51)

# Snake Initial pos 
SNAKE_INITIAL_POS = pygame.Vector2(GAME_WIDTH // CELL_SIZE // 2, 
                                   GAME_HEIGHT // CELL_SIZE // 2)
SNAKE_SEGMENT_COUNT = 3
SNAKE_INITIAL_DIR = pygame.Vector2(1,0)

FONT_FAM = 'Arial'
FONT_COLOR = "black"

# Movement
COUNTER_CLOCKWISE = [[0,-1],
                    [1,0]]
CLOCKWISE = [[0,1],
            [-1,0]]

# Machine learning constant / training const 
AlPHA = 0.001
GAMMA = .9
EPSILON = 1.0
EPS_DECAY = .995
EPS_MIN = 0.1
BATCH_SIZE = 64         #exp
MEMORY = 100_000