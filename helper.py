import pygame
import config
import os 
import json 
import time 
from numpy import sum

def rotate_left(vector: tuple[int, int]) -> list :
    x, y = vector
    return [-y, x]


def rotate_right(vector: tuple[int, int]) -> list :
    x, y = vector
    return [y, -x]


class UiRender():
    def __init__(self, screen: pygame.surface):
        self.plot = Plot(screen)
        self.screen = screen
        self.cell = config.CELL_SIZE
        self.g_w = config.GAME_WIDTH
        self.g_h = config.GAME_HEIGHT
        self.grid_color = config.GRID_COLOR

    def draw_grid(self) -> None:
        for x in range(0, self.g_w, self.cell):
            pygame.draw.line(self.screen,self.grid_color ,(x, 0), (x, self.g_h))
        for y in range(0, self.g_w, self.cell):
            pygame.draw.line(self.screen, self.grid_color, (0, y), (self.g_w, y))

    def draw_danger_box(self, rectangles: list[tuple[int, int, int, int]]):
        for Rect in rectangles:
            x, y, _ , _ = Rect
            if x < 0 or x >= config.GAME_WIDTH:
                continue
            if y < 0 or y >= config.GAME_HEIGHT:
                continue
            pygame.draw.rect(self.screen, "green", Rect, 1) 

    def draw_panel(self, package: dict) -> None:
        Rect = (config.GAME_WIDTH, 0,
                config.GAME_WIDTH + config.PANEL_WIDTH, config.GAME_HEIGHT)
        pygame.draw.rect(self.screen, config.PANEL_COLOR, Rect)
        # self.draw_button()
        self.plot.plot_score(package)
        self.plot.write_game_info(package)

    def draw_snake(self, segments: list[pygame.Vector2]):
        x = 255
        for segment in segments:
            rgb = (x,x,x)
            Rect = (segment.x * self.cell, segment.y * self.cell,
                    self.cell, self.cell)
            pygame.draw.rect(self.screen, rgb, Rect)
            x -= 5
            # pygame.draw.rect(screen, config.GRID_COLOR, Rect, width=1)

    def draw_fruit(self, position: pygame.Vector2):
        Rect = (position.x * self.cell, position.y * self.cell,
                self.cell, self.cell)
        pygame.draw.rect(self.screen, config.FRUIT_COLOR, Rect)


class Plot():
    def __init__(self, screen):
        # plot 
        self.y_bar_len = 260
        self.x_bar_len = config.GAME_WIDTH + 40 + (config.PANEL_WIDTH - 40 * 2)
        self.y_multiplier = 1
        self.x_multiplier = 1
        self.score_display_default = [i for i in range(self.y_bar_len // 20)]
        self.episode_display_default = [i for i in range(self.x_bar_len // 20)]
        self.start_time_training = time.time()
        self.screen = screen

    def write_game_info(self, package: dict) -> None:
        
        score_font = pygame.font.SysFont(config.FONT_FAM, 15)
        text_surface = score_font.render(f"Best score: {package['best_score']}", False, config.FONT_COLOR)
        text_rect = text_surface.get_rect(midleft=(config.GAME_WIDTH + 40, 380))
        self.screen.blit(text_surface, text_rect)

        score_font = pygame.font.SysFont(config.FONT_FAM, 15)
        text_surface = score_font.render(f"score: {package['score']}", False, config.FONT_COLOR)
        text_rect = text_surface.get_rect(midleft=(config.GAME_WIDTH + 40, 400))
        self.screen.blit(text_surface, text_rect)
        # No. of segments from snake i.e the length of the body 
        text_surface = score_font.render(f"No. of Segments: {package['segment_count']}", False,  config.FONT_COLOR)
        text_rect = text_surface.get_rect(midleft=(config.GAME_WIDTH + 40, 420))
        self.screen.blit(text_surface, text_rect)
        # display at what episode 
        text_surface = score_font.render(f"Current episode: {package['episodes']}", False,  config.FONT_COLOR)
        text_rect = text_surface.get_rect(midleft=(config.GAME_WIDTH + 40, 440))
        self.screen.blit(text_surface, text_rect)
        # Current mean score 
        text_surface = score_font.render(f"Mean score: {sum(package['scores_array']) / package['episodes']:.2}", False,  config.FONT_COLOR)
        text_rect = text_surface.get_rect(midleft=(config.GAME_WIDTH + 40, 460))
        self.screen.blit(text_surface, text_rect)
        # Display current randomness for exploration 
        score_font = pygame.font.SysFont(config.FONT_FAM, 15)
        text_surface = score_font.render(f"Current epsilon: {package['epsilon']:.5f}", False, config.FONT_COLOR)
        text_rect = text_surface.get_rect(midleft=(config.GAME_WIDTH + 40, 480))
        self.screen.blit(text_surface, text_rect)
        # Moves made from the start till the end of an episode 
        score_font = pygame.font.SysFont(config.FONT_FAM, 15)
        text_surface = score_font.render(f"Steps in this episode: {package['steps_per_game']}", False, config.FONT_COLOR)
        text_rect = text_surface.get_rect(midleft=(config.GAME_WIDTH + 40, 500))
        self.screen.blit(text_surface, text_rect)
        # Display sum of all steps taken from all episodes
        score_font = pygame.font.SysFont(config.FONT_FAM, 15)
        text_surface = score_font.render(f"Total steps: {package['total_steps']}", False, config.FONT_COLOR)
        text_rect = text_surface.get_rect(midleft=(config.GAME_WIDTH + 40, 520))
        self.screen.blit(text_surface, text_rect)
        # Display elapsed time since training start 
        score_font = pygame.font.SysFont(config.FONT_FAM, 15)
        duration = time.time() - self.start_time_training
        formatted_time = time.strftime("%H:%M:%S", time.gmtime(duration))
        text_surface = score_font.render(f"Training duration: {formatted_time}", False, config.FONT_COLOR)
        text_rect = text_surface.get_rect(midleft=(config.GAME_WIDTH + 40, 540))
        self.screen.blit(text_surface, text_rect)

    def plot_score(self, package: dict) -> None:
        # Unpack package
        scores_array = package["scores_array"]
        mean_score = package["mean_score"]

        font = pygame.font.SysFont(config.FONT_FAM, 20)
        font_ticks_label = pygame.font.SysFont(config.FONT_FAM, 10)

        offSetX, offSetY = 40, 40
        text_posX, text_posY = config.GAME_WIDTH + (config.PANEL_WIDTH / 2), 20

        # Set bar lengths
        self.y_bar_len = 260
        self.x_bar_len = config.GAME_WIDTH + 40 + (config.PANEL_WIDTH - 40 * 2)

        # Handle score and episode scaling
        max_score = max(scores_array) if scores_array else 1
        max_episode = len(scores_array)

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

        # Display y label -> "score" per letters vertically 
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
        coords = [((i * 20  )/ self.x_multiplier + config.GAME_WIDTH + 50, (acc_offsety - ((score * 20) / self.y_multiplier))) 
                for i, score in enumerate(scores_array)]
        
        mean_coor = [((i * 20 ) / self.x_multiplier + config.GAME_WIDTH + 50, (acc_offsety -(( mean_score * 20) / self.y_multiplier)))
                    for i, mean_score in enumerate(mean_score)]
        
        for i in range(1, len(coords)):
            x1, y1 = coords[i - 1]
            x2, y2 = coords[i]
            pygame.draw.line(self.screen, "green", (x1, y1), (x2, y2), 1)

        for i in range(1, len(mean_coor)):
            x1, y1 = mean_coor[i - 1]
            x2, y2 = mean_coor[i]
            pygame.draw.line(self.screen, "blue", (x1, y1), (x2, y2), 1)


class Logger():
    def __init__(self, screen,  path: str ="logs/snake_log.json"):
        self.log_data = {
            "Info": "Snake RL Logs",
            "description": "trying the standard state representation ",
            "Batch_size": config.BATCH_SIZE,
            "Memory": config.MEMORY,
            "Gamma": config.GAMMA,
            "Lr": config.AlPHA,
            "total training duration": None,
            "Episodes": []
        }
        self.episode_buffer = {}
        self.fruit_info = []
        self.path = path
        self.screen = screen
    
    def take_screenshot(self, episodes: int , score: int, best_score: int) -> None:
        os.makedirs("documentation/episodes", exist_ok=True)
        os.makedirs("documentation/best_score", exist_ok=True)
        if episodes % 10 == 0:
            file_name = f"documentation/episodes/episode_{episodes}.png"
            pygame.image.save(self.screen, file_name)
        elif score > best_score:
            file_name = f"documentation/best_score/best_score_{score}.png"
            pygame.image.save(self.screen, file_name)

    def save_to_json(self, episodes):
        # Ensure file exists, create if not
        if not os.path.exists(self.path):
            with open(self.path, 'w') as f:
                json.dump(self.log_data, f, indent=4)

        with open(self.path, 'r+') as file:
            file_data = json.load(file)
            # Append episode data
            file_data["Episodes"].append(self.episode_buffer)
            # Optional: update training duration if past 1000 episodes
            if episodes > 1000:
                duration = time.time() - self.start_time_training
                file_data["total training duration"] = time.strftime("%H:%M:%S", time.gmtime(duration))
            file.seek(0)
            json.dump(file_data, file, indent=4)
            file.truncate()  # Ensure any leftover bytes are removed

    def append_episode_info(self, package: dict) -> None:
        episode_data = {
            "episode": package["episodes"],
            "Duration_of_episode": round(time.time() - package["start_time"], 2),
            "Highest_episode_step": package["steps_per_game"],
            "Current_total_step": package["total_steps"],
            "Score": package["score"],
            "Mean_score": package["mean"],
            "Fruit_info": self.fruit_info  # List of dicts
        }
        self.episode_buffer = episode_data

    def append_fruit_info(self, package: dict, prev_pos: pygame.Vector2, curr_pos : pygame.Vector2) -> None:
        # distance from fruit pos to head
        if package["score"] == 0:
            x, y = config.SNAKE_INITIAL_POS
            distance_x = curr_pos.x - x
            distance_y = curr_pos.y - y
        else:
            distance_x = curr_pos.x - prev_pos.x
            distance_y = curr_pos.y - prev_pos.y

        dictionary = {
            "step": package["steps_per_game"],
            "time_elapsed":round(time.time() - package["start_time"], 3),
            "distance_to_fruit": [distance_x, distance_y]
        }
        self.fruit_info.append(dictionary)
