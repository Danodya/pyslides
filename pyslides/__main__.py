import argparse
import sys
from pathlib import Path
from pyslides.display import *
from pyslides.event_handler import handle_keydown, handle_keyup, handle_mouse
from pyslides.pdf_processor import *
from pyslides.transitions import draw_partial_slide, scroll_slide
from pyslides.config.transitions_config_reader import TransitionsConfig
from pyslides.state import AppState
import time

# Ensure the pyslides directory is in the Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pyslides'))

def main():
    """
    Main function that initializes the PDF viewer, handles user input, and manages the presentation loop.
    """

    state = AppState()

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
    # global image_paths
    state.image_paths = convert_pdf_to_images(pdf_path_abs, output_folder, state.window_size)
    images = [scale_image_to_fit(pygame.image.load(img_path), state.window_size) for img_path in state.image_paths]

    # Load slide transitions configuration for the specified PDF
    # global slide_transitions
    state.slide_transitions = TransitionsConfig.load_transitions_config(config_path_abs)

    # Load annotations if available
    state.text_annotations, state.pen_annotations = AnnotationsConfig.load_annotations_from_json(pdf_file)

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
                handle_keydown(event, images, pdf_file,
                               state)  # Handle keydown events
            elif event.type == pygame.KEYUP:
                handle_keyup(event, state)  # Handle keyup events
            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP):
                handle_mouse(event, images, state)  # Handle mouse events

        if state.black_screen_mode:
            state.screen.fill((0, 0, 0))  # Fill the screen with black if black screen mode is active
        else:
            if state.scrolling and current_time - last_scroll_time > 0.1:  # Scroll every 0.1 seconds
                scroll_slide(images, state.scroll_direction, state)
                last_scroll_time = current_time

            if state.show_help:
                display_help(state)  # Display the help screen
            elif state.show_overview:
                display_overview(images, state)  # Display the overview mode
            elif state.end_of_presentation:
                display_end_message(state)  # Display the end of the presentation message
            else:
                transition_config_current = TransitionsConfig.get_transition_config(state)
                transition_type_current = transition_config_current["transition"]
                if transition_type_current != constant.PARTIAL_SLIDE_TRANSITION:
                    display_slide(images, state)  # Display the current slide
                else:
                    draw_partial_slide(images, state)  # Draw the partial slide transition

            if state.spotlight_mode:
                draw_spotlight(state)  # Draw the spotlight effect
            elif state.highlight_mode:
                draw_highlight(state)  # Draw the highlight effect

            if not state.show_overview and state.zoom_level == 1 and not state.show_help:
                draw_text_annotations(state)  # Draw the text annotations
                draw_pen_annotations(state)  # Draw the pen annotations

            if state.show_initial_help_popup and current_time - initial_popup_start_time < 3:  # Show for 3 seconds
                display_initial_help_popup(state)  # Display the initial help popup
            elif state.show_initial_help_popup and current_time - initial_popup_start_time >= 3:
                state.show_initial_help_popup = False  # Hide the initial help popup

        pygame.display.flip()  # Update the screen

    pygame.quit()


if __name__ == '__main__':
    main()
