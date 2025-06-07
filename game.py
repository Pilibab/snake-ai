import pygame
import config
from snakeEnv import Snake_env
import os 

from numpy import sum

class Game:
    def __init__(self, agent):
        # Game logic
        self.isRunning = True
        self.screen = pygame.display.set_mode(config.TRUE_SCREEN)
        self.cell_size = config.CELL_SIZE
        self.clock = pygame.time.Clock()
        self.move_delay = 0
        self.score = 0
        self.best_score = 0 
        self.scores_array = []
        self.mean_score = []
        self.isFruit_eaten = False
        
        self.y_bar_len = 260
        self.x_bar_len = config.GAME_WIDTH + 40 + (config.PANEL_WIDTH - 40 * 2)
        self.y_multiplier = 1
        self.x_multiplier = 1
        self.score_display_default = [i for i in range(self.y_bar_len // 20)]
        self.episode_display_default = [i for i in range(self.x_bar_len // 20)]
        # Agent - env
        self.env = Snake_env(self.screen) 
        self.agent = agent
        self.snake = self.env.snake
        self.fruit = self.env.fruit
        self.danger_rects = []   
        # Training 
        self.training_enabled = True
        self.episode_done = False
        self.episodes = 1 
        # button 
        self.train_button = pygame.Rect(config.GAME_WIDTH + 20, 200, 120, 40)
        self.reset_button = pygame.Rect(config.GAME_WIDTH + 140, 200, 120, 40)
        # Load model
        if os.path.exists("model/dqn_model.pth"):
            self.agent.model.load_model("model/dqn_model.pth")
            print("Model auto-loaded.")

    def run(self):
        while self.isRunning:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.isRunning = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse(event.pos)

            # Reset screen
            self.screen.fill("black")

            # Draw game 
            self.draw_panel()
            self.draw_grid()

            self.danger_rects = self.env.danger_rects
            self.draw_danger_box(self.danger_rects)
            self.snake.draw_snake(self.screen)
            self.fruit.draw_fruit(self.screen)

            # Get old state
            old_state = self.env.get_state()
            dr, df, dl, fx, fy = old_state
            self.episode_done = False
            
            # Add movement delay to still keep 60 fps
            if self.move_delay > 1:
                self.move_delay = 0 

                if self.env.check_fruit_collision():
                    self.env.snake.grow = True
                    self.isFruit_eaten = True
                    self.score += 1
                    self.fruit.position = self.fruit.spawn_Fruit(self.snake.segments)   
                    print("\n\nate\n\n")

                status = "Tr" if self.training_enabled else ""

                # Getting action part 
                act_index = self.agent.get_action(old_state)
                action = [0,0,0]
                action[act_index] = 1

                # Use action to turn the snake
                if action == [1,0,0]:
                    self.snake.change_dir_left()
                elif action == [0,0,1]:
                    self.snake.change_dir_right()
                # else: [0,1,0] means go forward → do nothing

                self.snake.move_snake()
                new_state = self.env.get_state()

                if self.env.check_border_collision() or self.env.check_self_collision():
                    self.train()
                    self.episode_done = True

                reward = self.get_reward(old_state, new_state)
                self.agent.remember(old_state, action, reward, new_state, self.episode_done)

                # print(f"{status}: d[{dr},{df},{dl}], ∆F({fx}, {fy}), eps:{self.agent.epsilon:.2} r({reward})")

                self.agent.learn_short_term(old_state, action, reward, new_state, self.episode_done)

                # flag growth and eat
                self.isFruit_eaten = False
                self.env.snake.grow = False

                if self.episode_done:
                    self.take_screenshot()
                    self.reset()

            self.draw_panel()

            self.move_delay += 1
            self.clock.tick(60)
            # Update screen
            pygame.display.flip()

    def handle_mouse(self, pos):
        if self.train_button.collidepoint(pos):
            self.train()
        elif self.reset_button.collidepoint(pos):
            self.reset()

    def train(self):
        if self.training_enabled:
            self.episodes += 1
            self.agent.learn_long_term()
            self.agent.decay_exploration()
            if (self.episodes % 10) == 0:
                self.agent.model.save_model("model/dqn_model.pth")
                print(f"Model saved at episode {self.episodes}") 

    def get_reward(self, old, new):
        import math 
        _, _, _, ofx, ofy = old 
        _, _, _, nfx, nfy = new 


        mag_old = math.hypot(ofx, ofy)
        mag_new = math.hypot(nfx, nfy)
        if mag_new < mag_old: 
            return self.agent.reward["move_close"]
        if self.episode_done:
            return self.agent.reward["death"] 
        if self.isFruit_eaten:
            return self.agent.reward["eat"]
        return self.agent.reward["time_score_decay"] 

    def draw_button(self):
        pygame.draw.rect(self.screen, "blue", self.train_button)
        pygame.draw.rect(self.screen, "red", self.reset_button)

        font = pygame.font.SysFont("consolas", 20)
        train_text = font.render("Train", True, "white")
        reset_text = font.render("Reset", True, "white")

        self.screen.blit(train_text, (self.train_button.x + 20, self.train_button.y + 10))
        self.screen.blit(reset_text, (self.reset_button.x + 20, self.reset_button.y + 10))

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
        self.scores_array.append(self.score)
        self.mean_score.append(self.score / self.episodes)
        
        if self.score >= self.best_score:
            self.best_score = self.score

        self.score = 0

        if self.training_enabled: 
            self.episode_done = True

    def draw_panel(self):
        Rect = (config.GAME_WIDTH, 0,
                config.GAME_WIDTH + config.PANEL_WIDTH, config.GAME_HEIGHT)
        pygame.draw.rect(self.screen, config.PANEL_COLOR, Rect)
        # self.draw_button()
        self.plot_score()
        self.write_current_score()

    def write_current_score(self):
        
        score_font = pygame.font.SysFont(config.FONT_FAM, 15)
        text_surface = score_font.render(f"Best score: {self.best_score}", False, config.FONT_COLOR)
        text_rect = text_surface.get_rect(midleft=(config.GAME_WIDTH + 40, 380))
        self.screen.blit(text_surface, text_rect)

        score_font = pygame.font.SysFont(config.FONT_FAM, 15)
        text_surface = score_font.render(f"score: {self.score}", False, config.FONT_COLOR)
        text_rect = text_surface.get_rect(midleft=(config.GAME_WIDTH + 40, 400))
        self.screen.blit(text_surface, text_rect)

        text_surface = score_font.render(f"No. of Segments: {self.snake.segment_count}", False,  config.FONT_COLOR)
        text_rect = text_surface.get_rect(midleft=(config.GAME_WIDTH + 40, 420))
        self.screen.blit(text_surface, text_rect)

        text_surface = score_font.render(f"Current episode: {self.episodes}", False,  config.FONT_COLOR)
        text_rect = text_surface.get_rect(midleft=(config.GAME_WIDTH + 40, 440))
        self.screen.blit(text_surface, text_rect)

        text_surface = score_font.render(f"Mean score: {sum(self.scores_array) / self.episodes:.2}", False,  config.FONT_COLOR)
        text_rect = text_surface.get_rect(midleft=(config.GAME_WIDTH + 40, 460))
        self.screen.blit(text_surface, text_rect)
        
        
        score_font = pygame.font.SysFont(config.FONT_FAM, 15)
        text_surface = score_font.render(f"Current epsilon: {self.agent.epsilon:.2}", False, config.FONT_COLOR)
        text_rect = text_surface.get_rect(midleft=(config.GAME_WIDTH + 40, 480))
        self.screen.blit(text_surface, text_rect)

    def plot_score(self):
        # Render font and offset 
        font = pygame.font.SysFont(config.FONT_FAM, 20)
        font_label = pygame.font.SysFont(config.FONT_FAM, 15)
        font_ticks_label = pygame.font.SysFont(config.FONT_FAM, 10)

        offSetX, offSetY = 40, 40
        text_posX, text_posY = config.GAME_WIDTH + (config.PANEL_WIDTH / 2), 20

        # Set bar lengths
        self.y_bar_len = 260
        self.x_bar_len = config.GAME_WIDTH + 40 + (config.PANEL_WIDTH - 40 * 2)

        # Handle score and episode scaling
        max_score = max(self.scores_array) if self.scores_array else 1
        max_episode = len(self.scores_array)

        # Calculate multipliers to scale axes if needed
        self.y_multiplier = 1
        self.x_multiplier = 1
        y_tick_count = self.y_bar_len // 20 - 1
        x_tick_count = (self.x_bar_len - config.GAME_WIDTH - 40) // 20 - 1

        if max_score > y_tick_count:
            self.y_multiplier = (max_score // y_tick_count) + 1
        if max_episode > x_tick_count:
            self.x_multiplier = (max_episode // x_tick_count) + 1

        # Tick label values
        self.score_display_default = [i * self.y_multiplier for i in range(y_tick_count)]
        self.episode_display_default = [i * self.x_multiplier for i in range(x_tick_count)]

        # Axis endpoints
        vertical_start = (config.GAME_WIDTH + offSetX, offSetY)
        vertical_end = (config.GAME_WIDTH + offSetX, offSetY + self.y_bar_len)
        horizontal_start = vertical_end
        horizontal_end = (self.x_bar_len, vertical_end[1])

        # Title
        text_surface = font.render("Score-episode", False,  config.FONT_COLOR)
        text_rect = text_surface.get_rect(center=(text_posX, text_posY))
        self.screen.blit(text_surface, text_rect)

        # Axis labels
        x_label = font_ticks_label.render("No of games (episode)", True,  config.FONT_COLOR)
        y_label_letters = [font_ticks_label.render(c, False,  config.FONT_COLOR) for c in "Score"]

        x_label_rect = x_label.get_rect(center=(text_posX, vertical_end[1] + 40))
        self.screen.blit(x_label, x_label_rect)

        j = 125
        for label in y_label_letters:
            rect = label.get_rect(center=(config.GAME_WIDTH + 10, j))
            self.screen.blit(label, rect)
            j += 10

        # Draw Y-axis and ticks
        pygame.draw.line(self.screen, "black", vertical_start, vertical_end)

        for i, score in enumerate(self.score_display_default):
            y = offSetY - 10 + self.y_bar_len - i * 20
            # Tick mark
            pygame.draw.line(self.screen, "black", (vertical_start[0] - 5, y), (vertical_start[0], y), 2)
            # Tick label
            label = font_ticks_label.render(str(score), True, "black")
            self.screen.blit(label, (vertical_start[0] - 20, y - 8))

        # Draw X-axis and ticks
        pygame.draw.line(self.screen, "black", horizontal_start, horizontal_end)

        for i, episode in enumerate(self.episode_display_default):
            x = config.GAME_WIDTH + 50 + i * 20
            # Tick mark
            pygame.draw.line(self.screen, "black", (x, vertical_end[1]), (x, vertical_end[1] + 5), 2)
            # Tick label
            label = font_ticks_label.render(str(episode), True, "black")
            label_rect = label.get_rect(center=(x, vertical_end[1] + 15))
            self.screen.blit(label, label_rect)

        # Plot line 
        acc_offsety = offSetY - 10 + self.y_bar_len 

        # I DONT GET THIS MATH 
        coords = [((i * 20 )/ self.x_multiplier + config.GAME_WIDTH + 50, (acc_offsety - score * 20 )) 
                for i, score in enumerate(self.scores_array)]
        
        mean_coor = [((i * 20 )/ self.x_multiplier + config.GAME_WIDTH + 50, (acc_offsety - mean_score * 20 ))
                    for i, mean_score in enumerate(self.scores_array)]
        
        for i in range(len(coords)):
            x1, y1 = coords[i - 1]
            x2, y2 = coords[i]
            pygame.draw.line(self.screen, "green", (x1, y1), (x2, y2), 1)

        # for i in range(len(mean_coor)):
        #     x1, y1 = mean_coor[i - 1]
        #     x2, y2 = mean_coor[i]
        #     pygame.draw.line(self.screen, "blue", (x1, y1), (x2, y2), 1)


    def take_screenshot(self):
        os.makedirs("documentation/episodes", exist_ok=True)
        os.makedirs("documentation/best_score", exist_ok=True)

        if self.episodes % 10 == 0:
            file_name = f"documentation/episodes/episode_{self.episodes}.png"
            pygame.image.save(self.screen, file_name)
        elif self.score > self.best_score:
            file_name = f"documentation/best_score/best_score_{self.score}.png"
            pygame.image.save(self.screen, file_name)






