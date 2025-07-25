import config
import pygame 
from random import randint

class Fruit:
    def __init__(self, cell, snake_segment):
        self.cell_size = cell
        self.game_w = config.GAME_WIDTH
        self.game_h = config.GAME_HEIGHT
        self.position = self.spawn_Fruit(snake_segment)
        self.isEaten = False

    def spawn_Fruit(self, segments):
        while True:
            fruit_pos = pygame.Vector2(randint(0, self.game_w // self.cell_size - 1), 
                                        randint(0, self.game_h // self.cell_size- 1))
            
            # Check if random fruit pos is on top of snake 
            if all(fruit_pos != seg for seg in segments):
                return fruit_pos
                

