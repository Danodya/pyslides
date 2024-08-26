import os
import fitz  # PyMuPDF for PDF processing
import pygame


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

    print(f"\rLoading completed. {total_pages}/{total_pages} processed.               ")  # Clear the line after
    # completion
    return images


def scale_image_to_fit(image, window_size):
    """
    Scales an image to fit within the given window size while maintaining its aspect ratio.
    """
    # Calculate the scale factor to fit the image within the window size
    scale_factor = min(window_size[0] / image.get_width(), window_size[1] / image.get_height())
    new_size = (int(image.get_width() * scale_factor), int(image.get_height() * scale_factor))
    return pygame.transform.scale(image, new_size)  # Return the scaled image
