import fitz  # PyMuPDF
import pygame
import os
import constant
from transitions import SlideTransition
from config.transitions_config_reader import TransitionsConfig

pygame.init()

# Define the initial window size
window_size = (constant.SCREEN_WIDTH, constant.SCREEN_HIGHT)
screen = pygame.display.set_mode(window_size)
# Set caption of the window
pygame.display.set_caption(constant.DISPLAY_CAPTION)

is_fullscreen = False
show_overview = False
current_page = 0
highlighted_page = 0

# Function to toggle full screen
def toggle_fullscreen():
    global screen, window_size, is_fullscreen
    if screen.get_flags() & pygame.FULLSCREEN:
        window_size = (constant.SCREEN_WIDTH, constant.SCREEN_HIGHT)
        screen = pygame.display.set_mode(window_size)
        is_fullscreen = False
    else:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        window_size = screen.get_size()  # Update window_size to full screen size
        is_fullscreen = True

# Function to convert pdf to images
def convert_pdf_to_images(pdf_path, output_folder, window_size):
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)
    images = []

    # Get the screen width and height
    screen_width, screen_height = window_size

    # Higher resolution scaling factor
    high_res_factor = 2.0

    # Iterate through each page
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        rect = page.rect  # get the dimensions of the page

        # multiply the minimum of the width and height scaling factors by high resolution factor 
        # to calculate a uniform scaling factor to maintain aspect ratio
        zoom_factor = min(screen_width / rect.width, screen_height / rect.height) * high_res_factor
        matrix = fitz.Matrix(zoom_factor, zoom_factor)  # transformation matrix

        # Render the page to a high-resolution pixmap (creates a bitmap image of the page at the specified resolution)
        pix = page.get_pixmap(matrix=matrix)

        image_path = os.path.join(output_folder, f"page_{page_num}.png")
        pix.save(image_path)
        images.append(image_path)

    return images

# Function to scale image while maintaining aspect ratio
def scale_image_to_fit(image, window_size):
    image_width, image_height = image.get_size()
    window_width, window_height = window_size

    # Calculate the scaling factors
    scale_factor = min(window_width / image_width, window_height / image_height)

    # Calculate the new size
    new_width = int(image_width * scale_factor)
    new_height = int(image_height * scale_factor)

    # Scale the image
    scaled_image = pygame.transform.scale(image, (new_width, new_height))
    return scaled_image

# Function to display thumbnails of all slides
def display_overview(images, window_size, highlighted_page):
    rows = cols = int(len(images) ** 0.5) + 1
    margin = 10
    thumb_width = (window_size[0] - margin * (cols + 1)) // cols
    thumb_height = (window_size[1] - margin * (rows + 1)) // rows

    thumbnails = [pygame.transform.scale(img, (thumb_width, thumb_height)) for img in images]

    for i, thumbnail in enumerate(thumbnails):
        row = i // cols
        col = i % cols
        x = margin + col * (thumb_width + margin)
        y = margin + row * (thumb_height + margin)
        if i == highlighted_page:
            screen.blit(thumbnail, (x, y))
        else:
            faded_thumbnail = thumbnail.copy()
            faded_thumbnail.set_alpha(100)  # Set alpha for faded effect
            screen.blit(faded_thumbnail, (x, y))

# Function to display converted images
def display_images_with_pygame(image_paths, window_size):
    global show_overview, current_page, highlighted_page
    images = [pygame.image.load(img) for img in image_paths]
    scaled_images = [scale_image_to_fit(img, window_size) for img in images]

    # Display the first slide without a transition
    screen.fill((0, 0, 0))
    image = scaled_images[current_page]
    image_rect = image.get_rect(center=(window_size[0] // 2, window_size[1] // 2))
    screen.blit(image, image_rect.topleft)
    pygame.display.flip()

    running = True
    while running:
        # event handler
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT and not show_overview:
                    prev_page = current_page
                    current_page = (current_page + 1) % len(scaled_images)
                    transition_type = TransitionsConfig.get_transition_type(slide_transitions, current_page)
                    SlideTransition.choose_transition(scaled_images[prev_page], scaled_images[current_page], window_size, screen, transition_type)
                elif event.key == pygame.K_LEFT and not show_overview:
                    prev_page = current_page
                    current_page = (current_page - 1) % len(scaled_images)
                    transition_type = TransitionsConfig.get_transition_type(slide_transitions, current_page)
                    SlideTransition.choose_transition(scaled_images[prev_page], scaled_images[current_page], window_size, screen, transition_type)
                elif event.key == pygame.K_f:  # Press 'f' to toggle full screen
                    toggle_fullscreen()
                    # Rescale images to new window size
                    window_size = screen.get_size()
                    scaled_images = [scale_image_to_fit(img, window_size) for img in images]
                elif event.key == pygame.K_TAB:  # Press 'Tab' to toggle overview mode
                    show_overview = not show_overview
                elif event.key == pygame.K_RETURN and show_overview:  # Press 'Enter' to view highlighted slide
                    current_page = highlighted_page
                    show_overview = False
                elif event.key == pygame.K_UP and show_overview:
                    highlighted_page = (highlighted_page - 1) % len(scaled_images)
                elif event.key == pygame.K_DOWN and show_overview:
                    highlighted_page = (highlighted_page + 1) % len(scaled_images)
                elif event.key == pygame.K_RIGHT and show_overview:
                    highlighted_page = (highlighted_page + 1) % len(scaled_images)
                elif event.key == pygame.K_LEFT and show_overview:
                    highlighted_page = (highlighted_page - 1) % len(scaled_images)
            elif event.type == pygame.MOUSEBUTTONDOWN and show_overview:
                if event.button == 1:  # Left mouse button
                    pos = pygame.mouse.get_pos()
                    rows = cols = int(len(scaled_images) ** 0.5) + 1
                    margin = 10
                    thumb_width = (window_size[0] - margin * (cols + 1)) // cols
                    thumb_height = (window_size[1] - margin * (rows + 1)) // rows

                    for i in range(len(scaled_images)):
                        row = i // cols
                        col = i % cols
                        x = margin + col * (thumb_width + margin)
                        y = margin + row * (thumb_height + margin)
                        if x <= pos[0] <= x + thumb_width and y <= pos[1] <= y + thumb_height:
                            highlighted_page = i
                            current_page = highlighted_page
                            show_overview = False
                            break
            elif event.type == pygame.MOUSEMOTION and show_overview:
                pos = pygame.mouse.get_pos()
                rows = cols = int(len(scaled_images) ** 0.5) + 1
                margin = 10
                thumb_width = (window_size[0] - margin * (cols + 1)) // cols
                thumb_height = (window_size[1] - margin * (rows + 1)) // rows

                for i in range(len(scaled_images)):
                    row = i // cols
                    col = i % cols
                    x = margin + col * (thumb_width + margin)
                    y = margin + row * (thumb_height + margin)
                    if x <= pos[0] <= x + thumb_width and y <= pos[1] <= y + thumb_height:
                        highlighted_page = i
                        break

        screen.fill((0, 0, 0))

        if show_overview:
            display_overview(images, window_size, highlighted_page)
        else:
            image = scaled_images[current_page]
            # Center the image on the screen
            image_rect = image.get_rect(center=(window_size[0] // 2, window_size[1] // 2))
            screen.blit(image, image_rect.topleft)
        
        pygame.display.flip()

    pygame.quit()

# Path to the PDF file
file_name = 'demo'
pdf_path = f'pdfs/{file_name}.pdf'

# Output folder for images
output_folder = f'pdf_images/{file_name}'
os.makedirs(output_folder, exist_ok=True)

# Convert PDF to images
image_paths = convert_pdf_to_images(pdf_path, output_folder, window_size)

# load all transition types assigned to each slide
slide_transitions = TransitionsConfig.load_transitions_config()
# Display images using Pygame
display_images_with_pygame(image_paths, window_size)
