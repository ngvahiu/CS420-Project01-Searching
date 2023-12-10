import time

import pygame
from constants import WINDOW_HEIGHT, WINDOW_WIDTH
from game import Game

# pygame setup
pygame.init()
pygame.display.set_caption("CS420-Project01-Searching")


sc = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
characters = []
for i in range(1, 10):
    character = pygame.image.load("image/character" + str(i)+ ".png")
    character = character.convert_alpha()
    character = pygame.transform.scale(character, (40, 40))
    characters.append(character)
clock = pygame.time.Clock()
running = True

start = time.time()
end = start


game = Game(sc, characters)

# game loop     
while running:
    clock.tick(30)
    event_list = pygame.event.get()
    for event in event_list:
        if event.type == pygame.QUIT:
            running = False

    game.display(event_list)
    pygame.display.flip()


pygame.quit()
