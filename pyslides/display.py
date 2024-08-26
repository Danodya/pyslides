import pygame

from pyslides import constant
from pyslides.annotations import draw_text_annotations, draw_pen_annotations
from pyslides.config.annotations_config import AnnotationsConfig
from pyslides.config.transitions_config_reader import TransitionsConfig
from pyslides.pdf_processor import scale_image_to_fit


def toggle_fullscreen(images, prev_window_size, state):
    """
    Toggles fullscreen mode on and off, rescaling images and annotations as needed.
    """

    # Toggle fullscreen state
    state.is_fullscreen = not state.is_fullscreen
    if state.is_fullscreen:
        # Set the screen to fullscreen mode
        state.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        state.fullscreen_window_size = state.screen.get_size()  # Update fullscreen window size
    else:
        # Set the screen back to windowed mode
        state.screen = pygame.display.set_mode(state.original_window_size)

    new_window_size = state.screen.get_size()  # Get the new window size

    # Update the images to fit the new window size and track the new image size
    images[:] = [scale_image_to_fit(pygame.image.load(img_path), new_window_size) for img_path in state.image_paths]
    new_image_size = images[0].get_size()

    # Rescale annotations to match the new image size
    state.text_annotations, state.pen_annotations = AnnotationsConfig.rescale_annotations(state.text_annotations,
                                                                                          state.pen_annotations,
                                                                                          state.original_image_size,
                                                                                          new_image_size,
                                                                                          state.original_image_size,
                                                                                          new_window_size,
                                                                                          prev_window_size,
                                                                                          state.is_fullscreen)

    state.window_size = new_window_size  # Update global window size
    state.original_image_size = new_image_size  # Update the original image size to the new one

    # Recalculate slide positions if partial transition is active
    if state.current_page != 0 and (state.scrolling or constant.PARTIAL_SLIDE_TRANSITION ==
                                    TransitionsConfig.get_transition_config(state)["transition"]):
        halfway_pos = state.window_size[1] / 4
        prev_start_pos = ((state.window_size[1] - images[state.current_page - 1].get_height()) // 2)
        prev_slide_position = prev_start_pos - halfway_pos
        state.next_slide_position = prev_slide_position + images[state.current_page - 1].get_height()


def display_overview(images, state):
    """
    Displays thumbnails of all slides in an overview mode, with the currently highlighted slide faded out.
    """
    highlighted_page = state.focused_page
    state.screen.fill((0, 0, 0))  # Clear the screen with black
    margin = 10
    rows = cols = int(len(images) ** 0.5) + 1  # Calculate the number of rows and columns
    thumb_width = (state.window_size[0] - margin * (cols + 1)) // cols  # Calculate the thumbnail width
    thumb_height = (state.window_size[1] - margin * (rows + 1)) // rows  # Calculate the thumbnail height

    # Iterate through each thumbnail image and display it
    for i, thumbnail in enumerate([pygame.transform.scale(img, (thumb_width, thumb_height)) for img in images]):
        x = margin + (i % cols) * (thumb_width + margin)
        y = margin + (i // cols) * (thumb_height + margin)
        images[i].set_alpha(255)  # Just a quick fix for fade out slide in transition issue
        if i != highlighted_page:
            thumbnail.set_alpha(100)  # Fade out non-highlighted thumbnails
        state.screen.blit(thumbnail, (x, y))  # Display the thumbnail on the screen


def select_thumbnail(mouse_pos, images, state):
    """
    Selects a thumbnail in overview mode based on the mouse click position.
    """
    margin = 10
    rows = cols = int(len(images) ** 0.5) + 1  # Calculate the number of rows and columns
    thumb_width = (state.window_size[0] - margin * (cols + 1)) // cols  # Calculate the thumbnail width
    thumb_height = (state.window_size[1] - margin * (rows + 1)) // rows  # Calculate the thumbnail height

    # Iterate through thumbnails and check if the mouse click is within any thumbnail
    for i in range(len(images)):
        x = margin + (i % cols) * (thumb_width + margin)
        y = margin + (i // cols) * (thumb_height + margin)
        if x <= mouse_pos[0] <= x + thumb_width and y <= mouse_pos[1] <= y + thumb_height:
            state.focused_page = i  # Update the focused page
            state.current_page = state.focused_page  # Set the current page to the focused page
            state.show_overview = False  # Exit overview mode
            break


def highlight_thumbnail(mouse_pos, images, state):
    """
    Highlights a thumbnail in overview mode based on the mouse hover position.
    """
    margin = 10
    rows = cols = int(len(images) ** 0.5) + 1  # Calculate the number of rows and columns
    thumb_width = (state.window_size[0] - margin * (cols + 1)) // cols  # Calculate the thumbnail width
    thumb_height = (state.window_size[1] - margin * (rows + 1)) // rows  # Calculate the thumbnail height

    # Iterate through thumbnails and check if the mouse is hovering over any thumbnail
    for i in range(len(images)):
        x = margin + (i % cols) * (thumb_width + margin)
        y = margin + (i // cols) * (thumb_height + margin)
        images[i].set_alpha(255)  # Just a quick fix for fade out slide in transition issue
        if x <= mouse_pos[0] <= x + thumb_width and y <= mouse_pos[1] <= y + thumb_height:
            state.focused_page = i  # Update the focused page
            break


def display_slide(images, state):
    """
    Displays the current slide, considering zoom mode and any highlights.
    """

    state.screen.fill((0, 0, 0))  # Clear the screen with black
    image = images[state.current_page]

    if state.zoom_level > 1:
        # Scale the image for zooming
        zoomed_image = pygame.transform.scale(image, (
            int(image.get_width() * state.zoom_level), int(image.get_height() * state.zoom_level)))

        # Calculate the portion of the image to display at the center
        # New zoomed image size
        zoomed_width, zoomed_height = zoomed_image.get_size()
        # Center position on screen
        center_x, center_y = state.window_size[0] // 2, state.window_size[1] // 2
        # Calculate the offset from the zoom_pos to the center
        offset_x = int(state.zoom_pos[0] * state.zoom_level) - center_x
        offset_y = int(state.zoom_pos[1] * state.zoom_level) - center_y
        # Create the rectangle to be displayed
        zoom_rect = pygame.Rect(offset_x, offset_y, state.window_size[0], state.window_size[1])

        # Ensure the rectangle is within the bounds of the zoomed image
        zoom_rect = zoom_rect.clamp(pygame.Rect(0, 0, zoomed_width, zoomed_height))

        state.screen.blit(zoomed_image, (0, 0), zoom_rect)  # Display the zoomed image
    else:
        # Center the image on the screen
        image_rect = image.get_rect(center=(state.window_size[0] // 2, state.window_size[1] // 2))
        state.screen.blit(image, image_rect.topleft)  # Display the image

        # Draw annotations relative to the current image size
        draw_text_annotations(state)
        draw_pen_annotations(state)


def draw_spotlight(state):
    """
    Draws a spotlight effect on the slide, dimming the rest of the slide.
    """
    # Create a surface for the spotlight effect
    spotlight_surface = pygame.Surface(state.window_size, pygame.SRCALPHA)

    # Fill the surface with a semi-transparent black
    spotlight_surface.fill((0, 0, 0, 150))  # Use alpha value to dim

    # Cut out the spotlight area by making it fully transparent
    pygame.draw.circle(spotlight_surface, (0, 0, 0, 0), state.spotlight_position, state.spotlight_radius)

    # Blit the spotlight effect onto the main screen
    state.screen.blit(spotlight_surface, (0, 0))


def draw_highlight(state):
    """
    Draws a highlight rectangle over the slide, dimming the rest of the slide.
    """
    # global current_highlights
    # Create an overlay surface with transparency to dim the rest of the slide
    overlay_surface = pygame.Surface(state.window_size, pygame.SRCALPHA)
    overlay_surface.fill((0, 0, 0, 150))  # Semi-transparent black fill

    if state.current_highlights:
        for rect in state.current_highlights:
            # Cut out the highlight area by making it fully transparent
            pygame.draw.rect(overlay_surface, (0, 0, 0, 0), rect)

    # Blit the overlay to the screen
    state.screen.blit(overlay_surface, (0, 0))


def display_end_message(state):
    """
    Displays a message indicating the end of the presentation.
    """
    state.screen.fill((0, 0, 0))  # Clear the screen with black
    text = state.font.render("You have reached the end of the presentation", True, (255, 255, 255))
    text_rect = text.get_rect(
        center=(state.window_size[0] // 2, state.window_size[1] // 2))  # Center the text on the screen
    state.screen.blit(text, text_rect)  # Display the end message


def display_help(state):
    """
    Displays a help screen with key commands and instructions.
    """
    state.screen.fill((75, 75, 75))  # Fill the screen with a dark gray color
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
        text = state.font.render(line, True, (255, 255, 255))  # Render each line of help text
        state.screen.blit(text, (50, y_offset))  # Display the help text
        y_offset += 40  # Move to the next line


def display_initial_help_popup(state):
    """
    Displays an initial help popup with a short message.
    """
    popup_surface = pygame.Surface((state.window_size[0] * 0.8, 100), pygame.SRCALPHA)
    popup_surface.fill((0, 0, 0, 200))  # Create a semi-transparent black popup
    popup_rect = popup_surface.get_rect(
        center=(state.window_size[0] // 2, state.window_size[1] // 2))  # Center the popup on the screen
    text = state.font.render("Press 'H' for help", True, (255, 255, 255))  # Render the popup text
    text_rect = text.get_rect(center=popup_rect.center)  # Center the text within the popup
    state.screen.blit(popup_surface, popup_rect)  # Display the popup
    state.screen.blit(text, text_rect)  # Display the popup text
