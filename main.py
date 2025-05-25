import pygame
from pygame.locals import *
from game import Game

pygame.init()
pygame.font.init()

if __name__ == "__main__":

    game = Game()
    game.run()