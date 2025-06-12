import pygame
import config
from snakeEnv import Snake_env
from helper import Logger, UiRender
import time 
import sys
import os
import json 

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
        self.isFruit_eaten = False
        # plotting / displaying info
        self.start_time = None                      # Starts at the start of an episode (tracks duration of each epi)
        self.track_time = True
        self.training_enabled = True
        self.episode_done = False
        self.episodes = 0 
        self.steps_per_game = 0
        self.total_steps = 0
        self.speed_limit = False

        # Agent - env
        self.env = Snake_env(self.screen) 
        self.agent = agent
        self.snake = self.env.snake
        self.fruit = self.env.fruit
        self.render = UiRender(self.screen)
        self.log = Logger(self.screen)


    def run(self):
        while self.isRunning:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.isRunning = False

            if self.track_time:
                self.start_time = time.time()
                self.track_time = False
            #* --------------------------------------GAME LOGIC (60 FPS)-------------------------------------------
            # Add movement delay to still keep 60 fps
            if self.move_delay > 1 or not self.speed_limit:
                self.move_delay = 0 
                # 1. Get old state
                old_state = self.env.get_state()
                self.episode_done = False
                # 2. Getting action part 
                act_index = self.agent.get_action(old_state)
                # 3. Use action to turn the snake
                if act_index == 1:
                    self.snake.change_dir_left()
                elif act_index == 2:
                    self.snake.change_dir_right()

                # 4. Move snake
                self.snake.move_snake()
                self.steps_per_game += 1

                # 5. Check collision 
                if self.env.check_border_collision() or self.env.check_self_collision():
                    self.episode_done = True

                # Check fruit collision before moving 
                if not self.episode_done and self.env.check_fruit_collision():
                    self.env.snake.grow = True
                    prev_pos = self.fruit.position
                    self.env.fruit.position = self.fruit.spawn_Fruit(self.snake.segments)
                    self.log.append_fruit_info(package, prev_pos, self.fruit.position)
                    self.isFruit_eaten = True
                    self.score += 1

                # 6. New state after moving 
                new_state = self.env.get_state()
                # 7. Cal reward
                reward = self.get_reward(old_state, new_state)
                # 8. Remember experience
                self.agent.remember(old_state, act_index, reward, new_state, self.episode_done)
                # 9. Train short term
                self.agent.learn_short_term(old_state, act_index, reward, new_state, self.episode_done)

                self.isFruit_eaten = False

            score_arr, mean_score_arr = self.extract_info()  
            current_mean = 0 if self.episodes == 0 else mean_score_arr[-1] + (self.score -  mean_score_arr[-1]) / self.episodes       
            
            package = {
                "best_score": self.best_score,
                "score": self.score,
                "mean": current_mean,  # O(1) find the currebt mean score from previous mean score 
                "segment_count": self.snake.segment_count,
                "episodes": self.episodes,
                "epsilon": self.agent.epsilon, 
                "steps_per_game": self.steps_per_game,
                "total_steps": self.total_steps,
                "scores_array": score_arr,
                "mean_score": mean_score_arr,
                "start_time": self.start_time
            }

            if self.episode_done:
                    self.episodes += 1
                    self.train()
                    self.log.take_screenshot(self.episodes, self.score, self.best_score)
                    self.log.append_episode_info(package)
                    self.log.save_to_json(self.episodes)
                    self.reset()
                    self.end_training()
            #* --------------------------------------Update UI -------------------------------------------
            # Reset screen
            self.screen.fill("black")
            # Draw game 
            self.render.draw_panel(package)
            self.render.draw_grid()
            self.render.draw_danger_box(self.env.danger_rects)
            self.render.draw_snake(self.snake.segments)
            self.render.draw_fruit(self.fruit.position)

            self.move_delay += 1
            self.clock.tick(60)
            # Update screen
            pygame.display.flip()


    def debug_states(self, old_state, reward):
        dr, df, dl, dir_l, dir_r, dir_u, dir_d, fl, fr, fu, fd = old_state
        status = "Tr" if self.training_enabled else ""
        if dir_r:
            direction = "r"
        elif dir_l:
            direction = "l"
        elif dir_u:
            direction = "u"
        else:
            direction = "d"
        print(f"{status}: d[{dr},{df},{dl}], ∆F({fl},{fr},{fu},{fd}), dir:{dir_l},{dir_r},{dir_u},{dir_d} ab_hat:{direction}, eps:{self.agent.epsilon:.2} r({reward})")


    def train(self):
        if self.training_enabled:
            self.agent.learn_long_term()
            self.agent.decay_exploration()
            if (self.episodes % 50) == 0:
                self.agent.model.save_model("model/dqn_model", self.episodes)
                print(f"Model saved at episode {self.episodes}") 


    def get_reward(self, old, new):
        """
            [danger_right, 
            danger_forward, 
            danger_left, 
            dir_l, dir_r, dir_u, dir_d,
            fruit_dir_l, 
            fruit_dir_r, 
            fruit_dir_u,
            fruit_dir_d]
            """
        # if mag_new < mag_old: 
            # return self.agent.reward["move_close"]
            
        if self.episode_done:
            return self.agent.reward["death"] 
        if self.isFruit_eaten:
            return self.agent.reward["eat"]
        
        # return self.agent.reward["time_score_decay"] 
        return self.agent.reward["none"] 

    def end_training(self):
        if self.episodes > 1000:
            print("Training complete after 1000 episodes.")
            self.isRunning = False
            pygame.quit()
            sys.exit()


    def reset(self):
        self.env.reset(config.SNAKE_INITIAL_POS, config.SNAKE_INITIAL_DIR, config.SNAKE_SEGMENT_COUNT)
        self.snake = self.env.snake
        self.fruit = self.env.fruit

        if self.score > self.best_score:
            self.best_score = self.score

        self.total_steps += self.steps_per_game
        self.steps_per_game = 0
        self.start_time = None
        self.score = 0
        self.log.fruit_info = []
        self.track_time = True
        self.episode_buffer = {}

        if self.training_enabled: 
            self.episode_done = True

    def extract_info(self) -> tuple[list[int], list[float]]:
        path = self.log.path
        if not os.path.exists(path):
            return [0], [0]
        
        with open(path, "r") as file:
            data = json.load(file)

        scores_array =  [episode["Score"] for episode in data["Episodes"]]
        mean_score_array =  [episode["Mean_score"] for episode in data["Episodes"]]

        return scores_array, mean_score_array
