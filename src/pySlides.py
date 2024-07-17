import argparse
import sys

import fitz  # PyMuPDF
import pygame
import os
import src.constant as constant
from src.transitions import SlideTransition
from src.config.transitions_config_reader import TransitionsConfig
import time

# Ensure the src directory is in the Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

# Initialize Pygame
pygame.init()

# Define the initial window size
window_size = (constant.SCREEN_WIDTH, constant.SCREEN_HIGHT)
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption(constant.DISPLAY_CAPTION)

# Global state variables
is_fullscreen = False
show_overview = False
current_page = 0
focused_page = 0
prev_slide_position = 0  # previous slide y position for partial slide transition scrolling
scrolling = False  # Flag to indicate if scrolling is active
scroll_direction = 0  # Direction of scrolling: -1 for up, 1 for down
scroll_start_time = 0  # Time when scrolling started

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

# Function to display the current slide
def display_slide(images, current_page, window_size):
    screen.fill((0, 0, 0))
    image = images[current_page]
    image.set_alpha(250)
    image_rect = image.get_rect(center=(window_size[0] // 2, window_size[1] // 2))
    screen.blit(image, image_rect.topleft)
    pygame.display.flip()

# Function to handle keydown events
def handle_keydown(event, images, window_size, slide_transitions):
    global current_page, focused_page, show_overview, scrolling, scroll_direction, scroll_start_time

    if event.key == pygame.K_RIGHT:
        if show_overview:
            focused_page = (focused_page + 1) % len(images)
        else:
            prev_page = current_page
            current_page = (current_page + 1) % len(images)
            apply_transition(prev_page, current_page, images, slide_transitions, reverse=False)
    elif event.key == pygame.K_LEFT:
        if show_overview:
            focused_page = (focused_page - 1) % len(images)
        else:
            prev_page = current_page
            current_page = (current_page - 1) % len(images)
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
        scrolling = True
        scroll_direction = -1
        scroll_start_time = time.time()
    elif event.key == pygame.K_DOWN:
        scrolling = True
        scroll_direction = 1
        scroll_start_time = time.time()

def handle_keyup(event):
    global scrolling, scroll_direction

    if event.key in (pygame.K_UP, pygame.K_DOWN):
        scrolling = False
        scroll_direction = 0

# Function to handle mouse events
def handle_mouse(event, images, window_size, slide_transitions):
    global current_page, focused_page, show_overview

    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:
            if show_overview:
                select_thumbnail(event.pos, images, window_size)
            else:
                prev_page = current_page
                current_page = (current_page + 1) % len(images)
                apply_transition(prev_page, current_page, images, slide_transitions, reverse=False)
        elif event.button == 4:  # Scroll up
            scroll_slide(images, -1)
        elif event.button == 5:  # Scroll down
            scroll_slide(images, 1)
    elif event.type == pygame.MOUSEMOTION and show_overview:
        highlight_thumbnail(event.pos, images, window_size)


# Function to apply a slide transition
def apply_transition(prev_page, current_page, images, slide_transitions, reverse=False):
    global prev_slide_position
    transition_config = TransitionsConfig.get_transition_config(slide_transitions, current_page)
    transition_type = transition_config["transition"]
    duration = float(transition_config["duration"].replace('s', ''))
    SlideTransition.choose_transition(images[prev_page], images[current_page], window_size, screen, transition_type, duration, reverse)
    if transition_type == constant.PARTIAL_SLIDE_TRANSITION:
        halfway_pos = window_size[1] / 4
        prev_start_pos = ((window_size[1] - images[prev_page].get_height()) // 2)
        prev_slide_position = prev_start_pos - halfway_pos


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
    global current_page, window_size, screen, prev_slide_position
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

def main():
    global window_size, scrolling, scroll_direction

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="PDF Viewer with Slide Transitions")
    parser.add_argument("pdf_file", help="PDF file name")
    parser.add_argument("--config_file", help="Transitions config file name")
    args = parser.parse_args()

    # pdf file from the arguments
    pdf_file = args.pdf_file

    # Define paths for the PDF file and output images
    file_name = pdf_file  # Specify the name of the PDF file here
    pdf_path = f'pdfs/{file_name}'
    # config_file = ''
    output_folder = f'pdf_images/{file_name}'
    os.makedirs(output_folder, exist_ok=True)

    # Check if the provided pdf file is valid
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file '{pdf_file}' does not exist.")
        sys.exit(1)

    # Determine the config file path
    if args.config_file:
        config_file = args.config_file
        config_path = f'src/config/{config_file}'
        if not os.path.exists(config_path):
            print(f"Error: Transitions configuration file '{config_path}' does not exist.")
            sys.exit(1)
    else:
        config_file = f'{file_name.split(".")[0]}.json'
        config_path = f'src/config/{config_file}'
        print(config_path)
        if not os.path.exists(config_path):
            print(f"Error: No transition configuration file provided and '{config_file}' does not exist.")
            sys.exit(1)

    # Convert PDF to images and load them
    global image_paths
    image_paths = convert_pdf_to_images(pdf_path, output_folder, window_size)
    images = [scale_image_to_fit(pygame.image.load(img_path), window_size) for img_path in image_paths]

    # Load slide transitions configuration for the specified PDF
    global slide_transitions
    slide_transitions = TransitionsConfig.load_transitions_config(config_file)

    running = True
    last_scroll_time = 0  # Track the last time we scrolled

    while running:
        current_time = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                handle_keydown(event, images, window_size, slide_transitions)
            elif event.type == pygame.KEYUP:
                handle_keyup(event)
            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION):
                handle_mouse(event, images, window_size, slide_transitions)

        if scrolling and current_time - last_scroll_time > 0.1:  # Scroll every 0.1 seconds
            scroll_slide(images, scroll_direction)
            last_scroll_time = current_time

        if show_overview:
            display_overview(images, window_size, focused_page)
        else:
            transition_config_current = TransitionsConfig.get_transition_config(slide_transitions, current_page)
            transition_config_prev = TransitionsConfig.get_transition_config(slide_transitions, current_page - 1)
            transition_type_current = transition_config_current["transition"]
            transition_type_prev = transition_config_prev["transition"]
            if transition_type_current != constant.PARTIAL_SLIDE_TRANSITION and transition_type_prev != constant.PARTIAL_SLIDE_TRANSITION :
                display_slide(images, current_page, window_size)

        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()
