import fitz  # PyMuPDF
import pygame
import os
import constant
from transitions import SlideTransition
from config.transitions_config_reader import TransitionsConfig

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
    image_rect = image.get_rect(center=(window_size[0] // 2, window_size[1] // 2))
    screen.blit(image, image_rect.topleft)
    pygame.display.flip()

# Function to handle keydown events
def handle_keydown(event, images, window_size):
    global current_page, focused_page, show_overview

    if event.key == pygame.K_RIGHT:
        if show_overview:
            focused_page = (focused_page + 1) % len(images)
        else:
            prev_page = current_page
            current_page = (current_page + 1) % len(images)
            apply_transition(prev_page, current_page, images)
    elif event.key == pygame.K_LEFT:
        if show_overview:
            focused_page = (focused_page - 1) % len(images)
        else:
            prev_page = current_page
            current_page = (current_page - 1) % len(images)
            apply_transition(prev_page, current_page, images)
    elif event.key == pygame.K_f:
        toggle_fullscreen()
        window_size = screen.get_size()
        images[:] = [scale_image_to_fit(pygame.image.load(img_path), window_size) for img_path in image_paths]
    elif event.key == pygame.K_TAB:
        show_overview = not show_overview
    elif event.key == pygame.K_RETURN and show_overview:
        current_page = focused_page
        show_overview = False

# Function to handle mouse events
def handle_mouse(event, images, window_size):
    global current_page, focused_page, show_overview

    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:
            if show_overview:
                select_thumbnail(event.pos, images, window_size)
            else:
                prev_page = current_page
                current_page = (current_page + 1) % len(images)
                apply_transition(prev_page, current_page, images)
    elif event.type == pygame.MOUSEMOTION and show_overview:
        highlight_thumbnail(event.pos, images, window_size)

# Function to apply a slide transition
def apply_transition(prev_page, current_page, images):
    transition_type = TransitionsConfig.get_transition_type(slide_transitions, current_page)
    SlideTransition.choose_transition(images[prev_page], images[current_page], window_size, screen, transition_type)

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
        images[i].set_alpha(250) # just a quick fix for fade  out slide in trans issue
        if x <= mouse_pos[0] <= x + thumb_width and y <= mouse_pos[1] <= y + thumb_height:
            focused_page = i
            break

def main():
    global window_size

    # Define paths for the PDF file and output images
    file_name = 'demo'
    pdf_path = f'pdfs/{file_name}.pdf'
    output_folder = f'pdf_images/{file_name}'
    os.makedirs(output_folder, exist_ok=True)

    # Convert PDF to images and load them
    global image_paths
    image_paths = convert_pdf_to_images(pdf_path, output_folder, window_size)
    images = [scale_image_to_fit(pygame.image.load(img_path), window_size) for img_path in image_paths]

    # Load slide transitions configuration
    global slide_transitions
    slide_transitions = TransitionsConfig.load_transitions_config()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                handle_keydown(event, images, window_size)
            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION):
                handle_mouse(event, images, window_size)

        if show_overview:
            display_overview(images, window_size, focused_page)
        else:
            display_slide(images, current_page, window_size)

        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()
