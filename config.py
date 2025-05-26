import pygame
# initialize game screen
GAME_WIDTH = 600
GAME_HEIGHT = 600
PANEL_WIDTH = 300

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
SNAKE_INITIAL_DIR = pygame.Vector2(0,-1)