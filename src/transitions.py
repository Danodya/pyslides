import pygame
import time

class SlideTransition:
    preset_alpha = 250

    @staticmethod
    def pull(prev_image, next_image, window_size, screen, duration=1):
        start_time = time.time()
        end_time = start_time + duration

        start_pos = -window_size[1]  # Start above the screen
        end_pos = (window_size[1] - next_image.get_height()) // 2  # End in the center of the screen

        y_pos_prev = (window_size[1] - prev_image.get_height()) // 2  # Start at the center for the previous image

        # Make the previous slide opacity full
        prev_image.set_alpha(SlideTransition.preset_alpha)
        next_image.set_alpha(SlideTransition.preset_alpha)

        while time.time() < end_time:
            elapsed_time = time.time() - start_time
            progress = elapsed_time / duration

            y_pos_next = start_pos + (end_pos - start_pos) * progress
            y_pos_prev = (window_size[1] - prev_image.get_height()) // 2 - window_size[1] * progress

            screen.fill((0, 0, 0))
            if y_pos_prev > start_pos:
                screen.blit(prev_image, ((window_size[0] - prev_image.get_width()) // 2, y_pos_prev))
            screen.blit(next_image, ((window_size[0] - next_image.get_width()) // 2, y_pos_next))
            pygame.display.flip()

            pygame.time.delay(10)

    @staticmethod
    def fade_out_slide_in(prev_image, next_image, window_size, screen, duration=1):
        start_time = time.time()
        end_time = start_time + duration

        start_pos = -window_size[1]  # Start above the screen
        end_pos = (window_size[1] - next_image.get_height()) // 2  # End in the center of the screen
        alpha_step = 255 / (duration * 100)  # Calculate alpha decrement per frame

        y_pos_next = start_pos  # Start above the screen for the next image
        alpha = 255  # Start with full opacity for the previous image

        # Make the previous slide opacity full
        prev_image.set_alpha(SlideTransition.preset_alpha)
        next_image.set_alpha(SlideTransition.preset_alpha)

        while time.time() < end_time:
            elapsed_time = time.time() - start_time
            progress = elapsed_time / duration

            y_pos_next = start_pos + (end_pos - start_pos) * progress
            alpha = 255 - (255 * progress)

            screen.fill((0, 0, 0))
            if alpha > 0:
                prev_image.set_alpha(int(alpha))
                screen.blit(prev_image, ((window_size[0] - prev_image.get_width()) // 2, (window_size[1] - prev_image.get_height()) // 2))
            screen.blit(next_image, ((window_size[0] - next_image.get_width()) // 2, y_pos_next))
            pygame.display.flip()

            pygame.time.delay(10)

    @staticmethod
    def swipe_right(prev_image, next_image, window_size, screen, duration=1):
        start_time = time.time()
        end_time = start_time + duration

        start_pos = -window_size[0]  # Start to the left of the screen
        end_pos = 0  # End in the center of the screen

        x_pos_prev = (window_size[0] - prev_image.get_width()) // 2  # Start at the center for the previous image

        # Make the previous slide opacity full
        prev_image.set_alpha(SlideTransition.preset_alpha)
        next_image.set_alpha(SlideTransition.preset_alpha)

        while time.time() < end_time:
            elapsed_time = time.time() - start_time
            progress = elapsed_time / duration

            x_pos_next = start_pos + (end_pos - start_pos) * progress
            x_pos_prev = (window_size[0] - prev_image.get_width()) // 2 + window_size[0] * progress

            screen.fill((0, 0, 0))
            screen.blit(prev_image, (x_pos_prev, (window_size[1] - prev_image.get_height()) // 2))
            screen.blit(next_image, (x_pos_next, (window_size[1] - next_image.get_height()) // 2))
            pygame.display.flip()

            pygame.time.delay(10)

    @staticmethod
    def swipe_left(prev_image, next_image, window_size, screen, duration=1):
        start_time = time.time()
        end_time = start_time + duration

        start_pos = window_size[0]  # Start to the right of the screen
        end_pos = 0  # End in the center of the screen

        x_pos_prev = (window_size[0] - prev_image.get_width()) // 2  # Start at the center for the previous image

        # Make the previous slide opacity full
        prev_image.set_alpha(SlideTransition.preset_alpha)
        next_image.set_alpha(SlideTransition.preset_alpha)

        while time.time() < end_time:
            elapsed_time = time.time() - start_time
            progress = elapsed_time / duration

            x_pos_next = start_pos - (start_pos - end_pos) * progress
            x_pos_prev = (window_size[0] - prev_image.get_width()) // 2 - window_size[0] * progress

            screen.fill((0, 0, 0))
            screen.blit(prev_image, (x_pos_prev, (window_size[1] - prev_image.get_height()) // 2))
            screen.blit(next_image, (x_pos_next, (window_size[1] - next_image.get_height()) // 2))
            pygame.display.flip()

            pygame.time.delay(10)

    @staticmethod
    def fade_in(prev_image, next_image, window_size, screen, duration=1):
        start_time = time.time()
        end_time = start_time + duration

        start_alpha = 0
        end_alpha = 255
        alpha_step = end_alpha / (duration * 100)

        # Make the previous slide opacity full
        prev_image.set_alpha(SlideTransition.preset_alpha)
        next_image.set_alpha(start_alpha)

        while time.time() < end_time:
            elapsed_time = time.time() - start_time
            alpha = start_alpha + (end_alpha - start_alpha) * (elapsed_time / duration)

            screen.fill((0, 0, 0))
            screen.blit(prev_image, ((window_size[0] - prev_image.get_width()) // 2, (window_size[1] - prev_image.get_height()) // 2))
            next_image.set_alpha(int(alpha))
            screen.blit(next_image, ((window_size[0] - next_image.get_width()) // 2, (window_size[1] - next_image.get_height()) // 2))
            pygame.display.flip()

            pygame.time.delay(10)

    @staticmethod
    def choose_transition(prev_image, next_image, window_size, screen, transition_type, duration):
        if transition_type == 'pull':
            SlideTransition.pull(prev_image, next_image, window_size, screen, duration)
        elif transition_type == 'fade_out_slide_in':
            SlideTransition.fade_out_slide_in(prev_image, next_image, window_size, screen, duration)
        elif transition_type == 'swipe_right':
            SlideTransition.swipe_right(prev_image, next_image, window_size, screen, duration)
        elif transition_type == 'swipe_left':
            SlideTransition.swipe_left(prev_image, next_image, window_size, screen, duration)
        elif transition_type == 'fade_in':
            SlideTransition.fade_in(prev_image, next_image, window_size, screen, duration)
