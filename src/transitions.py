import pygame

class SlideTransition:
    @staticmethod
    def pull(prev_image, next_image, window_size, screen):
        start_pos = -window_size[1]  # Start above the screen
        end_pos = (window_size[1] - next_image.get_height()) // 2  # End in the center of the screen
        step = 40  # Pixels to move each frame

        y_pos_prev = (window_size[1] - prev_image.get_height()) // 2  # Start at the center for the previous image
        y_pos_next = start_pos  # Start above the screen for the next image

        while y_pos_next < end_pos:
            screen.fill((0, 0, 0))
            if y_pos_prev > start_pos:
                screen.blit(prev_image, ((window_size[0] - prev_image.get_width()) // 2, y_pos_prev))
            screen.blit(next_image, ((window_size[0] - next_image.get_width()) // 2, y_pos_next))
            pygame.display.flip()
            y_pos_prev -= step
            y_pos_next += step
            pygame.time.delay(20)  # Add a small delay to control the speed of the transition

    @staticmethod
    def fade_out_slide_in(prev_image, next_image, window_size, screen):
        start_pos = -window_size[1]  # Start above the screen
        end_pos = (window_size[1] - next_image.get_height()) // 2  # End in the center of the screen
        step = 40  # Pixels to move each frame
        alpha_step = 255 // ((end_pos - start_pos) // step)  # Calculate alpha decrement per frame

        y_pos_next = start_pos  # Start above the screen for the next image
        alpha = 255  # Start with full opacity for the previous image

        while y_pos_next < end_pos:
            screen.fill((0, 0, 0))
            if alpha > 0:
                prev_image.set_alpha(alpha)
                screen.blit(prev_image, ((window_size[0] - prev_image.get_width()) // 2, (window_size[1] - prev_image.get_height()) // 2))
            screen.blit(next_image, ((window_size[0] - next_image.get_width()) // 2, y_pos_next))
            pygame.display.flip()
            y_pos_next += step
            alpha -= alpha_step
            pygame.time.delay(10)  # Add a small delay to control the speed of the transition

    @staticmethod
    def swipe_right(prev_image, next_image, window_size, screen):
        start_pos = -window_size[0]  # Start to the left of the screen
        end_pos = (window_size[0] - next_image.get_width()) // 2  # End in the center of the screen
        step = 40  # Pixels to move each frame

        x_pos_prev = (window_size[0] - prev_image.get_width()) // 2  # Start at the center for the previous image
        x_pos_next = start_pos  # Start to the left of the screen for the next image

        while x_pos_next < end_pos:
            screen.fill((0, 0, 0))
            screen.blit(prev_image, (x_pos_prev, (window_size[1] - prev_image.get_height()) // 2))
            screen.blit(next_image, (x_pos_next, (window_size[1] - next_image.get_height()) // 2))
            pygame.display.flip()
            x_pos_prev += step
            x_pos_next += step
            pygame.time.delay(10)  # Add a small delay to control the speed of the transition

    @staticmethod
    def swipe_left(prev_image, next_image, window_size, screen):
        start_pos = window_size[0]  # Start to the right of the screen
        end_pos = (window_size[0] - next_image.get_width()) // 2  # End in the center of the screen
        step = 40  # Pixels to move each frame

        x_pos_prev = (window_size[0] - prev_image.get_width()) // 2  # Start at the center for the previous image
        x_pos_next = start_pos  # Start to the right of the screen for the next image

        while x_pos_next > end_pos:
            screen.fill((0, 0, 0))
            screen.blit(prev_image, (x_pos_prev, (window_size[1] - prev_image.get_height()) // 2))
            screen.blit(next_image, (x_pos_next, (window_size[1] - next_image.get_height()) // 2))
            pygame.display.flip()
            x_pos_prev -= step
            x_pos_next -= step
            pygame.time.delay(10)  # Add a small delay to control the speed of the transition

    @staticmethod
    def fade_in(prev_image, next_image, window_size, screen):
        start_alpha = 0
        end_alpha = 255
        alpha_step = 20

        alpha = start_alpha
        next_image.set_alpha(alpha)

        while alpha < end_alpha:
            screen.fill((0, 0, 0))
            screen.blit(prev_image, ((window_size[0] - prev_image.get_width()) // 2, (window_size[1] - prev_image.get_height()) // 2))
            screen.blit(next_image, ((window_size[0] - next_image.get_width()) // 2, (window_size[1] - next_image.get_height()) // 2))
            pygame.display.flip()
            alpha += alpha_step
            next_image.set_alpha(alpha)
            pygame.time.delay(25)  # Add a small delay to control the speed of the transition

    @staticmethod
    def choose_transition(prev_image, next_image, window_size, screen, transition_type):
        if transition_type == 'pull':
            SlideTransition.pull(prev_image, next_image, window_size, screen)
        elif transition_type == 'fade_out_slide_in':
            SlideTransition.fade_out_slide_in(prev_image, next_image, window_size, screen)
        elif transition_type == 'swipe_right':
            SlideTransition.swipe_right(prev_image, next_image, window_size, screen)
        elif transition_type == 'swipe_left':
            SlideTransition.swipe_left(prev_image, next_image, window_size, screen)
        elif transition_type == 'fade_in':
            SlideTransition.fade_in(prev_image, next_image, window_size, screen)
