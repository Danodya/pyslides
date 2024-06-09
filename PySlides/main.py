import pygame

pygame.init()

# game window
SCREEN_WIDTH = 794
SCREEN_HIGHT = 1123
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HIGHT))

run = True
# game loop
while run:

    # event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

pygame.quit()
