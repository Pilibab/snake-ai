import pygame
from pygame.locals import *
from game import Game

pygame.init()
pygame.font.init()
pygame.display.set_caption("SNAKE AI (DEEP-Q)")

if __name__ == "__main__":

    game = Game()
    game.run()