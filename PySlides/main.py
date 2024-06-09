import pygame

pygame.init()

# game window
SCREEN_WIDTH = 794
SCREEN_HIGHT = 1123
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HIGHT))

# create a square
player = pygame.Rect((300, 250, 50, 50))

run = True
# game loop
while run:

    # draw the square
    pygame.draw.rect(screen, (255, 0, 0), player)

    # event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # update window to display the square
    pygame.display.update()

pygame.quit()
