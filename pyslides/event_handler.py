import time

import pygame

from pyslides import constant
from pyslides.annotations import adjust_annotation_rect
from pyslides.config.annotations_config import AnnotationsConfig
from pyslides.config.transitions_config_reader import TransitionsConfig
from pyslides.display import display_slide, select_thumbnail, highlight_thumbnail, toggle_fullscreen
from pyslides.transitions import SlideTransition, scroll_slide


def handle_keydown(event, images, pdf_file, state):
    """
    Handles keydown events, such as navigating slides, toggling modes, and managing annotations.
    """

    if state.end_of_presentation and event.key != pygame.K_LEFT:
        return  # Ignore key presses if the presentation has ended, except for the left arrow key

    if state.is_entering_text:
        # Handle text entry for annotations
        if event.key == pygame.K_RETURN:  # Stop entering text mode with 'Enter' key
            if state.current_page not in state.text_annotations:
                state.text_annotations[state.current_page] = []
            state.text_annotations[state.current_page].append((state.annotation_rect, state.current_text))
            state.current_text = ""
            state.annotation_rect = None
            state.is_entering_text = False
            return
        elif event.key == pygame.K_BACKSPACE:
            # Handle backspace key to delete characters
            state.current_text = state.current_text[:-1]
        else:
            # Add the typed character to the current text
            state.current_text += event.unicode
            adjust_annotation_rect(state)  # Adjust the annotation rectangle as text is entered
        return  # Exit to avoid processing other keys while entering text

    if event.key == pygame.K_h:
        # Toggle help screen visibility
        state.show_help = not state.show_help
        state.show_initial_help_popup = False
        state.is_drawing_pen = False  # Disable pen mode when help is shown
    elif state.show_help:
        return  # Ignore other key presses when the help screen is active

    if event.key == pygame.K_RIGHT or event.key == pygame.K_PAGEDOWN:  # 'Page Down' for clickers
        if state.black_screen_mode:
            state.black_screen_mode = not state.black_screen_mode
        if state.show_overview:
            # Navigate to the next slide in overview mode
            state.focused_page = (state.focused_page + 1) % len(images)
        else:
            # Navigate to the next slide
            prev_page = state.current_page
            state.current_page = (state.current_page + 1)
            if state.current_page >= len(images):
                state.end_of_presentation = True
            else:
                state.next_slide_position = SlideTransition.apply_transition(prev_page, images,
                                                                             state, reverse=False)
            state.zoom_level = 1.0  # Reset zoom level on slide change
            state.current_highlights.clear()  # Clear any highlights
    elif event.key == pygame.K_LEFT or event.key == pygame.K_PAGEUP:  # 'Page Up' for clickers
        if state.black_screen_mode:
            state.black_screen_mode = not state.black_screen_mode
        if state.show_overview:
            # Navigate to the previous slide in overview mode
            state.focused_page = (state.focused_page - 1) % len(images)
        else:
            if state.end_of_presentation:
                state.current_page = len(images) - 1
                prev_page = state.current_page
                state.end_of_presentation = False
            else:
                prev_page = state.current_page
                state.current_page = (state.current_page - 1)
                if state.current_page < 0:
                    state.current_page = 0
            state.zoom_level = 1.0  # Reset zoom level on slide change
            state.current_highlights.clear()  # Clear any highlights
            transition_config_current = TransitionsConfig.get_transition_config(state)
            reversal_strategy = transition_config_current["reversal-strategy"]
            if reversal_strategy != constant.NONE:
                state.next_slide_position = SlideTransition.apply_transition(prev_page, images, state,
                                                                             TransitionsConfig.check_reversal_strategy(
                                                                                 reversal_strategy))
            else:
                display_slide(images, state)
    elif event.key == pygame.K_f:
        # Toggle fullscreen mode
        state.original_image_size = images[state.current_page].get_size()
        prev_window_size = state.screen.get_size()
        toggle_fullscreen(images, prev_window_size, state)
    elif event.key == pygame.K_TAB:
        state.show_overview = not state.show_overview  # Toggle overview mode
    elif event.key == pygame.K_RETURN and state.show_overview:
        # Select the slide in overview mode
        state.current_page = state.focused_page
        state.show_overview = False
    elif event.key == pygame.K_UP:
        # Scroll up in partial slide transition
        transition_config_prev = TransitionsConfig.get_transition_config(state)
        transition_type_prev = transition_config_prev["transition"]
        state.scrolling = transition_type_prev == constant.PARTIAL_SLIDE_TRANSITION
        state.scroll_direction = -1  # Scroll up
        state.scroll_start_time = time.time()
    elif event.key == pygame.K_DOWN:
        # Scroll down in partial slide transition
        transition_config_prev = TransitionsConfig.get_transition_config(state)
        transition_type_prev = transition_config_prev["transition"]
        state.scrolling = transition_type_prev == constant.PARTIAL_SLIDE_TRANSITION
        state.scroll_direction = 1  # Scroll down
        state.scroll_start_time = time.time()
    elif event.key == pygame.K_s:
        # Toggle spotlight mode or save annotations with Ctrl + S
        if pygame.key.get_mods() & pygame.KMOD_CTRL:
            AnnotationsConfig.save_annotations_to_json(images[state.current_page], state,
                                                       pdf_file)  # Save annotations when Ctrl + S is pressed
        else:
            state.spotlight_mode = not state.spotlight_mode
            if state.spotlight_mode:
                state.highlight_mode = False  # Turn off highlight mode if spotlight mode is enabled
    elif event.key == pygame.K_r:
        # Toggle highlight mode
        if state.highlight_mode:
            state.current_highlights.clear()  # Clear current highlights
        state.spotlight_mode = False  # Turn off spotlight mode if highlight mode is enabled
        state.highlight_mode = not state.highlight_mode
        state.highlight_start = None  # Reset highlight start position
    elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
        # Increase spotlight radius
        if state.spotlight_mode:
            state.spotlight_radius = min(state.spotlight_radius + 10, state.window_size[1])
    elif event.key == pygame.K_MINUS:
        # Decrease spotlight radius
        if state.spotlight_mode:
            state.spotlight_radius = max(state.spotlight_radius - 10, 10)
    elif event.key == pygame.K_PERIOD:
        # Toggle black screen mode
        state.black_screen_mode = not state.black_screen_mode
    elif event.key == pygame.K_t:
        # Toggle text annotation mode
        state.is_drawing_pen = False  # Disable pen mode when text annotations are enabled
        if not state.show_overview and state.zoom_level == 1:
            if state.is_entering_text:  # Stop entering text mode
                if state.current_page not in state.text_annotations:
                    state.text_annotations[state.current_page] = []
                state.text_annotations[state.current_page].append((state.annotation_rect, state.current_text))
                state.current_text = ""
                state.annotation_rect = None
                state.is_entering_text = False
            else:  # Start drawing a box for text annotation
                for rect, text in state.text_annotations.get(state.current_page, []):
                    if rect.collidepoint(pygame.mouse.get_pos()):
                        state.annotation_rect = rect
                        state.current_text = text
                        state.text_annotations[state.current_page].remove((rect, text))
                        state.is_entering_text = True
                        break
                else:
                    state.is_drawing_box = True
                    state.annotation_start = pygame.mouse.get_pos()  # Capture the starting position for the annotation box
                    state.current_text = ""  # Initialize an empty text string
    elif event.key == pygame.K_p:
        # Toggle pen mode for freehand drawing
        if not state.show_overview and state.zoom_level == 1:
            state.is_drawing_pen = not state.is_drawing_pen  # Toggle pen drawing mode
            if not state.is_drawing_pen and state.pen_points:
                if state.current_page not in state.pen_annotations:
                    state.pen_annotations[state.current_page] = []
                state.pen_annotations[state.current_page].append(state.pen_points)
                pen_points = []


def handle_keyup(event, state):
    """
    Handles keyup events, specifically to stop scrolling.
    """
    # global scrolling, scroll_direction

    # Stop scrolling when the up or down arrow key is released
    if event.key in (pygame.K_UP, pygame.K_DOWN):
        state.scrolling = False
        state.scroll_direction = 0


def handle_mouse(event, images, state):
    """
    Handles mouse events, including clicks, drags, and scrolls for interactions with slides.
    """

    if state.end_of_presentation:
        return  # Ignore mouse events if the presentation has ended

    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:  # Left mouse button
            print("Mouse button down detected!")
            if state.black_screen_mode:
                state.black_screen_mode = not state.black_screen_mode
            if state.is_entering_text:
                return  # Ignore clicks while entering text
            if state.show_overview:
                # Select a slide thumbnail in overview mode
                select_thumbnail(event.pos, images, state)
            elif state.highlight_mode:
                # Start drawing a highlight rectangle
                state.highlight_start = event.pos
            elif state.is_drawing_box:
                # Start drawing an annotation box
                state.annotation_start = event.pos
                state.is_drawing_box = True
                state.annotation_rect = None
            elif state.is_drawing_pen:
                # Start drawing a pen stroke
                state.pen_points.append(event.pos)
            else:
                # Check if an annotation is being dragged
                for rect, text in state.text_annotations.get(state.current_page, []):
                    if rect.collidepoint(event.pos):
                        state.dragging = True
                        state.annotation_rect = rect
                        state.current_text = text
                        state.text_annotations[state.current_page].remove((rect, text))
                        break
                else:
                    # Navigate to the next slide on left-click
                    prev_page = state.current_page
                    state.current_page = (state.current_page + 1)
                    state.zoom_level = 1.0  # Reset zoom level on slide change
                    state.current_highlights.clear()
                    if state.current_page >= len(images):
                        state.end_of_presentation = True
                    else:
                        state.next_slide_position = SlideTransition.apply_transition(prev_page, images,
                                                                                     state,
                                                                                     reverse=False)
        elif event.button == 3 and not state.show_overview:  # Right mouse button and not in overview mode
            # Go to the previous slide
            if state.black_screen_mode:
                state.black_screen_mode = not state.black_screen_mode
            if state.end_of_presentation:
                state.current_page = len(images) - 1
                prev_page = state.current_page
                state.end_of_presentation = False
            else:
                prev_page = state.current_page
                state.current_page = (state.current_page - 1)
                if state.current_page < 0:
                    state.current_page = 0
            state.zoom_level = 1.0  # Reset zoom level on slide change
            state.current_highlights.clear()
            transition_config_current = TransitionsConfig.get_transition_config(state)
            reversal_strategy = transition_config_current["reversal-strategy"]
            if reversal_strategy != constant.NONE:
                state.next_slide_position = SlideTransition.apply_transition(prev_page, images,
                                                                             state,
                                                                             TransitionsConfig.
                                                                             check_reversal_strategy(reversal_strategy))
            else:
                display_slide(images, state)
        elif event.button == 4:  # Scroll up (mouse wheel up)
            if pygame.key.get_mods() & pygame.KMOD_CTRL:  # Check if Ctrl key is pressed
                state.is_drawing_pen = False
                state.zoom_level = min(state.zoom_level * 1.25, state.max_zoom_level)  # Increase zoom level
                state.zoom_pos = event.pos
            else:
                transition_config_prev = TransitionsConfig.get_transition_config(state)
                transition_type_prev = transition_config_prev["transition"]
                if transition_type_prev == constant.PARTIAL_SLIDE_TRANSITION:
                    scroll_slide(images, -1, state)  # Scroll up
        elif event.button == 5:  # Scroll down (mouse wheel down)
            if pygame.key.get_mods() & pygame.KMOD_CTRL:  # Check if Ctrl key is pressed
                state.is_drawing_pen = False
                state.zoom_level = max(state.zoom_level / 1.25, state.min_zoom_level)  # Decrease zoom level
                state.zoom_pos = event.pos
            else:
                transition_config_prev = TransitionsConfig.get_transition_config(state)
                transition_type_prev = transition_config_prev["transition"]
                if transition_type_prev == constant.PARTIAL_SLIDE_TRANSITION:
                    scroll_slide(images, 1, state)  # Scroll down
    elif event.type == pygame.MOUSEMOTION:
        if state.show_overview:
            highlight_thumbnail(event.pos, images, state)  # Highlight a slide thumbnail in overview mode
        if state.spotlight_mode:
            state.spotlight_position = event.pos  # Update spotlight position
        if state.highlight_mode and state.highlight_start:
            # Draw a highlight rectangle as the mouse is dragged
            x1, y1 = state.highlight_start
            x2, y2 = event.pos
            highlight_rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x1 - x2), abs(y1 - y2))
            state.current_highlights.append(highlight_rect)
        if state.zoom_level > 1:
            state.zoom_pos = event.pos  # Update zoom position
        if state.is_drawing_box and state.annotation_start:
            # Update the size of the annotation box as the mouse is dragged
            x1, y1 = state.annotation_start
            x2, y2 = event.pos
            state.annotation_rect = pygame.Rect(x1, y1, abs(x1 - x2), abs(y1 - y2))  # Keep width constant
        if state.dragging and state.annotation_rect:
            # Move the annotation box as the mouse is dragged
            state.annotation_rect.topleft = event.pos
        if state.is_drawing_pen and event.buttons[0]:  # Check if the left mouse button is held down
            state.pen_points.append(event.pos)  # Add points to the pen stroke
    elif event.type == pygame.MOUSEBUTTONUP:
        if event.button == 1 and state.is_drawing_box:
            state.is_drawing_box = False
            state.is_entering_text = True  # Now enter text mode
        if event.button == 1 and state.dragging:
            state.dragging = False
            state.text_annotations[state.current_page].append(
                (state.annotation_rect, state.current_text))  # Save the dragged annotation
            state.annotation_rect = None
            state.current_text = ""
        if event.button == 1 and state.is_drawing_pen and len(state.pen_points) > 1:
            if state.current_page not in state.pen_annotations:
                state.pen_annotations[state.current_page] = []
            state.pen_annotations[state.current_page].append(state.pen_points)  # Save the pen stroke
            state.pen_points = []
        if event.button == 1 and state.highlight_mode and state.highlight_start:
            x1, y1 = state.highlight_start
            x2, y2 = event.pos
            state.highlight_rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x1 - x2), abs(y1 - y2))
            state.current_highlights.append(state.highlight_rect)  # Save the highlight rectangle
            state.highlight_start = None
