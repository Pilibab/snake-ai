import pygame 
import config


class Snake:
    def __init__(self, cell, position, direction, segment_count):
        self.direction = direction
        self.segment_count = segment_count
        self.segments = [
            position- pygame.Vector2(segment,0)
            for segment in range(self.segment_count)
        ]
        self.cell = cell


    def draw_snake(self, screen):
        for segment in self.segments:
            Rect = (segment.x * self.cell, segment.y * self.cell,
                    self.cell, self.cell)
            pygame.draw.rect(screen, "white", Rect)
            pygame.draw.rect(screen, config.GRID_COLOR, Rect, width=1)

    def change_dir(Self):
        pass

    def move_snake(self, growth_flag):
        self.segments.insert(0, self.direction + self.segments[0])
        
        if not growth_flag:
            self.segments.pop()      

    # def check_self_collision(self):
    #     pass

    def check_border_collision(self):
        border = [config.GAME_HEIGHT // self.cell, 
                config.GAME_WIDTH // self.cell, -1]
        if self.segments[0].x in border or self.segments[0].y in border:
            return True
        return False
    
    def reset(self, initial_pos, initial_direction, initial_count):
        self.direction = initial_direction
        self.segment_count = initial_count
        self.segments = [
            initial_pos - pygame.Vector2(segment,0)
            for segment in range(initial_count)
        ]
    def check_self_collision(self):
        if self.segments[0] in self.segments[1:]:
            return True
        return False