import argparse
import sys

import fitz  # PyMuPDF
import pygame
import os
from pathlib import Path
import pyslides.constant as constant
from pyslides.transitions import SlideTransition
from pyslides.config.transitions_config_reader import TransitionsConfig
import time

# Ensure the pyslides directory is in the Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pyslides'))

# Define the initial window size
window_size = (constant.SCREEN_WIDTH, constant.SCREEN_HIGHT)
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption(constant.DISPLAY_CAPTION)

# Initialize Pygame's font module
pygame.font.init()
font = pygame.font.Font(None, 36)  # None uses the default font, 36 is the font size

# Global state variables
is_fullscreen = False
show_overview = False
current_page = 0
focused_page = 0
prev_slide_position = 0  # previous slide y position for partial slide transition scrolling
next_slide_position = 0  # next slide y position for partial slide transition scrolling
scrolling = False  # Flag to indicate if scrolling is active
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
show_initial_help_popup = True  # Flag for initial help popup
zoom_level = 1  # Initial zoom level (1 = no zoom)
max_zoom_level = 4  # Maximum zoom level
min_zoom_level = 1  # Minimum zoom level
zoom_pos = (0, 0)  # Position around which zoom is centered

# Function to toggle full screen mode
def toggle_fullscreen():
    global screen, window_size, is_fullscreen
    is_fullscreen = not is_fullscreen
    if is_fullscreen:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((constant.SCREEN_WIDTH, constant.SCREEN_HIGHT))
    window_size = screen.get_size()

# Function to convert PDF pages to images
def convert_pdf_to_images(pdf_path, output_folder, window_size):
    pdf_document = fitz.open(pdf_path)
    screen_width, screen_height = window_size
    high_res_factor = 2.0
    images = []

    # Iterate through each page of the PDF
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        zoom_factor = min(screen_width / page.rect.width, screen_height / page.rect.height) * high_res_factor
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom_factor, zoom_factor))
        image_path = os.path.join(output_folder, f"page_{page_num}.png")
        pix.save(image_path)
        images.append(image_path)

    return images

# Function to scale an image to fit within the window size while maintaining aspect ratio
def scale_image_to_fit(image, window_size):
    scale_factor = min(window_size[0] / image.get_width(), window_size[1] / image.get_height())
    new_size = (int(image.get_width() * scale_factor), int(image.get_height() * scale_factor))
    return pygame.transform.scale(image, new_size)

# Function to display thumbnails of all slides in overview mode
def display_overview(images, window_size, highlighted_page):
    screen.fill((0, 0, 0))
    margin = 10
    rows = cols = int(len(images) ** 0.5) + 1
    thumb_width = (window_size[0] - margin * (cols + 1)) // cols
    thumb_height = (window_size[1] - margin * (rows + 1)) // rows

    # Iterate through each thumbnail image and display it
    for i, thumbnail in enumerate([pygame.transform.scale(img, (thumb_width, thumb_height)) for img in images]):
        x = margin + (i % cols) * (thumb_width + margin)
        y = margin + (i // cols) * (thumb_height + margin)
        if i != highlighted_page:
            thumbnail.set_alpha(100)  # Fade out non-highlighted thumbnails
        screen.blit(thumbnail, (x, y))

# Function to display the current slide, considering zoom mode and highlights
def display_slide(images, current_page, window_size):
    global zoom_pos, zoom_level, highlight_rects

    screen.fill((0, 0, 0))
    image = images[current_page]

    if zoom_level > 1:
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

        screen.blit(zoomed_image, (0, 0), zoom_rect)
    else:
        image_rect = image.get_rect(center=(window_size[0] // 2, window_size[1] // 2))
        screen.blit(image, image_rect.topleft)

    # # Display the highlight rectangles for the current slide
    # if current_page in highlight_rects:
    #     for rect in highlight_rects[current_page]:
    #         pygame.draw.rect(screen, (255, 0, 0), rect, 2)

# Function to handle keydown events
def handle_keydown(event, images, window_size, slide_transitions):
    global current_page, focused_page, show_overview, scrolling, scroll_direction, scroll_start_time
    global spotlight_mode, spotlight_radius, end_of_presentation, show_help, show_initial_help_popup
    global highlight_mode, highlight_start, highlight_rects, current_highlights

    if end_of_presentation and event.key != pygame.K_LEFT:
        return  # Ignore key presses if the presentation has ended, except for the left arrow key

    if event.key == pygame.K_h:
        show_help = not show_help
        show_initial_help_popup = False
    elif show_help:
        return  # Ignore other key presses when the help screen is active

    if event.key == pygame.K_RIGHT:
        if show_overview:
            focused_page = (focused_page + 1) % len(images)
        else:
            prev_page = current_page
            current_page = (current_page + 1)
            if current_page >= len(images):
                end_of_presentation = True
            else:
                apply_transition(prev_page, current_page, images, slide_transitions, reverse=False)
            zoom_level = 1.0  # Reset zoom level on slide change
            current_highlights.clear()
    elif event.key == pygame.K_LEFT:
        if show_overview:
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
            current_highlights.clear()
            transition_config_current = TransitionsConfig.get_transition_config(slide_transitions, current_page)
            reversal_strategy = transition_config_current["reversal-strategy"]
            if reversal_strategy != constant.NONE:
                apply_transition(prev_page, current_page, images, slide_transitions,
                                 TransitionsConfig.check_reversal_strategy(reversal_strategy))
            else:
                display_slide(images, current_page, window_size)
    elif event.key == pygame.K_f:
        toggle_fullscreen()
        window_size = screen.get_size()
        images[:] = [scale_image_to_fit(pygame.image.load(img_path), window_size) for img_path in image_paths]
    elif event.key == pygame.K_TAB:
        show_overview = not show_overview
    elif event.key == pygame.K_RETURN and show_overview:
        current_page = focused_page
        show_overview = False
    elif event.key == pygame.K_UP:
        transition_config_prev = TransitionsConfig.get_transition_config(slide_transitions, current_page)
        transition_type_prev = transition_config_prev["transition"]
        scrolling = transition_type_prev == constant.PARTIAL_SLIDE_TRANSITION
        scroll_direction = -1
        scroll_start_time = time.time()
    elif event.key == pygame.K_DOWN:
        transition_config_prev = TransitionsConfig.get_transition_config(slide_transitions, current_page)
        transition_type_prev = transition_config_prev["transition"]
        scrolling = transition_type_prev == constant.PARTIAL_SLIDE_TRANSITION
        scroll_direction = 1
        scroll_start_time = time.time()
    elif event.key == pygame.K_s:
        spotlight_mode = not spotlight_mode
        if spotlight_mode:
            highlight_mode = False  # Turn off highlight mode if spotlight mode is enabled
    elif event.key == pygame.K_r:
        if highlight_mode:
            current_highlights.clear()
        spotlight_mode = False  # Turn off spotlight mode if highlight mode is enabled
        highlight_mode = not highlight_mode
        highlight_start = None
    elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
        if spotlight_mode:
            spotlight_radius = min(spotlight_radius + 10, window_size[1])
    elif event.key == pygame.K_MINUS:
        if spotlight_mode:
            spotlight_radius = max(spotlight_radius - 10, 10)

# Function to handle keyup events
def handle_keyup(event):
    global scrolling, scroll_direction

    if event.key in (pygame.K_UP, pygame.K_DOWN):
        scrolling = False
        scroll_direction = 0

# Function to handle mouse events
def handle_mouse(event, images, window_size, slide_transitions):
    global current_page, focused_page, show_overview, spotlight_position, end_of_presentation
    global highlight_start, highlight_rects, current_highlights, zoom_pos, zoom_level

    if end_of_presentation:
        return  # Ignore mouse events if the presentation has ended

    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:
            if show_overview:
                select_thumbnail(event.pos, images, window_size)
            elif highlight_mode:
                highlight_start = event.pos
            else:
                prev_page = current_page
                current_page = (current_page + 1)
                zoom_level = 1.0  # Reset zoom level on slide change
                current_highlights.clear()
                if current_page >= len(images):
                    end_of_presentation = True
                else:
                    apply_transition(prev_page, current_page, images, slide_transitions, reverse=False)
        elif event.button == 4:  # Scroll up (mouse wheel up)
            if pygame.key.get_mods() & pygame.KMOD_CTRL:  # Check if Ctrl key is pressed
                zoom_level = min(zoom_level * 1.25, max_zoom_level)
                zoom_pos = event.pos
                # display_slide(images, current_page, window_size)
            else:
                transition_config_prev = TransitionsConfig.get_transition_config(slide_transitions, current_page)
                transition_type_prev = transition_config_prev["transition"]
                if transition_type_prev == constant.PARTIAL_SLIDE_TRANSITION:
                    scroll_slide(images, -1)
        elif event.button == 5:  # Scroll down (mouse wheel down)
            if pygame.key.get_mods() & pygame.KMOD_CTRL:  # Check if Ctrl key is pressed
                zoom_level = max(zoom_level / 1.25, min_zoom_level)
                zoom_pos = event.pos
                # display_slide(images, current_page, window_size)
            else:
                transition_config_prev = TransitionsConfig.get_transition_config(slide_transitions, current_page)
                transition_type_prev = transition_config_prev["transition"]
                if transition_type_prev == constant.PARTIAL_SLIDE_TRANSITION:
                    scroll_slide(images, 1)
    elif event.type == pygame.MOUSEMOTION:
        if show_overview:
            highlight_thumbnail(event.pos, images, window_size)
        if spotlight_mode:
            spotlight_position = event.pos
        if highlight_mode and highlight_start:
            x1, y1 = highlight_start
            x2, y2 = event.pos
            highlight_rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x1 - x2), abs(y1 - y2))
            current_highlights.append(highlight_rect)
        if zoom_level > 1:
            zoom_pos = event.pos
    elif event.type == pygame.MOUSEBUTTONUP:
        if event.button == 1 and highlight_mode and highlight_start:
            x1, y1 = highlight_start
            x2, y2 = event.pos
            highlight_rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x1 - x2), abs(y1 - y2))
            current_highlights.append(highlight_rect)
            highlight_start = None

# Function to apply a slide transition
def apply_transition(prev_page, current_page, images, slide_transitions, reverse=False):
    global prev_slide_position, next_slide_position
    transition_config = TransitionsConfig.get_transition_config(slide_transitions, current_page)
    transition_type = transition_config["transition"]
    duration = float(transition_config["duration"].replace('s', ''))
    SlideTransition.choose_transition(images[prev_page], images[current_page], window_size, screen, transition_type, duration, reverse)
    if transition_type == constant.PARTIAL_SLIDE_TRANSITION:
        halfway_pos = window_size[1] / 4
        prev_start_pos = ((window_size[1] - images[prev_page].get_height()) // 2)
        prev_slide_position = prev_start_pos - halfway_pos
        next_slide_position = prev_slide_position + images[prev_page].get_height()

# Function to select a thumbnail based on mouse click position
def select_thumbnail(mouse_pos, images, window_size):
    global current_page, focused_page, show_overview
    margin = 10
    rows = cols = int(len(images) ** 0.5) + 1
    thumb_width = (window_size[0] - margin * (cols + 1)) // cols
    thumb_height = (window_size[1] - margin * (rows + 1)) // rows

    # Iterate through thumbnails and check if the mouse click is within any thumbnail
    for i in range(len(images)):
        x = margin + (i % cols) * (thumb_width + margin)
        y = margin + (i // cols) * (thumb_height + margin)
        if x <= mouse_pos[0] <= x + thumb_width and y <= mouse_pos[1] <= y + thumb_height:
            focused_page = i
            current_page = focused_page
            show_overview = False
            break

# Function to highlight a thumbnail based on mouse hover position
def highlight_thumbnail(mouse_pos, images, window_size):
    global focused_page
    margin = 10
    rows = cols = int(len(images) ** 0.5) + 1
    thumb_width = (window_size[0] - margin * (cols + 1)) // cols
    thumb_height = (window_size[1] - margin * (rows + 1)) // rows

    # Iterate through thumbnails and check if the mouse is hovering over any thumbnail
    for i in range(len(images)):
        x = margin + (i % cols) * (thumb_width + margin)
        y = margin + (i // cols) * (thumb_height + margin)
        images[i].set_alpha(250)  # just a quick fix for fade out slide in transition issue
        if x <= mouse_pos[0] <= x + thumb_width and y <= mouse_pos[1] <= y + thumb_height:
            focused_page = i
            break

# Function to scroll slides
def scroll_slide(images, direction):
    global current_page, window_size, screen, prev_slide_position, next_slide_position
    scroll_step = 10  # Pixels to move per scroll step
    image = images[current_page - 1]
    next_image = images[current_page]
    end_pos = (window_size[1] - next_image.get_height()) // 2  # end scrolling when main slide at the center
    if (prev_slide_position + image.get_height() > end_pos) if direction > 0 else (prev_slide_position < end_pos):
        prev_start_pos = prev_slide_position
        next_start_pos = prev_start_pos + image.get_height()

        y_pos_prev = prev_start_pos - scroll_step * direction
        y_pos_next = next_start_pos - scroll_step * direction

        screen.fill((0, 0, 0))
        screen.blit(image, ((window_size[0] - image.get_width()) // 2, y_pos_prev))
        screen.blit(next_image, ((window_size[0] - next_image.get_width()) // 2, y_pos_next))
        pygame.display.flip()

        prev_slide_position = y_pos_prev
        next_slide_position = y_pos_next

# Function to draw the slides after partial sliding and after each scrolling
def draw_partial_slide(images):
    global window_size, prev_slide_position, next_slide_position
    image = images[current_page - 1]
    next_image = images[current_page]

    screen.fill((0, 0, 0))
    screen.blit(image, ((window_size[0] - image.get_width()) // 2, prev_slide_position))
    screen.blit(next_image, ((window_size[0] - next_image.get_width()) // 2, next_slide_position))

# Function to draw a spotlight on the slide
def draw_spotlight():
    # Create a surface for the spotlight effect
    spotlight_surface = pygame.Surface(window_size, pygame.SRCALPHA)

    # Fill the surface with a semi-transparent black
    spotlight_surface.fill((0, 0, 0, 150))  # Use alpha value to dim

    # Cut out the spotlight area by making it fully transparent
    pygame.draw.circle(spotlight_surface, (0, 0, 0, 0), spotlight_position, spotlight_radius)

    # Blit the spotlight effect onto the main screen
    screen.blit(spotlight_surface, (0, 0))

# Function to draw the highlight rectangle
def draw_highlight():
    global current_highlights

    if current_highlights:
        # Create an overlay surface with transparency to dim the rest of the slide
        overlay_surface = pygame.Surface(window_size, pygame.SRCALPHA)
        overlay_surface.fill((0, 0, 0, 150))  # Semi-transparent black fill

        for rect in current_highlights:
            # Cut out the highlight area by making it fully transparent
            pygame.draw.rect(overlay_surface, (0, 0, 0, 0), rect)

        # Blit the overlay to the screen
        screen.blit(overlay_surface, (0, 0))

# Function to display end of presentation message
def display_end_message():
    screen.fill((0, 0, 0))
    text = font.render("You have reached the end of the presentation", True, (255, 255, 255))
    text_rect = text.get_rect(center=(window_size[0] // 2, window_size[1] // 2))
    screen.blit(text, text_rect)

# Function to display help screen
def display_help():
    screen.fill((75, 75, 75))
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
        "Ctrl + Mouse Wheel: Zoom in/out"
    ]
    y_offset = 50
    for line in help_text:
        text = font.render(line, True, (255, 255, 255))
        screen.blit(text, (50, y_offset))
        y_offset += 40

# Function to display initial help popup
def display_initial_help_popup():
    popup_surface = pygame.Surface((window_size[0] * 0.8, 100), pygame.SRCALPHA)
    popup_surface.fill((0, 0, 0, 200))
    popup_rect = popup_surface.get_rect(center=(window_size[0] // 2, window_size[1] // 2))
    text = font.render("Press 'H' for help", True, (255, 255, 255))
    text_rect = text.get_rect(center=popup_rect.center)
    screen.blit(popup_surface, popup_rect)
    screen.blit(text, text_rect)

def main():
    global window_size, scrolling, scroll_direction, spotlight_mode, spotlight_radius, spotlight_position
    global end_of_presentation, show_help, show_initial_help_popup, highlight_mode, highlight_start, highlight_rects
    global current_highlights

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

    output_folder = f'pdf_images/{pdf_file}'
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
        print(config_path_abs)
        if not os.path.exists(config_path_abs):
            print(f"Error: No transition configuration file provided and '{config_file}' does not exist.")
            sys.exit(1)

    # Initialize Pygame
    pygame.init()

    # Convert PDF to images and load them
    global image_paths
    image_paths = convert_pdf_to_images(pdf_path_abs, output_folder, window_size)
    images = [scale_image_to_fit(pygame.image.load(img_path), window_size) for img_path in image_paths]

    # Load slide transitions configuration for the specified PDF
    global slide_transitions
    slide_transitions = TransitionsConfig.load_transitions_config(config_path_abs)

    running = True
    last_scroll_time = 0  # Track the last time we scrolled
    initial_popup_start_time = time.time()  # Track the start time of the initial popup

    # Restrict which event types should be placed on the event queue
    pygame.event.set_blocked(None)
    pygame.event.set_allowed([pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.KEYDOWN, pygame.KEYUP, pygame.QUIT])

    pygame.event.clear()  # clear the events queue

    while running:
        current_time = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                handle_keydown(event, images, window_size, slide_transitions)
            elif event.type == pygame.KEYUP:
                handle_keyup(event)
            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP):
                handle_mouse(event, images, window_size, slide_transitions)

        if scrolling and current_time - last_scroll_time > 0.1:  # Scroll every 0.1 seconds
            scroll_slide(images, scroll_direction)
            last_scroll_time = current_time

        if show_help:
            display_help()
        elif show_overview:
            display_overview(images, window_size, focused_page)
        elif end_of_presentation:
            display_end_message()
        else:
            transition_config_current = TransitionsConfig.get_transition_config(slide_transitions, current_page)
            transition_type_current = transition_config_current["transition"]
            if transition_type_current != constant.PARTIAL_SLIDE_TRANSITION:
                display_slide(images, current_page, window_size)
            else:
                draw_partial_slide(images)

        if spotlight_mode:
            draw_spotlight()
        elif highlight_mode:
            draw_highlight()

        if show_initial_help_popup and current_time - initial_popup_start_time < 3:  # Show for 3 seconds
            display_initial_help_popup()
        elif show_initial_help_popup and current_time - initial_popup_start_time >= 3:
            show_initial_help_popup = False

        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()