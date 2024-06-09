import fitz  # PyMuPDF
import pygame
import os
import constant

pygame.init()

# Define the initial window size
window_size = (constant.SCREEN_WIDTH, constant.SCREEN_HIGHT)
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption(constant.DISPLAY_CAPTION)

# Function to toggle full screen
def toggle_fullscreen():
    global screen, window_size
    if screen.get_flags() & pygame.FULLSCREEN:
        window_size = (constant.SCREEN_WIDTH, constant.SCREEN_HIGHT)
        screen = pygame.display.set_mode(window_size)
    else:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        window_size = screen.get_size()  # Update window_size to full screen size

# Function to convert pdf to images
def convert_pdf_to_images(pdf_path, output_folder):
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)
    images = []

    # Specify a scaling factor for higher resolution
    zoom_x = 2.0  # Horizontal zoom
    zoom_y = 2.0  # Vertical zoom
    matrix = fitz.Matrix(zoom_x, zoom_y)

    # Iterate through each page
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        # Render the page to a high-resolution pixmap
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

# Function to display converted images
def display_images_with_pygame(image_paths, window_size):
    images = [pygame.image.load(img) for img in image_paths]
    scaled_images = [scale_image_to_fit(img, window_size) for img in images]
    current_page = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    current_page = (current_page + 1) % len(scaled_images)
                elif event.key == pygame.K_LEFT:
                    current_page = (current_page - 1) % len(scaled_images)
                elif event.key == pygame.K_f:  # Press 'f' to toggle full screen
                    toggle_fullscreen()
                    # Rescale images to new window size
                    window_size = screen.get_size()
                    scaled_images = [scale_image_to_fit(img, window_size) for img in images]
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button to go to the next image
                    current_page = (current_page + 1) % len(scaled_images)

        screen.fill((0, 0, 0))
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
image_paths = convert_pdf_to_images(pdf_path, output_folder)

# Display images using Pygame
display_images_with_pygame(image_paths, window_size)
