import pygame
import config
from snakeEnv import Snake_env
from snakeAgent import Agent

class Game:
    def __init__(self):
        self.isRunning = True
        self.screen = pygame.display.set_mode(config.TRUE_SCREEN)
        self.cell_size = config.CELL_SIZE
        self.env = Snake_env(self.screen) 
        self.agent = Agent()
        self.snake = self.env.snake
        self.fruit = self.env.fruit
        self.clock = pygame.time.Clock()
        self.move_delay = 0
        self.danger_rects = []   

    def run(self):
        while self.isRunning:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.isRunning = False

            # Reset screen
            self.screen.fill("black")

            
            # Draw game 
            self.draw_panel()
            self.draw_grid()

            self.snake.draw_snake(self.screen)
            self.fruit.draw_fruit(self.screen)


            # Add movement delay to still keep 60 fps
            if self.move_delay > 6:
                self.move_delay = 0 

                if self.env.check_border_collision() or self.env.check_self_collision():
                    self.reset()

                if self.env.check_fruit_collision():
                    self.env.snake.grow = True
                    self.env.score += 1
                    self.fruit.spawn_Fruit(self.snake.segments)
                
                state = self.env.get_state()
                dr, df, dl, fx, fy, Rects = state
                self.danger_rects = Rects
                print(f"danger: [{dr}, {df}, {dl}], delta_fruit_pos: ({fx}, {fy})")
                
                action, act_index = self.agent.get_action(state)

                # Use action to turn the snake
                if action == [1,0,0]:
                    self.snake.change_dir_left()
                elif action == [0,0,1]:
                    self.snake.change_dir_right()
                # else: [0,1,0] means go forward → do nothing

                self.snake.move_snake()
            
            self.draw_danger_box(self.danger_rects)

            self.move_delay += 1
            self.clock.tick(60)

            # Update screen
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

    def draw_danger_box(self, rectangles):
        for Rect in rectangles:
            x, y, _ , _ = Rect

            if x < 0 or x >= config.GAME_WIDTH:
                continue
            if y < 0 or y >= config.GAME_HEIGHT:
                continue
            pygame.draw.rect(self.screen, "green", Rect, 1) 
        
    def reset(self):
        self.env.reset(config.SNAKE_INITIAL_POS, config.SNAKE_INITIAL_DIR, config.SNAKE_SEGMENT_COUNT)
        self.snake = self.env.snake
        self.fruit = self.env.fruit