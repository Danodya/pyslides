import pygame
import time

from pyslides.config.transitions_config_reader import TransitionsConfig


class SlideTransition:
    preset_alpha = 250  # Default opacity value for images

    @staticmethod
    def pull(prev_image, next_image, window_size, screen, duration=1, reverse=False):
        # Record the start and end time for the transition
        start_time = time.time()
        end_time = start_time + duration

        # Define starting position (above the screen) and ending position (centered) for the next image
        start_pos = window_size[1] if reverse else -window_size[1]
        end_pos = (window_size[1] - next_image.get_height()) // 2

        # Define the starting position for the previous image (centered)
        y_pos_prev = (window_size[1] - prev_image.get_height()) // 2

        # Set full opacity for both images
        prev_image.set_alpha(SlideTransition.preset_alpha)
        next_image.set_alpha(SlideTransition.preset_alpha)

        # Perform the pull transition
        while time.time() < end_time:
            elapsed_time = time.time() - start_time
            progress = elapsed_time / duration

            # Calculate current positions for images based on progress
            y_pos_next = start_pos - (start_pos - end_pos) * progress if reverse else start_pos + (end_pos - start_pos) * progress
            # y_pos_prev = y_pos_prev + window_size[1] * progress if reverse else y_pos_prev - window_size[1] * progress
            y_pos_prev = -(window_size[1] - prev_image.get_height()) // 2 + window_size[1] * progress if reverse else (window_size[1] - prev_image.get_height()) // 2 - window_size[1] * progress

            # Clear screen and draw images at calculated positions
            screen.fill((0, 0, 0))
            if y_pos_prev > start_pos:
                screen.blit(prev_image, ((window_size[0] - prev_image.get_width()) // 2, y_pos_prev))
            screen.blit(next_image, ((window_size[0] - next_image.get_width()) // 2, y_pos_next))
            pygame.display.flip()

            # Delay to control frame rate
            pygame.time.delay(10)

    @staticmethod
    def fade_out_slide_in(prev_image, next_image, window_size, screen, duration=1, reverse=False):
        # Record the start and end time for the transition
        start_time = time.time()
        end_time = start_time + duration

        # Define starting position (above the screen) and ending position (centered) for the next image
        start_pos = window_size[1] if reverse else -window_size[1]
        end_pos = (window_size[1] - next_image.get_height()) // 2
        # Calculate alpha decrement step per frame
        alpha_step = 255 / (duration * 100)

        y_pos_next = start_pos  # Start above the screen for the next image
        alpha = 255  # Start with full opacity for the previous image

        # Set full opacity for both images
        prev_image.set_alpha(SlideTransition.preset_alpha)
        next_image.set_alpha(SlideTransition.preset_alpha)

        # Perform the fade out and slide in transition
        while time.time() < end_time:
            # Calculate elapsed time and progress
            elapsed_time = time.time() - start_time
            progress = elapsed_time / duration

            # Calculate current position and alpha based on progress
            y_pos_next = start_pos - (start_pos - end_pos) * progress if reverse else start_pos + (end_pos - start_pos) * progress
            # alpha = 255 * progress if reverse else 255 - (255 * progress)
            alpha = 255 - (255 * progress)

            # Clear screen and draw images at calculated positions with updated alpha
            screen.fill((0, 0, 0))
            if alpha > 0:
                prev_image.set_alpha(int(alpha))
                screen.blit(prev_image, ((window_size[0] - prev_image.get_width()) // 2, (window_size[1] - prev_image.get_height()) // 2))
            screen.blit(next_image, ((window_size[0] - next_image.get_width()) // 2, y_pos_next))
            pygame.display.flip()

            # Delay to control frame rate
            pygame.time.delay(10)

    @staticmethod
    def swipe_right(prev_image, next_image, window_size, screen, duration=1, reverse=False):
        # Record the start and end time for the transition
        start_time = time.time()
        end_time = start_time + duration

        # Define starting position (left of the screen) and ending position (centered) for the next image
        start_pos = window_size[0] if reverse else -window_size[0]
        end_pos = 0  # Centered on the screen

        # Define the starting position for the previous image (centered)
        x_pos_prev = (window_size[0] - prev_image.get_width()) // 2

        # Set full opacity for both images
        prev_image.set_alpha(SlideTransition.preset_alpha)
        next_image.set_alpha(SlideTransition.preset_alpha)

        # Perform the swipe right transition
        while time.time() < end_time:
            # Calculate elapsed time and progress
            elapsed_time = time.time() - start_time
            progress = elapsed_time / duration

            # Calculate current positions for images based on progress
            x_pos_next = start_pos - (start_pos - end_pos) * progress if reverse else start_pos + (end_pos - start_pos) * progress
            x_pos_prev = end_pos - window_size[0] * progress if reverse else (window_size[0] - prev_image.get_width()) // 2 + window_size[0] * progress

            # Clear screen and draw images at calculated positions
            screen.fill((0, 0, 0))
            screen.blit(prev_image, (x_pos_prev, (window_size[1] - prev_image.get_height()) // 2))
            screen.blit(next_image, (x_pos_next, (window_size[1] - next_image.get_height()) // 2))
            pygame.display.flip()

            # Delay to control frame rate
            pygame.time.delay(10)

    @staticmethod
    def swipe_left(prev_image, next_image, window_size, screen, duration=1, reverse=False):
        # Record the start and end time for the transition
        start_time = time.time()
        end_time = start_time + duration

        # Define starting position (right of the screen) and ending position (centered) for the next image
        start_pos = -window_size[0] if reverse else window_size[0]
        end_pos = 0  # Centered on the screen

        # Define the starting position for the previous image (centered)
        x_pos_prev = (window_size[0] - prev_image.get_width()) // 2

        # Set full opacity for both images
        prev_image.set_alpha(SlideTransition.preset_alpha)
        next_image.set_alpha(SlideTransition.preset_alpha)

        # Perform the swipe left transition
        while time.time() < end_time:
            elapsed_time = time.time() - start_time
            progress = elapsed_time / duration

            # Calculate current positions for images based on progress
            x_pos_next = start_pos + (end_pos - start_pos) * progress if reverse else start_pos - (start_pos - end_pos) * progress
            x_pos_prev = end_pos + window_size[0] * progress if reverse else (window_size[0] - prev_image.get_width()) // 2 - window_size[0] * progress

            # Clear screen and draw images at calculated positions
            screen.fill((0, 0, 0))
            screen.blit(prev_image, (x_pos_prev, (window_size[1] - prev_image.get_height()) // 2))
            screen.blit(next_image, (x_pos_next, (window_size[1] - next_image.get_height()) // 2))
            pygame.display.flip()

            # Delay to control frame rate
            pygame.time.delay(10)

    @staticmethod
    def fade_in(prev_image, next_image, window_size, screen, duration=1, reverse=False):
        # Record the start and end time for the transition
        start_time = time.time()
        end_time = start_time + duration

        # Define starting and ending alpha values
        start_alpha = 255 if reverse else 0  # Starting alpha for the next image
        end_alpha = 0 if reverse else 255  # Ending alpha for the next image
        alpha_step = end_alpha / (duration * 100)  # Calculate alpha increment per frame

        # Set full opacity for the previous image and starting alpha for the next image
        prev_image.set_alpha(SlideTransition.preset_alpha)
        next_image.set_alpha(start_alpha)

        # Perform the fade in transition
        while time.time() < end_time:
            # Calculate elapsed time and current alpha based on progress
            elapsed_time = time.time() - start_time
            progress = elapsed_time / duration
            alpha = start_alpha + (end_alpha - start_alpha) * progress

            # Clear screen and draw images with updated alpha
            screen.fill((0, 0, 0))
            prev_image.set_alpha(int(255 - alpha) if not reverse else int(alpha))
            next_image.set_alpha(int(alpha) if not reverse else int(255 - alpha))
            screen.blit(prev_image, ((window_size[0] - prev_image.get_width()) // 2, (window_size[1] - prev_image.get_height()) // 2))
            screen.blit(next_image, ((window_size[0] - next_image.get_width()) // 2, (window_size[1] - next_image.get_height()) // 2))
            pygame.display.flip()

            # Delay to control frame rate
            pygame.time.delay(10)

    @staticmethod
    def partial_sliding(prev_image, next_image, window_size, screen, duration=1, reverse=False):
        if reverse:
            SlideTransition.choose_transition(prev_image, next_image, window_size, screen, TransitionsConfig.general_settings["transition"],
                              float(TransitionsConfig.general_settings["transition-duration"].replace('s', '')), reverse=False)
            # SlideTransition.fade_in(prev_image, next_image, window_size, screen, duration)
        else:
            # Record the start and end time for the transition
            start_time = time.time()
            end_time = start_time + duration

            # Calculate start and end positions for both images
            prev_start_pos = (window_size[1] - prev_image.get_height()) // 2
            next_start_pos = window_size[1]
            halfway_pos = window_size[1] / 4

            # Distance the next slide needs to move
            distance_to_move = next_start_pos - (prev_start_pos + prev_image.get_height())

            # Set full opacity for both images
            prev_image.set_alpha(SlideTransition.preset_alpha)
            next_image.set_alpha(SlideTransition.preset_alpha)

            # Perform the partial sliding transition
            while time.time() < end_time:
                elapsed_time = time.time() - start_time
                progress = elapsed_time / duration

                # Move previous image up halfway and next image up from the bottom to just below the previous image
                y_pos_prev = prev_start_pos - halfway_pos * progress

                # Calculate current vertical position of the next slide
                y_pos_next = next_start_pos - (halfway_pos + distance_to_move) * progress

                screen.fill((0, 0, 0))
                screen.blit(prev_image, ((window_size[0] - prev_image.get_width()) // 2, y_pos_prev))
                screen.blit(next_image, ((window_size[0] - next_image.get_width()) // 2, y_pos_next))
                pygame.display.flip()
                pygame.time.delay(10)

    @staticmethod
    def choose_transition(prev_image, next_image, window_size, screen, transition_type, duration, reverse=False):
        # Call the appropriate transition method based on the transition type
        if transition_type == 'pull':
            SlideTransition.pull(prev_image, next_image, window_size, screen, duration, reverse)
        elif transition_type == 'fade_out_slide_in':
            SlideTransition.fade_out_slide_in(prev_image, next_image, window_size, screen, duration, reverse)
        elif transition_type == 'swipe_right':
            SlideTransition.swipe_right(prev_image, next_image, window_size, screen, duration, reverse)
        elif transition_type == 'swipe_left':
            SlideTransition.swipe_left(prev_image, next_image, window_size, screen, duration, reverse)
        elif transition_type == 'partial_sliding':
            SlideTransition.partial_sliding(prev_image, next_image, window_size, screen, duration, reverse=reverse)
        elif transition_type == 'fade_in':
            SlideTransition.fade_in(prev_image, next_image, window_size, screen, duration, reverse)
