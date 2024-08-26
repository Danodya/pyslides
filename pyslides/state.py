import pygame

from pyslides import constant


class AppState:
    def __init__(self):
        # Define the initial window size
        self.original_window_size = (constant.SCREEN_WIDTH, constant.SCREEN_HIGHT)
        self.window_size = self.original_window_size
        print("window_size", self.window_size)
        self.fullscreen_window_size = self.original_window_size  # initialized to original window size
        self.screen = pygame.display.set_mode(self.window_size)
        print("screen", self.screen)
        pygame.display.set_caption(constant.DISPLAY_CAPTION)

        # Initialize Pygame's font module for text rendering
        pygame.font.init()
        self.font = pygame.font.Font(None, 36)  # Default font, size 36 for general text
        self.annotation_font = pygame.font.SysFont("timesnewroman", 18)  # Font for annotations

        # Global state variables to track various modes and states in the presentation
        self.is_fullscreen = False  # Track whether fullscreen mode is active
        self.show_overview = False  # Track whether overview mode is active
        self.current_page = 0  # Track the current slide being displayed
        self.focused_page = 0  # Track the currently highlighted slide in overview mode
        self.prev_slide_position = 0  # Y position of the previous slide during partial slide transition
        self.next_slide_position = 0  # Y position of the next slide during partial slide transition
        self.scrolling = False  # Flag to indicate if scrolling is active (for partial slides)
        self.scroll_direction = 0  # Direction of scrolling: -1 for up, 1 for down
        self.scroll_start_time = 0  # Time when scrolling started
        self.spotlight_mode = False  # Flag to indicate if spotlight mode is active
        self.highlight_mode = False  # Flag to indicate if highlight mode is active
        self.highlight_start = None  # Start position for the highlight rectangle
        self.highlight_rects = {}  # Store highlight rectangles per slide
        self.current_highlights = []  # Current highlights being drawn
        self.spotlight_radius = 100  # Initial spotlight radius
        self.spotlight_position = (constant.SCREEN_WIDTH // 2, constant.SCREEN_HIGHT // 2)  # Initial spotlight position
        self.end_of_presentation = False  # Flag to indicate the end of the presentation
        self.show_help = False  # Flag to indicate if help screen is active
        self.show_initial_help_popup = True  # Flag to show the initial help popup
        self.zoom_level = 1  # Initial zoom level (1 = no zoom)
        self.max_zoom_level = 4  # Maximum zoom level allowed
        self.min_zoom_level = 1  # Minimum zoom level allowed
        self.zoom_pos = (0, 0)  # Position around which zoom is centered
        self.black_screen_mode = False  # Flag to indicate if black screen mode is active

        # Global variables for text annotation
        self.is_drawing_box = False  # Flag to indicate if an annotation box is being drawn
        self.annotation_start = None  # Starting position for drawing the annotation box
        self.annotation_rect = None  # Rectangle defining the annotation area
        self.is_entering_text = False  # Flag to indicate if text is being entered
        self.current_text = ""  # Current text being entered in the annotation
        self.text_annotations = {}  # Store list of (rect, text) per slide
        self.dragging = False  # Flag for dragging the annotation box

        # Global variables for pen annotations
        self.is_drawing_pen = False  # Flag to indicate if pen mode is active
        self.pen_points = []  # Store points for the current pen stroke
        self.pen_annotations = {}  # Store list of pen points per slide
        self.original_image_size = []  # Store the original size of the images
