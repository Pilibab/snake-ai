import pygame


import config
from snake import Snake
from snakeEnv import Snake_env

class Game:
    def __init__(self):
        self.isRunning = True
        self.screen = pygame.display.set_mode(config.TRUE_SCREEN)
        self.cell_size = config.CELL_SIZE
        self.env = Snake_env(self.screen) 
        self.snake = self.env.snake
        self.fruit = self.env.fruit
        self.clock = pygame.time.Clock()
        self.move_delay = 0

    def run(self):
        while self.isRunning:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.isRunning = False

            self.screen.fill("black")


            self.draw_panel()
            self.draw_grid()

            self.snake.draw_snake(self.screen)
            self.fruit.draw_fruit(self.screen)


            # Add movement delay to still keep 60 fps
            if self.move_delay > 6:
                self.snake.move_snake()
                self.move_delay = 0 

                if self.env.check_border_collision() or self.env.check_self_collision():
                    self.reset()

                self.env.check_fruit_collision()

            self.move_delay += 1
            self.clock.tick(60)
            pygame.display.flip()

    def draw_panel(self):
        Rect = (config.GAME_WIDTH, 0,
                config.GAME_WIDTH + config.PANEL_WIDTH, config.GAME_HEIGHT)
        pygame.draw.rect(self.screen, config.PANEL_COLOR, Rect)

    def draw_grid(self):
        for x in range(0, config.GAME_WIDTH, config.CELL_SIZE):
            pygame.draw.line(self.screen,  config.GRID_COLOR,(x, 0), (x, config.GAME_HEIGHT))
        for y in range(0, config.GAME_HEIGHT, config.CELL_SIZE):
            pygame.draw.line(self.screen, config.GRID_COLOR, (0, y), (config.GAME_WIDTH, y))

    def reset(self):
        self.env.reset(config.SNAKE_INITIAL_POS, config.SNAKE_INITIAL_DIR, config.SNAKE_SEGMENT_COUNT)
        self.snake = self.env.snake
        self.fruit = self.env.fruit