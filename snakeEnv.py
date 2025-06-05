import config 
import pygame 

from snake import Snake
from helper import rotate_left, rotate_right
from fruit import Fruit

class Snake_env:
    def __init__(self, screen):

        self.screen = screen
        self.cell_size = config.CELL_SIZE
        
        # Set starting info Snake
        self.snake_pos = config.SNAKE_INITIAL_POS
        self.snake_dir = config.SNAKE_INITIAL_DIR
        self.segment_count = config.SNAKE_SEGMENT_COUNT

        # Initialize Snake class
        self.snake = Snake(self.cell_size, 
                        self.snake_pos, 
                        self.snake_dir, 
                        self.segment_count)
        
        # Initialize Fruit class
        self.fruit = Fruit(
                        self.cell_size, 
                        self.snake.segments)
        self.score = 0 
    
    def check_border_collision(self, pos=None):
        if pos is None:
            head = self.snake.segments[0]
            x, y = head.x, head.y
        else:
            x, y = pos

        if x < 0 or x >= config.GAME_WIDTH or y < 0 or y >= config.GAME_HEIGHT:
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
            return True
        return False

    def get_state(self):
        head = self.snake.segments[0]               # gets the first segment -> return vect2(), tuples 
        dir_v = self.snake.direction                # direction -> returns vect2() i.e (-1,0), (1,0) etc..

        # Grid relative to head
        left_dir = rotate_left(dir_v)
        right_dir = rotate_right(dir_v)
        forward_dir = dir_v

        # Compute relative positions
        pos_left = (head.x + left_dir[0], head.y + left_dir[1])
        pos_forward = (head.x + forward_dir[0], head.y + forward_dir[1])
        pos_right = (head.x + right_dir[0], head.y + right_dir[1])

        # Get danger flags
        danger_left = self.danger(pos_left)
        danger_forward = self.danger(pos_forward)
        danger_right = self.danger(pos_right)

        # Relative fruit position
        fruit_dx = self.fruit.position.x - head.x
        fruit_dy = self.fruit.position.y - head.y

        Rects = [
            ((head.x + left_dir[0]) * self.cell_size, (head.y + left_dir[1]) * self.cell_size, self.cell_size, self.cell_size),
            ((head.x + forward_dir[0]) * self.cell_size, (head.y + forward_dir[1]) * self.cell_size, self.cell_size, self.cell_size),
            ((head.x + right_dir[0]) * self.cell_size, (head.y + right_dir[1]) * self.cell_size, self.cell_size, self.cell_size),
        ]

        return [danger_right, danger_forward, danger_left, fruit_dx, fruit_dy, Rects]
        
    def danger(self, pos):
        x, y = pos
        # Check for border 
        if x < 0 or x >= config.GAME_HEIGHT // self.cell_size:
            return 1
        if y < 0 or y >= config.GAME_HEIGHT // self.cell_size:
            return 1
        
        # Check for self possible collision 
        if pygame.Vector2(x,y) in self.snake.segments:
            return 1
        # Default     
        return 0





