import pygame 
import config
from helper import rotate_left, rotate_right

class Snake:
    def __init__(self, cell, position, direction, segment_count):
        self.direction = direction
        self.segment_count = segment_count
        self.segments = [
            position - pygame.Vector2(segment,0)
            for segment in range(self.segment_count)
        ]
        self.cell = cell
        self.grow = False

    def change_dir_right(self):
        self.direction = pygame.Vector2(*rotate_right(self.direction))

    def change_dir_left(self):
        self.direction = pygame.Vector2(*rotate_left(self.direction))

    def move_snake(self):
        self.segments.insert(0, self.direction + self.segments[0])
        if self.grow:
            self.grow = False
        else: 
            self.segments.pop()     




