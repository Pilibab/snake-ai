import pygame 
import config
from numpy import matmul, array


class Snake:
    def __init__(self, cell, position, direction, segment_count):
        self.direction = direction
        self.segment_count = segment_count
        self.segments = [
            position- pygame.Vector2(segment,0)
            for segment in range(self.segment_count)
        ]
        self.cell = cell
        self.grow = False


    def draw_snake(self, screen):
        for segment in self.segments:
            Rect = (segment.x * self.cell, segment.y * self.cell,
                    self.cell, self.cell)
            pygame.draw.rect(screen, "white", Rect)
            pygame.draw.rect(screen, config.GRID_COLOR, Rect, width=1)

    def change_dir_right(self):
        x, y = self.direction
        n_x, n_y = matmul([x, y], config.CLOCKWISE)
        self.direction = pygame.Vector2(n_x, n_y)

    def change_dir_left(self):
        x, y = self.direction
        n_x, n_y = matmul([x, y], config.COUNTER_CLOCKWISE)
        self.direction = pygame.Vector2(n_x, n_y)


    def move_snake(self):
        self.segments.insert(0, self.direction + self.segments[0])
        if not self.grow:
            self.segments.pop() 




