import pygame
import constant

pygame.init()

# game window
screen = pygame.display.set_mode((constant.SCREEN_WIDTH, constant.SCREEN_HIGHT))

pygame.display.set_caption(constant.DISPLAY_CAPTION)


# Function to toggle full screen
def toggle_fullscreen():
    global screen
    if screen.get_flags() & pygame.FULLSCREEN:
        pygame.display.set_mode((constant.SCREEN_WIDTH, constant.SCREEN_HIGHT))
    else:
        pygame.display.set_mode((constant.SCREEN_WIDTH, constant.SCREEN_HIGHT), pygame.FULLSCREEN)

# create a square
player = pygame.Rect((300, 250, 50, 50))

run = True
# game loop
while run:

    # refresh screen to avoid trail of the history
    screen.fill((0, 0, 0))

    # draw the square
    pygame.draw.rect(screen, (255, 0, 0), player)

    # controls
    # get pressed key
    key = pygame.key.get_pressed()
    if key[pygame.K_a] == True:
        player.move_ip(-1, 0)
    elif key[pygame.K_d] == True:
        player.move_ip(1, 0)
    elif key[pygame.K_w] == True:
        player.move_ip(0, -1)
    elif key[pygame.K_s] == True:
        player.move_ip(0, 1)

    # event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:  # Press 'f' to toggle full screen
                toggle_fullscreen()

    # update the window
    pygame.display.flip()

pygame.quit()
