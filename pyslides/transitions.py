import pygame
import time

from pyslides import constant
from pyslides.config.transitions_config_reader import TransitionsConfig


class SlideTransition:
    preset_alpha = 255  # Default opacity value for images

    @staticmethod
    def pull(prev_image, next_image, window_size, screen, duration=1, reverse=False):
        """
         Perform a vertical pull transition between two slides.
        """

        # Record the start and end time for the transition
        start_time = time.time()
        end_time = start_time + duration

        # Define starting position (above the screen) and ending position (centered) for the next image
        start_pos = window_size[1] if reverse else -window_size[1]
        end_pos = (window_size[1] - next_image.get_height()) // 2

        # Define the starting position for the previous image (centered)
        y_pos_prev = (window_size[1] - prev_image.get_height()) // 2

        # # Set full opacity for both images
        # prev_image.set_alpha(SlideTransition.preset_alpha)
        # next_image.set_alpha(SlideTransition.preset_alpha)

        # Perform the pull transition
        while time.time() < end_time:
            elapsed_time = time.time() - start_time
            progress = elapsed_time / duration

            # Calculate current positions for images based on progress
            y_pos_next = start_pos - (start_pos - end_pos) * progress if reverse else start_pos + (
                    end_pos - start_pos) * progress
            # y_pos_prev = y_pos_prev + window_size[1] * progress if reverse else y_pos_prev - window_size[1] * progress
            y_pos_prev = -(window_size[1] - prev_image.get_height()) // 2 + window_size[1] * progress if reverse else \
                (window_size[1] - prev_image.get_height()) // 2 - window_size[1] * progress

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
        """
        Perform a fade-out and slide-in transition between two slides.
        """

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

        # # Set full opacity for both images
        # prev_image.set_alpha(SlideTransition.preset_alpha)
        # next_image.set_alpha(SlideTransition.preset_alpha)

        # Perform the fade out and slide in transition
        while time.time() < end_time:
            # Calculate elapsed time and progress
            elapsed_time = time.time() - start_time
            progress = elapsed_time / duration

            # Calculate current position and alpha based on progress
            y_pos_next = start_pos - (start_pos - end_pos) * progress if reverse else start_pos + (
                    end_pos - start_pos) * progress
            # alpha = 255 * progress if reverse else 255 - (255 * progress)
            alpha = 255 - (255 * progress)

            # Clear screen and draw images at calculated positions with updated alpha
            screen.fill((0, 0, 0))
            if alpha > 0:
                prev_image.set_alpha(int(alpha))
                screen.blit(prev_image, (
                    (window_size[0] - prev_image.get_width()) // 2, (window_size[1] - prev_image.get_height()) // 2))
            screen.blit(next_image, ((window_size[0] - next_image.get_width()) // 2, y_pos_next))
            pygame.display.flip()

            # Delay to control frame rate
            pygame.time.delay(10)

    @staticmethod
    def swipe_right(prev_image, next_image, window_size, screen, duration=1, reverse=False):
        """
        Perform a swipe-right transition between two slides.
        """

        # Record the start and end time for the transition
        start_time = time.time()
        end_time = start_time + duration

        # Define starting position (left of the screen) and ending position (centered) for the next image
        start_pos = window_size[0] if reverse else -window_size[0]
        end_pos = 0  # Centered on the screen

        # Define the starting position for the previous image (centered)
        x_pos_prev = (window_size[0] - prev_image.get_width()) // 2

        # # Set full opacity for both images
        # prev_image.set_alpha(SlideTransition.preset_alpha)
        # next_image.set_alpha(SlideTransition.preset_alpha)

        # Perform the swipe right transition
        while time.time() < end_time:
            # Calculate elapsed time and progress
            elapsed_time = time.time() - start_time
            progress = elapsed_time / duration

            # Calculate current positions for images based on progress
            x_pos_next = start_pos - (start_pos - end_pos) * progress if reverse else start_pos + (
                    end_pos - start_pos) * progress
            x_pos_prev = end_pos - window_size[0] * progress if reverse else (window_size[
                                                                                  0] - prev_image.get_width()) // 2 + \
                                                                             window_size[0] * progress

            # Clear screen and draw images at calculated positions
            screen.fill((0, 0, 0))
            screen.blit(prev_image, (x_pos_prev, (window_size[1] - prev_image.get_height()) // 2))
            screen.blit(next_image, (x_pos_next, (window_size[1] - next_image.get_height()) // 2))
            pygame.display.flip()

            # Delay to control frame rate
            pygame.time.delay(10)

    @staticmethod
    def swipe_left(prev_image, next_image, window_size, screen, duration=1, reverse=False):
        """
        Perform a swipe-left transition between two slides.
        """

        # Record the start and end time for the transition
        start_time = time.time()
        end_time = start_time + duration

        # Define starting position (right of the screen) and ending position (centered) for the next image
        start_pos = -window_size[0] if reverse else window_size[0]
        end_pos = 0  # Centered on the screen

        # Define the starting position for the previous image (centered)
        x_pos_prev = (window_size[0] - prev_image.get_width()) // 2

        # # Set full opacity for both images
        # prev_image.set_alpha(SlideTransition.preset_alpha)
        # next_image.set_alpha(SlideTransition.preset_alpha)

        # Perform the swipe left transition
        while time.time() < end_time:
            elapsed_time = time.time() - start_time
            progress = elapsed_time / duration

            # Calculate current positions for images based on progress
            x_pos_next = start_pos + (end_pos - start_pos) * progress if reverse else start_pos - (
                    start_pos - end_pos) * progress
            x_pos_prev = end_pos + window_size[0] * progress if reverse else (window_size[
                                                                                  0] - prev_image.get_width()) // 2 - \
                                                                             window_size[0] * progress

            # Clear screen and draw images at calculated positions
            screen.fill((0, 0, 0))
            screen.blit(prev_image, (x_pos_prev, (window_size[1] - prev_image.get_height()) // 2))
            screen.blit(next_image, (x_pos_next, (window_size[1] - next_image.get_height()) // 2))
            pygame.display.flip()

            # Delay to control frame rate
            pygame.time.delay(10)

    @staticmethod
    def fade_in(prev_image, next_image, window_size, screen, duration=1, reverse=False):
        """
        Perform a fade-in transition between two slides.
        """

        # Record the start and end time for the transition
        start_time = time.time()
        end_time = start_time + duration

        # Define starting and ending alpha values
        start_alpha = 255 if reverse else 0  # Starting alpha for the next image
        end_alpha = 0 if reverse else 255  # Ending alpha for the next image
        alpha_step = end_alpha / (duration * 100)  # Calculate alpha increment per frame

        # # Set full opacity for the previous image and starting alpha for the next image
        # prev_image.set_alpha(SlideTransition.preset_alpha)
        # next_image.set_alpha(start_alpha)

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
            screen.blit(prev_image, (
                (window_size[0] - prev_image.get_width()) // 2, (window_size[1] - prev_image.get_height()) // 2))
            screen.blit(next_image, (
                (window_size[0] - next_image.get_width()) // 2, (window_size[1] - next_image.get_height()) // 2))
            pygame.display.flip()

            # Delay to control frame rate
            pygame.time.delay(10)

    @staticmethod
    def partial_sliding(prev_image, next_image, window_size, screen, duration=1, reverse=False):
        """
        Perform a partial sliding transition where the next slide slides in partially from the bottom.
        """
        if reverse:
            SlideTransition.choose_transition(prev_image, next_image, window_size, screen,
                                              TransitionsConfig.general_settings["transition"],
                                              float(
                                                  TransitionsConfig.general_settings["transition-duration"]
                                                      .replace('s', '')), reverse=False)
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

            # # Set full opacity for both images
            # prev_image.set_alpha(SlideTransition.preset_alpha)
            # next_image.set_alpha(SlideTransition.preset_alpha)

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
        """
        Choose and apply the appropriate transition method based on the transition type.
        """

        # Reset alpha values to full opacity before starting any transition
        prev_image.set_alpha(SlideTransition.preset_alpha)
        next_image.set_alpha(SlideTransition.preset_alpha)

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

    @staticmethod
    def apply_transition(prev_page, images, state, reverse=False):
        """
        Applies a transition effect between slides, based on the transition configuration.
        """

        # Reset alpha values before applying the transition
        images[prev_page].set_alpha(SlideTransition.preset_alpha)
        images[state.current_page].set_alpha(SlideTransition.preset_alpha)

        transition_config = TransitionsConfig.get_transition_config(state)
        transition_type = transition_config["transition"]  # Get the transition type
        duration = float(transition_config["duration"].replace('s', ''))  # Get the transition duration
        SlideTransition.choose_transition(images[prev_page], images[state.current_page], state.window_size,
                                          state.screen, transition_type,
                                          duration, reverse)  # Apply the transition
        if transition_type == constant.PARTIAL_SLIDE_TRANSITION:
            # Calculate positions for partial slide transitions
            halfway_pos = state.window_size[1] / 4
            prev_start_pos = ((state.window_size[1] - images[prev_page].get_height()) // 2)
            state.prev_slide_position = prev_start_pos - halfway_pos
            state.next_slide_position = state.prev_slide_position + images[prev_page].get_height()
        return state.next_slide_position


def scroll_slide(images, direction, state):
    """
    Scrolls slides up or down for partial slide transitions.
    """
    # global current_page, window_size, screen, prev_slide_position, next_slide_position
    scroll_step = 10  # Pixels to move per scroll step
    image = images[state.current_page - 1]  # Get the previous slide image
    next_image = images[state.current_page]  # Get the current slide image
    end_pos = (state.window_size[1] - next_image.get_height()) // 2  # End scrolling when the main slide is centered
    if (state.prev_slide_position + image.get_height() > end_pos) if direction > 0 else (
            state.prev_slide_position < end_pos):
        prev_start_pos = state.prev_slide_position
        next_start_pos = prev_start_pos + image.get_height()

        y_pos_prev = prev_start_pos - scroll_step * direction  # Update the Y position of the previous slide
        y_pos_next = next_start_pos - scroll_step * direction  # Update the Y position of the next slide

        state.screen.fill((0, 0, 0))  # Clear the screen with black
        state.screen.blit(image,
                          ((state.window_size[0] - image.get_width()) // 2, y_pos_prev))  # Draw the previous slide
        state.screen.blit(next_image,
                          ((state.window_size[0] - next_image.get_width()) // 2, y_pos_next))  # Draw the current slide

        state.prev_slide_position = y_pos_prev  # Update the previous slide position
        state.next_slide_position = y_pos_next  # Update the next slide position


def draw_partial_slide(images, state):
    """
    Draws the slides after partial sliding and after each scrolling action.
    """
    # global window_size, prev_slide_position, next_slide_position
    image = images[state.current_page - 1]  # Get the previous slide image
    next_image = images[state.current_page]  # Get the current slide image

    state.screen.fill((0, 0, 0))  # Clear the screen with black
    state.screen.blit(image, (
        (state.window_size[0] - image.get_width()) // 2, state.prev_slide_position))  # Draw the previous slide
    state.screen.blit(next_image, (
        (state.window_size[0] - next_image.get_width()) // 2, state.next_slide_position))  # Draw the current slide
