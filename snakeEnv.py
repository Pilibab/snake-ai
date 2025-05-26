import config 
import pygame 

from snake import Snake
from fruit import Fruit

class Snake_env:
    def __init__(self, screen,):
        self.cell_size = config.CELL_SIZE
        
        self.snake_pos = config.SNAKE_INITIAL_POS
        self.snake_dir = config.SNAKE_INITIAL_DIR
        self.segment_count = config.SNAKE_SEGMENT_COUNT
        self.snake = Snake(self.cell_size, 
                        self.snake_pos, 
                        self.snake_dir, 
                        self.segment_count)
        self.fruit = Fruit(
                        self.cell_size, 
                        self.snake.segments)
        self.score = 0 
    
    
    def check_border_collision(self):
        border = [config.GAME_HEIGHT // self.cell_size, 
                config.GAME_WIDTH // self.cell_size, -1]
        if self.snake.segments[0].x in border or self.snake.segments[0].y in border:
            print("border collided")
            return True
        return False
    
    def reset(self, initial_pos, initial_direction, initial_count):
        self.snake = Snake(self.cell_size, initial_pos, initial_direction, initial_count)
        self.fruit = Fruit(self.cell_size, self.snake.segments)
        self.score = 0
        
    def check_self_collision(self):
        if self.snake.segments[0] in self.snake.segments[1:]:
            return True
        return False
    
    def check_fruit_collision(self):
        if self.fruit.position == self.snake.segments[0]:
            self.snake.grow = True
            self.score += 1


