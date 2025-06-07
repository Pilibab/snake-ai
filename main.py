import pygame
from game import Game
from snakeAgent import Agent

pygame.init()
pygame.font.init()
pygame.display.set_caption("SNAKE AI (DEEP-Q)")

# def main()

if __name__ == "__main__":
    agent = Agent()
    game = Game(agent)
    game.run()