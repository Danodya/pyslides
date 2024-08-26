import pygame


def draw_text_annotations(state):
    """
    Draws text annotations on the current slide.
    """
    if state.current_page in state.text_annotations:
        for rect, text in state.text_annotations[state.current_page]:
            if rect:  # Draw only if rect is not None
                render_text_in_box(text, rect, state)

    # Render the text being entered
    if state.is_entering_text and state.annotation_rect:
        pygame.draw.rect(state.screen, (0, 0, 255), state.annotation_rect, 2)  # Draw the rectangle
        render_text_in_box(state.current_text, state.annotation_rect,
                           state)  # Render the entered text inside the rectangle


def draw_pen_annotations(state):
    """
    Draws the pen annotations on the current slide.
    """
    if state.current_page in state.pen_annotations:
        for points in state.pen_annotations[state.current_page]:
            if len(points) > 1:  # Ensure there are enough points to draw
                pygame.draw.lines(state.screen, (255, 0, 0), False, points, 2)  # Draw the pen stroke

    # Draw the current pen points being drawn
    if state.is_drawing_pen and len(state.pen_points) > 1:
        pygame.draw.lines(state.screen, (255, 0, 0), False, state.pen_points, 2)


def adjust_annotation_rect(state):
    """
    Adjusts the size of the annotation rectangle dynamically as text is entered.
    """
    # global annotation_rect
    if not state.annotation_rect:
        return
    words = state.current_text.split(' ')  # Split the text into words
    space_width = state.annotation_font.size(' ')[0]  # Get the width of a space character
    max_width = state.annotation_rect.width  # Get the maximum width for the text
    x, y = state.annotation_rect.topleft
    line_height = state.annotation_font.get_height()  # Get the height of a line of text
    current_line = []  # Initialize the current line of text
    max_height = 0  # Initialize the maximum height of the text

    for word in words:
        word_width, word_height = state.annotation_font.size(word)
        if word_width > max_width:
            continue  # Skip too long words
        if sum(state.annotation_font.size(w)[0] for w in current_line) + word_width + space_width <= max_width:
            current_line.append(word)  # Add the word to the current line
        else:
            max_height += line_height  # Move to the next line
            current_line = [word]
    if current_line:
        max_height += line_height  # Add the height of the last line

    state.annotation_rect.height = max_height  # Adjust the height of the annotation rectangle


def render_text_in_box(text, rect, state):
    """
    Renders text inside a rectangular box, ensuring it wraps appropriately.
    """
    words = text.split(' ')  # Split the text into words
    space_width = state.annotation_font.size(' ')[0]  # Get the width of a space character
    max_width = rect.width  # Get the maximum width for the text
    max_height = rect.height  # Get the maximum height for the text
    x, y = rect.topleft
    line_height = state.annotation_font.get_height()  # Get the height of a line of text
    lines = []  # Initialize the list of lines
    current_line = []  # Initialize the current line of text

    for word in words:
        word_width, word_height = state.annotation_font.size(word)
        if word_width > max_width:
            continue  # Skip too long words
        if sum(state.annotation_font.size(w)[0] for w in current_line) + word_width + space_width <= max_width:
            current_line.append(word)  # Add the word to the current line
        else:
            lines.append(' '.join(current_line))  # Add the current line to the list of lines
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))  # Add the last line to the list of lines

    for line in lines:
        line_surface = state.annotation_font.render(line, True, (0, 0, 255))  # Render the line of text
        state.screen.blit(line_surface, (x, y))  # Display the line of text
        y += line_height  # Move to the next line
        if y + line_height > rect.bottom:
            break  # Stop drawing if text exceeds the box
