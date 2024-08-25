import argparse
import copy
import sys
import fitz  # PyMuPDF for PDF processing
import pygame
import os
import json
from pathlib import Path
import pyslides.constant as constant
from pyslides.transitions import SlideTransition
from pyslides.config.transitions_config_reader import TransitionsConfig
import time

# Ensure the pyslides directory is in the Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pyslides'))

# Define the initial window size
original_window_size = (constant.SCREEN_WIDTH, constant.SCREEN_HIGHT)
window_size = original_window_size
fullscreen_window_size = original_window_size  # initialized to original window size
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption(constant.DISPLAY_CAPTION)

# Initialize Pygame's font module for text rendering
pygame.font.init()
font = pygame.font.Font(None, 36)  # Default font, size 36 for general text
annotation_font = pygame.font.SysFont("timesnewroman", 18)  # Font for annotations

# Global state variables to track various modes and states in the presentation
is_fullscreen = False  # Track whether fullscreen mode is active
show_overview = False  # Track whether overview mode is active
current_page = 0  # Track the current slide being displayed
focused_page = 0  # Track the currently highlighted slide in overview mode
prev_slide_position = 0  # Y position of the previous slide during partial slide transition
next_slide_position = 0  # Y position of the next slide during partial slide transition
scrolling = False  # Flag to indicate if scrolling is active (for partial slides)
scroll_direction = 0  # Direction of scrolling: -1 for up, 1 for down
scroll_start_time = 0  # Time when scrolling started
spotlight_mode = False  # Flag to indicate if spotlight mode is active
highlight_mode = False  # Flag to indicate if highlight mode is active
highlight_start = None  # Start position for the highlight rectangle
highlight_rects = {}  # Store highlight rectangles per slide
current_highlights = []  # Current highlights being drawn
spotlight_radius = 100  # Initial spotlight radius
spotlight_position = (window_size[0] // 2, window_size[1] // 2)  # Initial spotlight position
end_of_presentation = False  # Flag to indicate the end of the presentation
show_help = False  # Flag to indicate if help screen is active
show_initial_help_popup = True  # Flag to show the initial help popup
zoom_level = 1  # Initial zoom level (1 = no zoom)
max_zoom_level = 4  # Maximum zoom level allowed
min_zoom_level = 1  # Minimum zoom level allowed
zoom_pos = (0, 0)  # Position around which zoom is centered
black_screen_mode = False  # Flag to indicate if black screen mode is active

# Global variables for text annotation
is_drawing_box = False  # Flag to indicate if an annotation box is being drawn
annotation_start = None  # Starting position for drawing the annotation box
annotation_rect = None  # Rectangle defining the annotation area
is_entering_text = False  # Flag to indicate if text is being entered
current_text = ""  # Current text being entered in the annotation
text_annotations = {}  # Store list of (rect, text) per slide
dragging = False  # Flag for dragging the annotation box

# Global variables for pen annotations
is_drawing_pen = False  # Flag to indicate if pen mode is active
pen_points = []  # Store points for the current pen stroke
pen_annotations = {}  # Store list of pen points per slide
original_image_size = []  # Store the original size of the images

def toggle_fullscreen(images, prev_window_size):
    """
    Toggles fullscreen mode on and off, rescaling images and annotations as needed.
    """
    global screen, window_size, is_fullscreen, original_image_size, prev_slide_position, next_slide_position
    global fullscreen_window_size, text_annotations, pen_annotations

    # Toggle fullscreen state
    is_fullscreen = not is_fullscreen
    if is_fullscreen:
        # Set the screen to fullscreen mode
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        fullscreen_window_size = screen.get_size()  # Update fullscreen window size
    else:
        # Set the screen back to windowed mode
        screen = pygame.display.set_mode(original_window_size)

    new_window_size = screen.get_size()  # Get the new window size

    # Update the images to fit the new window size and track the new image size
    images[:] = [scale_image_to_fit(pygame.image.load(img_path), new_window_size) for img_path in image_paths]
    new_image_size = images[0].get_size()

    # Rescale annotations to match the new image size
    text_annotations, pen_annotations = rescale_annotations(new_image_size, original_image_size, new_window_size, prev_window_size, is_fullscreen)

    window_size = new_window_size  # Update global window size
    original_image_size = new_image_size  # Update the original image size to the new one

    # Recalculate slide positions if partial transition is active
    if current_page != 0 and (scrolling or constant.PARTIAL_SLIDE_TRANSITION ==
                              TransitionsConfig.get_transition_config(slide_transitions, current_page)["transition"]):
        halfway_pos = window_size[1] / 4
        prev_start_pos = ((window_size[1] - images[current_page - 1].get_height()) // 2)
        prev_slide_position = prev_start_pos - halfway_pos
        next_slide_position = prev_slide_position + images[current_page - 1].get_height()

def rescale_annotations(new_size, original_size, new_window_size, original_window_size, is_fullscreen = False):
    """
    Rescales text and pen annotations when the window size or fullscreen mode changes.
    """
    global text_annotations, pen_annotations
    # Create deep copies of the annotations to avoid modifying the originals
    rescaled_text_annotations, rescaled_pen_annotations = copy.deepcopy(text_annotations), copy.deepcopy(pen_annotations)
    if original_size:

        width_scale = new_size[0] / original_size[0]  # Calculate the width scaling factor
        height_scale = new_size[1] / original_size[1]  # Calculate the height scaling factor

        # Adjust text annotations
        for page, annotations in rescaled_text_annotations.items():
            for i, (rect, text) in enumerate(annotations):
                if is_fullscreen:
                    # Adjust annotation position for fullscreen mode
                    x_adjust = ((new_window_size[0] - new_size[0]) / 2)
                    y_adjust = ((original_window_size[1] - original_image_size[1]) / 2)
                    new_rect = pygame.Rect(
                        int(round(x_adjust + rect.left * width_scale)),
                        int(round((rect.top - y_adjust) * height_scale)),
                        int(round(rect.width * width_scale)),
                        int(round(rect.height * height_scale))
                    )
                else:
                    # Adjust annotation position for windowed mode
                    x_adjust = ((original_window_size[0] - original_size[0]) / 2)
                    y_adjust = ((new_window_size[1] - new_size[1]) / 2)
                    new_rect = pygame.Rect(
                        int(round((rect.left - x_adjust) * width_scale)),
                        int(round((rect.top * height_scale) + y_adjust)),
                        int(round(rect.width * width_scale)),
                        int(round(rect.height * height_scale))
                    )

                # Update the annotation with the new position and size
                rescaled_text_annotations[page][i] = (new_rect, text)

        # Adjust pen annotations
        for page, pen_strokes in rescaled_pen_annotations.items():
            for stroke in pen_strokes:
                for i, (x, y) in enumerate(stroke):
                    if is_fullscreen:
                        # Adjust pen stroke position for fullscreen mode
                        x_adjust = ((new_window_size[0] - new_size[0]) / 2)
                        y_adjust = ((original_window_size[1] - original_image_size[1]) / 2)
                        stroke[i] = (int(round(x_adjust + x * width_scale)), int(round((y - y_adjust) * height_scale)))
                    else:
                        # Adjust pen stroke position for windowed mode
                        x_adjust = ((original_window_size[0] - original_size[0]) / 2)
                        y_adjust = ((new_window_size[1] - new_size[1]) / 2)
                        stroke[i] = (int(round((x - x_adjust) * width_scale)), int(round((y * height_scale) + y_adjust)))
    return rescaled_text_annotations, rescaled_pen_annotations

def convert_pdf_to_images(pdf_path, output_folder, window_size):
    """
    Converts a PDF document into a series of images, one for each page.
    """
    pdf_document = fitz.open(pdf_path)  # Open the PDF file
    screen_width, screen_height = window_size
    high_res_factor = 2.0  # Scale factor for higher resolution images
    images = []

    total_pages = len(pdf_document)  # Get the total number of pages in the PDF

    # Iterate through each page of the PDF and save as an image
    for page_num in range(total_pages):
        page = pdf_document.load_page(page_num)  # Load the current page
        zoom_factor = min(screen_width / page.rect.width, screen_height / page.rect.height) * high_res_factor
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom_factor, zoom_factor))  # Create a high-resolution pixmap
        image_path = os.path.join(output_folder, f"page_{page_num}.png")  # Define the image path
        pix.save(image_path)  # Save the pixmap as a PNG image
        images.append(image_path)  # Add the image path to the list of images

        # Update the progress in the terminal
        print(f"\rLoading slides: {page_num + 1}/{total_pages} processed", end="")

    print(f"\rLoading completed. {total_pages}/{total_pages} processed.               ")  # Clear the line after completion
    return images

def scale_image_to_fit(image, window_size):
    """
    Scales an image to fit within the given window size while maintaining its aspect ratio.
    """
    # Calculate the scale factor to fit the image within the window size
    scale_factor = min(window_size[0] / image.get_width(), window_size[1] / image.get_height())
    new_size = (int(image.get_width() * scale_factor), int(image.get_height() * scale_factor))
    return pygame.transform.scale(image, new_size)  # Return the scaled image

def display_overview(images, window_size, highlighted_page):
    """
    Displays thumbnails of all slides in an overview mode, with the currently highlighted slide faded out.
    """
    screen.fill((0, 0, 0))  # Clear the screen with black
    margin = 10
    rows = cols = int(len(images) ** 0.5) + 1  # Calculate the number of rows and columns
    thumb_width = (window_size[0] - margin * (cols + 1)) // cols  # Calculate the thumbnail width
    thumb_height = (window_size[1] - margin * (rows + 1)) // rows  # Calculate the thumbnail height

    # Iterate through each thumbnail image and display it
    for i, thumbnail in enumerate([pygame.transform.scale(img, (thumb_width, thumb_height)) for img in images]):
        x = margin + (i % cols) * (thumb_width + margin)
        y = margin + (i // cols) * (thumb_height + margin)
        if i != highlighted_page:
            thumbnail.set_alpha(100)  # Fade out non-highlighted thumbnails
        screen.blit(thumbnail, (x, y))  # Display the thumbnail on the screen

def display_slide(images, current_page, window_size):
    """
    Displays the current slide, considering zoom mode and any highlights.
    """
    global zoom_pos, zoom_level, highlight_rects

    screen.fill((0, 0, 0))  # Clear the screen with black
    image = images[current_page]

    if zoom_level > 1:
        # Scale the image for zooming
        zoomed_image = pygame.transform.scale(image, (
            int(image.get_width() * zoom_level), int(image.get_height() * zoom_level)))

        # Calculate the portion of the image to display at the center
        # New zoomed image size
        zoomed_width, zoomed_height = zoomed_image.get_size()
        # Center position on screen
        center_x, center_y = window_size[0] // 2, window_size[1] // 2
        # Calculate the offset from the zoom_pos to the center
        offset_x = int(zoom_pos[0] * zoom_level) - center_x
        offset_y = int(zoom_pos[1] * zoom_level) - center_y
        # Create the rectangle to be displayed
        zoom_rect = pygame.Rect(offset_x, offset_y, window_size[0], window_size[1])

        # Ensure the rectangle is within the bounds of the zoomed image
        zoom_rect = zoom_rect.clamp(pygame.Rect(0, 0, zoomed_width, zoomed_height))

        screen.blit(zoomed_image, (0, 0), zoom_rect)  # Display the zoomed image
    else:
        # Center the image on the screen
        image_rect = image.get_rect(center=(window_size[0] // 2, window_size[1] // 2))
        screen.blit(image, image_rect.topleft)  # Display the image

        # Draw annotations relative to the current image size
        draw_text_annotations()
        draw_pen_annotations()

def handle_keydown(event, images, window_size, slide_transitions):
    """
    Handles keydown events, such as navigating slides, toggling modes, and managing annotations.
    """
    global current_page, focused_page, show_overview, scrolling, scroll_direction, scroll_start_time
    global spotlight_mode, spotlight_radius, end_of_presentation, show_help, show_initial_help_popup, zoom_level
    global highlight_mode, highlight_start, highlight_rects, current_highlights, black_screen_mode
    global is_entering_text, current_text, annotation_rect, text_annotations, is_drawing_box, annotation_start
    global is_drawing_pen, pen_points, pen_annotations, original_image_size

    if end_of_presentation and event.key != pygame.K_LEFT:
        return  # Ignore key presses if the presentation has ended, except for the left arrow key

    if is_entering_text:
        # Handle text entry for annotations
        if event.key == pygame.K_RETURN:  # Stop entering text mode with 'Enter' key
            if current_page not in text_annotations:
                text_annotations[current_page] = []
            text_annotations[current_page].append((annotation_rect, current_text))
            current_text = ""
            annotation_rect = None
            is_entering_text = False
            return
        elif event.key == pygame.K_BACKSPACE:
            # Handle backspace key to delete characters
            current_text = current_text[:-1]
        else:
            # Add the typed character to the current text
            current_text += event.unicode
            adjust_annotation_rect()  # Adjust the annotation rectangle as text is entered
        return  # Exit to avoid processing other keys while entering text

    if event.key == pygame.K_h:
        # Toggle help screen visibility
        show_help = not show_help
        show_initial_help_popup = False
        is_drawing_pen = False  # Disable pen mode when help is shown
    elif show_help:
        return  # Ignore other key presses when the help screen is active

    if event.key == pygame.K_RIGHT or event.key == pygame.K_PAGEDOWN:  # 'Page Down' for clickers
        if black_screen_mode:
            black_screen_mode = not black_screen_mode
        if show_overview:
            # Navigate to the next slide in overview mode
            focused_page = (focused_page + 1) % len(images)
        else:
            # Navigate to the next slide
            prev_page = current_page
            current_page = (current_page + 1)
            if current_page >= len(images):
                end_of_presentation = True
            else:
                apply_transition(prev_page, current_page, images, slide_transitions, reverse=False)
            zoom_level = 1.0  # Reset zoom level on slide change
            current_highlights.clear()  # Clear any highlights
    elif event.key == pygame.K_LEFT or event.key == pygame.K_PAGEUP:  # 'Page Up' for clickers
        if black_screen_mode:
            black_screen_mode = not black_screen_mode
        if show_overview:
            # Navigate to the previous slide in overview mode
            focused_page = (focused_page - 1) % len(images)
        else:
            if end_of_presentation:
                current_page = len(images) - 1
                prev_page = current_page
                end_of_presentation = False
            else:
                prev_page = current_page
                current_page = (current_page - 1)
                if current_page < 0:
                    current_page = 0
            zoom_level = 1.0  # Reset zoom level on slide change
            current_highlights.clear()  # Clear any highlights
            transition_config_current = TransitionsConfig.get_transition_config(slide_transitions, current_page)
            reversal_strategy = transition_config_current["reversal-strategy"]
            if reversal_strategy != constant.NONE:
                apply_transition(prev_page, current_page, images, slide_transitions,
                                 TransitionsConfig.check_reversal_strategy(reversal_strategy))
            else:
                display_slide(images, current_page, window_size)
    elif event.key == pygame.K_f:
        # Toggle fullscreen mode
        original_image_size = images[current_page].get_size()
        prev_window_size = screen.get_size()
        toggle_fullscreen(images, prev_window_size)
    elif event.key == pygame.K_TAB:
        show_overview = not show_overview  # Toggle overview mode
    elif event.key == pygame.K_RETURN and show_overview:
        # Select the slide in overview mode
        current_page = focused_page
        show_overview = False
    elif event.key == pygame.K_UP:
        # Scroll up in partial slide transition
        transition_config_prev = TransitionsConfig.get_transition_config(slide_transitions, current_page)
        transition_type_prev = transition_config_prev["transition"]
        scrolling = transition_type_prev == constant.PARTIAL_SLIDE_TRANSITION
        scroll_direction = -1  # Scroll up
        scroll_start_time = time.time()
    elif event.key == pygame.K_DOWN:
        # Scroll down in partial slide transition
        transition_config_prev = TransitionsConfig.get_transition_config(slide_transitions, current_page)
        transition_type_prev = transition_config_prev["transition"]
        scrolling = transition_type_prev == constant.PARTIAL_SLIDE_TRANSITION
        scroll_direction = 1  # Scroll down
        scroll_start_time = time.time()
    elif event.key == pygame.K_s:
        # Toggle spotlight mode or save annotations with Ctrl + S
        if pygame.key.get_mods() & pygame.KMOD_CTRL:
            save_annotations_to_json(images[current_page])  # Save annotations when Ctrl + S is pressed
        else:
            spotlight_mode = not spotlight_mode
            if spotlight_mode:
                highlight_mode = False  # Turn off highlight mode if spotlight mode is enabled
    elif event.key == pygame.K_r:
        # Toggle highlight mode
        if highlight_mode:
            current_highlights.clear()  # Clear current highlights
        spotlight_mode = False  # Turn off spotlight mode if highlight mode is enabled
        highlight_mode = not highlight_mode
        highlight_start = None  # Reset highlight start position
    elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
        # Increase spotlight radius
        if spotlight_mode:
            spotlight_radius = min(spotlight_radius + 10, window_size[1])
    elif event.key == pygame.K_MINUS:
        # Decrease spotlight radius
        if spotlight_mode:
            spotlight_radius = max(spotlight_radius - 10, 10)
    elif event.key == pygame.K_PERIOD:
        # Toggle black screen mode
        black_screen_mode = not black_screen_mode
    elif event.key == pygame.K_t:
        # Toggle text annotation mode
        is_drawing_pen = False  # Disable pen mode when text annotations are enabled
        if not show_overview and zoom_level == 1:
            if is_entering_text:  # Stop entering text mode
                if current_page not in text_annotations:
                    text_annotations[current_page] = []
                text_annotations[current_page].append((annotation_rect, current_text))
                current_text = ""
                annotation_rect = None
                is_entering_text = False
            else:  # Start drawing a box for text annotation
                for rect, text in text_annotations.get(current_page, []):
                    if rect.collidepoint(pygame.mouse.get_pos()):
                        annotation_rect = rect
                        current_text = text
                        text_annotations[current_page].remove((rect, text))
                        is_entering_text = True
                        break
                else:
                    is_drawing_box = True
                    annotation_start = pygame.mouse.get_pos()  # Capture the starting position for the annotation box
                    current_text = ""  # Initialize an empty text string
    elif event.key == pygame.K_p:
        # Toggle pen mode for freehand drawing
        if not show_overview and zoom_level == 1:
            is_drawing_pen = not is_drawing_pen  # Toggle pen drawing mode
            if not is_drawing_pen and pen_points:
                if current_page not in pen_annotations:
                    pen_annotations[current_page] = []
                pen_annotations[current_page].append(pen_points)
                pen_points = []

def handle_keyup(event):
    """
    Handles keyup events, specifically to stop scrolling.
    """
    global scrolling, scroll_direction

    # Stop scrolling when the up or down arrow key is released
    if event.key in (pygame.K_UP, pygame.K_DOWN):
        scrolling = False
        scroll_direction = 0

def handle_mouse(event, images, window_size, slide_transitions):
    """
    Handles mouse events, including clicks, drags, and scrolls for interactions with slides.
    """
    global current_page, focused_page, show_overview, spotlight_position, end_of_presentation, black_screen_mode
    global highlight_start, highlight_rects, current_highlights, zoom_pos, zoom_level
    global is_drawing_box, annotation_start, annotation_rect, is_entering_text, dragging, current_text
    global is_drawing_pen, pen_points

    if end_of_presentation:
        return  # Ignore mouse events if the presentation has ended

    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:  # Left mouse button
            if black_screen_mode:
                black_screen_mode = not black_screen_mode
            if is_entering_text:
                return  # Ignore clicks while entering text
            if show_overview:
                # Select a slide thumbnail in overview mode
                select_thumbnail(event.pos, images, window_size)
            elif highlight_mode:
                # Start drawing a highlight rectangle
                highlight_start = event.pos
            elif is_drawing_box:
                # Start drawing an annotation box
                annotation_start = event.pos
                is_drawing_box = True
                annotation_rect = None
            elif is_drawing_pen:
                # Start drawing a pen stroke
                pen_points.append(event.pos)
            else:
                # Check if an annotation is being dragged
                for rect, text in text_annotations.get(current_page, []):
                    if rect.collidepoint(event.pos):
                        dragging = True
                        annotation_rect = rect
                        current_text = text
                        text_annotations[current_page].remove((rect, text))
                        break
                else:
                    # Navigate to the next slide on left-click
                    prev_page = current_page
                    current_page = (current_page + 1)
                    zoom_level = 1.0  # Reset zoom level on slide change
                    current_highlights.clear()
                    if current_page >= len(images):
                        end_of_presentation = True
                    else:
                        apply_transition(prev_page, current_page, images, slide_transitions, reverse=False)
        elif event.button == 3 and not show_overview:  # Right mouse button and not in overview mode
            # Go to the previous slide
            if black_screen_mode:
                black_screen_mode = not black_screen_mode
            if end_of_presentation:
                current_page = len(images) - 1
                prev_page = current_page
                end_of_presentation = False
            else:
                prev_page = current_page
                current_page = (current_page - 1)
                if current_page < 0:
                    current_page = 0
            zoom_level = 1.0  # Reset zoom level on slide change
            current_highlights.clear()
            transition_config_current = TransitionsConfig.get_transition_config(slide_transitions, current_page)
            reversal_strategy = transition_config_current["reversal-strategy"]
            if reversal_strategy != constant.NONE:
                apply_transition(prev_page, current_page, images, slide_transitions,
                                 TransitionsConfig.check_reversal_strategy(reversal_strategy))
            else:
                display_slide(images, current_page, window_size)
        elif event.button == 4:  # Scroll up (mouse wheel up)
            if pygame.key.get_mods() & pygame.KMOD_CTRL:  # Check if Ctrl key is pressed
                is_drawing_pen = False
                zoom_level = min(zoom_level * 1.25, max_zoom_level)  # Increase zoom level
                zoom_pos = event.pos
            else:
                transition_config_prev = TransitionsConfig.get_transition_config(slide_transitions, current_page)
                transition_type_prev = transition_config_prev["transition"]
                if transition_type_prev == constant.PARTIAL_SLIDE_TRANSITION:
                    scroll_slide(images, -1)  # Scroll up
        elif event.button == 5:  # Scroll down (mouse wheel down)
            if pygame.key.get_mods() & pygame.KMOD_CTRL:  # Check if Ctrl key is pressed
                is_drawing_pen = False
                zoom_level = max(zoom_level / 1.25, min_zoom_level)  # Decrease zoom level
                zoom_pos = event.pos
            else:
                transition_config_prev = TransitionsConfig.get_transition_config(slide_transitions, current_page)
                transition_type_prev = transition_config_prev["transition"]
                if transition_type_prev == constant.PARTIAL_SLIDE_TRANSITION:
                    scroll_slide(images, 1)  # Scroll down
    elif event.type == pygame.MOUSEMOTION:
        if show_overview:
            highlight_thumbnail(event.pos, images, window_size)  # Highlight a slide thumbnail in overview mode
        if spotlight_mode:
            spotlight_position = event.pos  # Update spotlight position
        if highlight_mode and highlight_start:
            # Draw a highlight rectangle as the mouse is dragged
            x1, y1 = highlight_start
            x2, y2 = event.pos
            highlight_rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x1 - x2), abs(y1 - y2))
            current_highlights.append(highlight_rect)
        if zoom_level > 1:
            zoom_pos = event.pos  # Update zoom position
        if is_drawing_box and annotation_start:
            # Update the size of the annotation box as the mouse is dragged
            x1, y1 = annotation_start
            x2, y2 = event.pos
            annotation_rect = pygame.Rect(x1, y1, abs(x1 - x2), abs(y1 - y2))  # Keep width constant
        if dragging and annotation_rect:
            # Move the annotation box as the mouse is dragged
            annotation_rect.topleft = event.pos
        if is_drawing_pen and event.buttons[0]:  # Check if the left mouse button is held down
            pen_points.append(event.pos)  # Add points to the pen stroke
    elif event.type == pygame.MOUSEBUTTONUP:
        if event.button == 1 and is_drawing_box:
            is_drawing_box = False
            is_entering_text = True  # Now enter text mode
        if event.button == 1 and dragging:
            dragging = False
            text_annotations[current_page].append((annotation_rect, current_text))  # Save the dragged annotation
            annotation_rect = None
            current_text = ""
        if event.button == 1 and is_drawing_pen and len(pen_points) > 1:
            if current_page not in pen_annotations:
                pen_annotations[current_page] = []
            pen_annotations[current_page].append(pen_points)  # Save the pen stroke
            pen_points = []
        if event.button == 1 and highlight_mode and highlight_start:
            x1, y1 = highlight_start
            x2, y2 = event.pos
            highlight_rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x1 - x2), abs(y1 - y2))
            current_highlights.append(highlight_rect)  # Save the highlight rectangle
            highlight_start = None

def apply_transition(prev_page, current_page, images, slide_transitions, reverse=False):
    """
    Applies a transition effect between slides, based on the transition configuration.
    """
    global prev_slide_position, next_slide_position
    transition_config = TransitionsConfig.get_transition_config(slide_transitions, current_page)
    transition_type = transition_config["transition"]  # Get the transition type
    duration = float(transition_config["duration"].replace('s', ''))  # Get the transition duration
    SlideTransition.choose_transition(images[prev_page], images[current_page], window_size, screen, transition_type,
                                      duration, reverse)  # Apply the transition
    if transition_type == constant.PARTIAL_SLIDE_TRANSITION:
        # Calculate positions for partial slide transitions
        halfway_pos = window_size[1] / 4
        prev_start_pos = ((window_size[1] - images[prev_page].get_height()) // 2)
        prev_slide_position = prev_start_pos - halfway_pos
        next_slide_position = prev_slide_position + images[prev_page].get_height()

def select_thumbnail(mouse_pos, images, window_size):
    """
    Selects a thumbnail in overview mode based on the mouse click position.
    """
    global current_page, focused_page, show_overview
    margin = 10
    rows = cols = int(len(images) ** 0.5) + 1  # Calculate the number of rows and columns
    thumb_width = (window_size[0] - margin * (cols + 1)) // cols  # Calculate the thumbnail width
    thumb_height = (window_size[1] - margin * (rows + 1)) // rows  # Calculate the thumbnail height

    # Iterate through thumbnails and check if the mouse click is within any thumbnail
    for i in range(len(images)):
        x = margin + (i % cols) * (thumb_width + margin)
        y = margin + (i // cols) * (thumb_height + margin)
        if x <= mouse_pos[0] <= x + thumb_width and y <= mouse_pos[1] <= y + thumb_height:
            focused_page = i  # Update the focused page
            current_page = focused_page  # Set the current page to the focused page
            show_overview = False  # Exit overview mode
            break

def highlight_thumbnail(mouse_pos, images, window_size):
    """
    Highlights a thumbnail in overview mode based on the mouse hover position.
    """
    global focused_page
    margin = 10
    rows = cols = int(len(images) ** 0.5) + 1  # Calculate the number of rows and columns
    thumb_width = (window_size[0] - margin * (cols + 1)) // cols  # Calculate the thumbnail width
    thumb_height = (window_size[1] - margin * (rows + 1)) // rows  # Calculate the thumbnail height

    # Iterate through thumbnails and check if the mouse is hovering over any thumbnail
    for i in range(len(images)):
        x = margin + (i % cols) * (thumb_width + margin)
        y = margin + (i // cols) * (thumb_height + margin)
        images[i].set_alpha(250)  # Just a quick fix for fade out slide in transition issue
        if x <= mouse_pos[0] <= x + thumb_width and y <= mouse_pos[1] <= y + thumb_height:
            focused_page = i  # Update the focused page
            break

def scroll_slide(images, direction):
    """
    Scrolls slides up or down for partial slide transitions.
    """
    global current_page, window_size, screen, prev_slide_position, next_slide_position
    scroll_step = 10  # Pixels to move per scroll step
    image = images[current_page - 1]  # Get the previous slide image
    next_image = images[current_page]  # Get the current slide image
    end_pos = (window_size[1] - next_image.get_height()) // 2  # End scrolling when the main slide is centered
    if (prev_slide_position + image.get_height() > end_pos) if direction > 0 else (prev_slide_position < end_pos):
        prev_start_pos = prev_slide_position
        next_start_pos = prev_start_pos + image.get_height()

        y_pos_prev = prev_start_pos - scroll_step * direction  # Update the Y position of the previous slide
        y_pos_next = next_start_pos - scroll_step * direction  # Update the Y position of the next slide

        screen.fill((0, 0, 0))  # Clear the screen with black
        screen.blit(image, ((window_size[0] - image.get_width()) // 2, y_pos_prev))  # Draw the previous slide
        screen.blit(next_image, ((window_size[0] - next_image.get_width()) // 2, y_pos_next))  # Draw the current slide

        prev_slide_position = y_pos_prev  # Update the previous slide position
        next_slide_position = y_pos_next  # Update the next slide position

def draw_partial_slide(images):
    """
    Draws the slides after partial sliding and after each scrolling action.
    """
    global window_size, prev_slide_position, next_slide_position
    image = images[current_page - 1]  # Get the previous slide image
    next_image = images[current_page]  # Get the current slide image

    screen.fill((0, 0, 0))  # Clear the screen with black
    screen.blit(image, ((window_size[0] - image.get_width()) // 2, prev_slide_position))  # Draw the previous slide
    screen.blit(next_image, ((window_size[0] - next_image.get_width()) // 2, next_slide_position))  # Draw the current slide

def draw_spotlight():
    """
    Draws a spotlight effect on the slide, dimming the rest of the slide.
    """
    # Create a surface for the spotlight effect
    spotlight_surface = pygame.Surface(window_size, pygame.SRCALPHA)

    # Fill the surface with a semi-transparent black
    spotlight_surface.fill((0, 0, 0, 150))  # Use alpha value to dim

    # Cut out the spotlight area by making it fully transparent
    pygame.draw.circle(spotlight_surface, (0, 0, 0, 0), spotlight_position, spotlight_radius)

    # Blit the spotlight effect onto the main screen
    screen.blit(spotlight_surface, (0, 0))

def draw_highlight():
    """
    Draws a highlight rectangle over the slide, dimming the rest of the slide.
    """
    global current_highlights
    # Create an overlay surface with transparency to dim the rest of the slide
    overlay_surface = pygame.Surface(window_size, pygame.SRCALPHA)
    overlay_surface.fill((0, 0, 0, 150))  # Semi-transparent black fill

    if current_highlights:
        for rect in current_highlights:
            # Cut out the highlight area by making it fully transparent
            pygame.draw.rect(overlay_surface, (0, 0, 0, 0), rect)

    # Blit the overlay to the screen
    screen.blit(overlay_surface, (0, 0))

def draw_pen_annotations():
    """
    Draws the pen annotations on the current slide.
    """
    if current_page in pen_annotations:
        for points in pen_annotations[current_page]:
            if len(points) > 1:  # Ensure there are enough points to draw
                pygame.draw.lines(screen, (255, 0, 0), False, points, 2)  # Draw the pen stroke

    # Draw the current pen points being drawn
    if is_drawing_pen and len(pen_points) > 1:
        pygame.draw.lines(screen, (255, 0, 0), False, pen_points, 2)

def display_end_message():
    """
    Displays a message indicating the end of the presentation.
    """
    screen.fill((0, 0, 0))  # Clear the screen with black
    text = font.render("You have reached the end of the presentation", True, (255, 255, 255))
    text_rect = text.get_rect(center=(window_size[0] // 2, window_size[1] // 2))  # Center the text on the screen
    screen.blit(text, text_rect)  # Display the end message

def display_help():
    """
    Displays a help screen with key commands and instructions.
    """
    screen.fill((75, 75, 75))  # Fill the screen with a dark gray color
    help_text = [
        "Help Menu:",
        "RIGHT ARROW: Next slide",
        "LEFT ARROW: Previous slide",
        "UP ARROW: Scroll up (for partial slides)",
        "DOWN ARROW: Scroll down (for partial slides)",
        "S: Toggle spotlight mode",
        "R: Toggle highlight mode",
        "+ / =: Increase spotlight radius",
        "-: Decrease spotlight radius",
        "F: Toggle fullscreen",
        "TAB: Toggle overview mode",
        "RETURN: Select slide in overview mode",
        "H: Toggle help menu",
        "Ctrl + Mouse Wheel: Zoom in/out",
        "T: Add text annotation",
        "P: Toggle pen mode for freehand drawing",
        "RETURN: Stop entering text in text annotation box",
        "Ctrl + S: Save annotations"
    ]
    y_offset = 50  # Initial vertical position for the help text
    for line in help_text:
        text = font.render(line, True, (255, 255, 255))  # Render each line of help text
        screen.blit(text, (50, y_offset))  # Display the help text
        y_offset += 40  # Move to the next line

def display_initial_help_popup():
    """
    Displays an initial help popup with a short message.
    """
    popup_surface = pygame.Surface((window_size[0] * 0.8, 100), pygame.SRCALPHA)
    popup_surface.fill((0, 0, 0, 200))  # Create a semi-transparent black popup
    popup_rect = popup_surface.get_rect(center=(window_size[0] // 2, window_size[1] // 2))  # Center the popup on the screen
    text = font.render("Press 'H' for help", True, (255, 255, 255))  # Render the popup text
    text_rect = text.get_rect(center=popup_rect.center)  # Center the text within the popup
    screen.blit(popup_surface, popup_rect)  # Display the popup
    screen.blit(text, text_rect)  # Display the popup text

def draw_text_annotations():
    """
    Draws text annotations on the current slide.
    """
    if current_page in text_annotations:
        for rect, text in text_annotations[current_page]:
            if rect:  # Draw only if rect is not None
                render_text_in_box(text, rect)

    # Render the text being entered
    if is_entering_text and annotation_rect:
        pygame.draw.rect(screen, (0, 0, 255), annotation_rect, 2)  # Draw the rectangle
        render_text_in_box(current_text, annotation_rect)  # Render the entered text inside the rectangle

def adjust_annotation_rect():
    """
    Adjusts the size of the annotation rectangle dynamically as text is entered.
    """
    global annotation_rect
    if not annotation_rect:
        return
    words = current_text.split(' ')  # Split the text into words
    space_width = annotation_font.size(' ')[0]  # Get the width of a space character
    max_width = annotation_rect.width  # Get the maximum width for the text
    x, y = annotation_rect.topleft
    line_height = annotation_font.get_height()  # Get the height of a line of text
    current_line = []  # Initialize the current line of text
    max_height = 0  # Initialize the maximum height of the text

    for word in words:
        word_width, word_height = annotation_font.size(word)
        if word_width > max_width:
            continue  # Skip too long words
        if sum(annotation_font.size(w)[0] for w in current_line) + word_width + space_width <= max_width:
            current_line.append(word)  # Add the word to the current line
        else:
            max_height += line_height  # Move to the next line
            current_line = [word]
    if current_line:
        max_height += line_height  # Add the height of the last line

    annotation_rect.height = max_height  # Adjust the height of the annotation rectangle

def render_text_in_box(text, rect):
    """
    Renders text inside a rectangular box, ensuring it wraps appropriately.
    """
    words = text.split(' ')  # Split the text into words
    space_width = annotation_font.size(' ')[0]  # Get the width of a space character
    max_width = rect.width  # Get the maximum width for the text
    max_height = rect.height  # Get the maximum height for the text
    x, y = rect.topleft
    line_height = annotation_font.get_height()  # Get the height of a line of text
    lines = []  # Initialize the list of lines
    current_line = []  # Initialize the current line of text

    for word in words:
        word_width, word_height = annotation_font.size(word)
        if word_width > max_width:
            continue  # Skip too long words
        if sum(annotation_font.size(w)[0] for w in current_line) + word_width + space_width <= max_width:
            current_line.append(word)  # Add the word to the current line
        else:
            lines.append(' '.join(current_line))  # Add the current line to the list of lines
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))  # Add the last line to the list of lines

    for line in lines:
        line_surface = annotation_font.render(line, True, (0, 0, 255))  # Render the line of text
        screen.blit(line_surface, (x, y))  # Display the line of text
        y += line_height  # Move to the next line
        if y + line_height > rect.bottom:
            break  # Stop drawing if text exceeds the box

def save_annotations_to_json(image):
    """
    Saves text and pen annotations to a JSON file.
    """
    global fullscreen_window_size, is_fullscreen
    rescaled_text_annotations, rescaled_pen_annotations = copy.deepcopy(text_annotations), copy.deepcopy(pen_annotations)
    if is_fullscreen:
        # Rescale annotations if in fullscreen mode
        fs_image_size = scale_image_to_fit(image, fullscreen_window_size)
        org_image_size = scale_image_to_fit(image, original_window_size)
        rescaled_text_annotations, rescaled_pen_annotations = rescale_annotations(
            org_image_size.get_size(), fs_image_size.get_size(), original_window_size, fullscreen_window_size)
    annotations = {
        "text_annotations": {str(k): [{"rect": [r.left, r.top, r.width, r.height], "text": t} for r, t in v] for k, v in
                             rescaled_text_annotations.items()},
        "pen_annotations": {str(k): [[(x, y) for x, y in points] for points in v] for k, v in rescaled_pen_annotations.items()}
    }
    annotations_file = f"{Path(pdf_file).stem}_annotations.json"

    # Create the file if it doesn't exist
    if not os.path.exists(annotations_file):
        with open(annotations_file, 'w') as f:
            json.dump({}, f)  # Initialize an empty JSON object

    # Save annotations to the file
    with open(annotations_file, 'w') as f:
        json.dump(annotations, f, indent=4)  # Use indent for better readability
    print(f"Annotations saved to {annotations_file}")

def load_annotations_from_json():
    """
    Loads text and pen annotations from a JSON file.
    """
    global text_annotations, pen_annotations
    annotations_file = f"{Path(pdf_file).stem}_annotations.json"

    if os.path.exists(annotations_file):
        with open(annotations_file, 'r') as f:
            annotations = json.load(f)
            # Load text annotations from the JSON file
            text_annotations = {
                int(k): [(pygame.Rect(a["rect"][0], a["rect"][1], a["rect"][2], a["rect"][3]), a["text"]) for a in v]
                for k, v in annotations.get("text_annotations", {}).items()}
            # Load pen annotations from the JSON file
            pen_annotations = {int(k): [points for points in v] for k, v in
                               annotations.get("pen_annotations", {}).items()}
        print(f"Annotations loaded from {annotations_file}")
    else:
        print(f"No annotations file found at {annotations_file}")

def main():
    """
    Main function that initializes the PDF viewer, handles user input, and manages the presentation loop.
    """
    global window_size, scrolling, scroll_direction, spotlight_mode, spotlight_radius, spotlight_position
    global end_of_presentation, show_help, show_initial_help_popup, highlight_mode, highlight_start, highlight_rects
    global current_highlights, pdf_file

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="PDF Viewer with Slide Transitions")
    parser.add_argument("pdf_file", help="PDF file name")
    parser.add_argument("--config_file", help="Transitions config file name")
    args = parser.parse_args()

    # pdf file from the arguments
    pdf_file = args.pdf_file

    # Define paths for the PDF file and output images
    pdf_path = Path(pdf_file)  # relative to current directory
    pdf_path_abs = pdf_path.resolve()  # converts to absolute path

    output_folder_name = f'{pdf_file.split(".")[0]}'
    output_folder = f'pdf_images/{output_folder_name}'
    os.makedirs(output_folder, exist_ok=True)

    # Check if the provided pdf file is valid
    if not os.path.exists(pdf_path_abs):
        print(f"Error: PDF file '{pdf_file}' does not exist.")
        sys.exit(1)

    # Determine the config file path
    if args.config_file:
        config_file = args.config_file

        config_path = Path(config_file)  # relative to current directory
        config_path_abs = config_path.resolve()  # converts to absolute path
        if not os.path.exists(config_path_abs):
            print(f"Error: Transitions configuration file '{config_path_abs}' does not exist.")
            sys.exit(1)
    else:
        config_file = f'{pdf_file.split(".")[0]}.json'
        config_path = Path(config_file)  # relative to current directory
        config_path_abs = config_path.resolve()  # converts to absolute path
        if not os.path.exists(config_path_abs):
            print(f"Error: No specific transition configuration file provided and '{config_file}' does not exist.")
            print("Loading default transitions...")

    # Initialize Pygame
    pygame.init()

    # Convert PDF to images and load them
    global image_paths
    image_paths = convert_pdf_to_images(pdf_path_abs, output_folder, window_size)
    images = [scale_image_to_fit(pygame.image.load(img_path), window_size) for img_path in image_paths]

    # Load slide transitions configuration for the specified PDF
    global slide_transitions
    slide_transitions = TransitionsConfig.load_transitions_config(config_path_abs)

    # Load annotations if available
    load_annotations_from_json()

    running = True
    last_scroll_time = 0  # Track the last time we scrolled
    initial_popup_start_time = time.time()  # Track the start time of the initial popup

    # Restrict which event types should be placed on the event queue
    pygame.event.set_blocked(None)
    pygame.event.set_allowed(
        [pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.KEYDOWN, pygame.KEYUP, pygame.QUIT])

    pygame.event.clear()  # Clear the events queue

    while running:
        current_time = time.time()  # Get the current time
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False  # Exit the main loop
            elif event.type == pygame.KEYDOWN:
                handle_keydown(event, images, window_size, slide_transitions)  # Handle keydown events
            elif event.type == pygame.KEYUP:
                handle_keyup(event)  # Handle keyup events
            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP):
                handle_mouse(event, images, window_size, slide_transitions)  # Handle mouse events

        if black_screen_mode:
            screen.fill((0, 0, 0))  # Fill the screen with black if black screen mode is active
        else:
            if scrolling and current_time - last_scroll_time > 0.1:  # Scroll every 0.1 seconds
                scroll_slide(images, scroll_direction)
                last_scroll_time = current_time

            if show_help:
                display_help()  # Display the help screen
            elif show_overview:
                display_overview(images, window_size, focused_page)  # Display the overview mode
            elif end_of_presentation:
                display_end_message()  # Display the end of the presentation message
            else:
                transition_config_current = TransitionsConfig.get_transition_config(slide_transitions, current_page)
                transition_type_current = transition_config_current["transition"]
                if transition_type_current != constant.PARTIAL_SLIDE_TRANSITION:
                    display_slide(images, current_page, window_size)  # Display the current slide
                else:
                    draw_partial_slide(images)  # Draw the partial slide transition

            if spotlight_mode:
                draw_spotlight()  # Draw the spotlight effect
            elif highlight_mode:
                draw_highlight()  # Draw the highlight effect

            if not show_overview and zoom_level == 1 and not show_help:
                draw_text_annotations()  # Draw the text annotations
                draw_pen_annotations()  # Draw the pen annotations

            if show_initial_help_popup and current_time - initial_popup_start_time < 3:  # Show for 3 seconds
                display_initial_help_popup()  # Display the initial help popup
            elif show_initial_help_popup and current_time - initial_popup_start_time >= 3:
                show_initial_help_popup = False  # Hide the initial help popup

        pygame.display.flip()  # Update the screen

    pygame.quit()

if __name__ == '__main__':
    main()
