import fitz  # PyMuPDF
import pygame
import os
import constant

pygame.init()

# Define the initial window size
window_size = (constant.SCREEN_WIDTH, constant.SCREEN_HIGHT)
screen = pygame.display.set_mode(window_size)
# Set caption of the window
pygame.display.set_caption(constant.DISPLAY_CAPTION)

is_fullscreen = False
show_overview = False

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
        rect = page.rect # get the dimensions of the page

        # multiply the minimum of the width and height scaling factors by high resolution factor 
        # to calculate a uniform scaling factor to maintain aspect ratio
        zoom_factor = min(screen_width / rect.width, screen_height / rect.height) * high_res_factor 
        matrix = fitz.Matrix(zoom_factor, zoom_factor) # transformation matrix

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
def display_overview(images, window_size):
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
        screen.blit(thumbnail, (x, y))

# Function for top-to-bottom transition
def top_to_bottom_transition(prev_image, next_image, window_size):
    start_pos = -window_size[1]  # Start above the screen
    end_pos = (window_size[1] - next_image.get_height()) // 2  # End in the center of the screen
    step = 20  # Pixels to move each frame

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
        pygame.time.delay(10)  # Add a small delay to control the speed of the transition

# Function to display converted images
def display_images_with_pygame(image_paths, window_size, transition_type):
    global show_overview
    images = [pygame.image.load(img) for img in image_paths]
    scaled_images = [scale_image_to_fit(img, window_size) for img in images]
    current_page = 0

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
                    top_to_bottom_transition(scaled_images[prev_page], scaled_images[current_page], window_size)
                elif event.key == pygame.K_LEFT and not show_overview:
                    prev_page = current_page
                    current_page = (current_page - 1) % len(scaled_images)
                    top_to_bottom_transition(scaled_images[prev_page], scaled_images[current_page], window_size)
                elif event.key == pygame.K_f:  # Press 'f' to toggle full screen
                    toggle_fullscreen()
                    # Rescale images to new window size
                    window_size = screen.get_size()
                    scaled_images = [scale_image_to_fit(img, window_size) for img in images]
                elif event.key == pygame.K_TAB:  # Press 'Tab' to toggle overview mode
                    show_overview = not show_overview
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not show_overview:  # Left mouse button to go to the next image
                    prev_page = current_page
                    current_page = (current_page + 1) % len(scaled_images)
                    top_to_bottom_transition(scaled_images[prev_page], scaled_images[current_page], window_size)

        screen.fill((0, 0, 0))

        if show_overview:
            display_overview(images, window_size)
        else:
            image = scaled_images[current_page]
            # Center the image on the screen
            image_rect = image.get_rect(center=(window_size[0] // 2, window_size[1] // 2))
            screen.blit(image, image_rect.topleft)
        
        pygame.display.flip()

    pygame.quit()

# Path to the PDF file
file_name = 'demo'
pdf_path = f'/home/danodya/Documents/{file_name}.pdf'

# Output folder for images
output_folder = f'pdf_images/{file_name}'
os.makedirs(output_folder, exist_ok=True)

# Convert PDF to images
image_paths = convert_pdf_to_images(pdf_path, output_folder, window_size)

# Display images using Pygame with specified transition type
# transition_type = 'fade_out_slide_in'  # or 'top_to_bottom'
transition_type = 'top_to_bottom'  # or 'top_to_bottom'
display_images_with_pygame(image_paths, window_size, transition_type)
