import copy
import json
import os
from pathlib import Path
import pygame
from pyslides.pdf_processor import scale_image_to_fit


class AnnotationsConfig:

    @staticmethod
    def rescale_annotations(text_annotations, pen_annotations, original_image_size, new_size, original_size,
                            new_window_size, original_window_size, is_fullscreen=False):
        """
        Rescales text and pen annotations when the window size or fullscreen mode changes.
        """
        # Create deep copies of the annotations to avoid modifying the originals
        rescaled_text_annotations, rescaled_pen_annotations = copy.deepcopy(text_annotations), copy.deepcopy(
            pen_annotations)
        if original_size:

            width_scale = new_size[0] / original_size[0]  # Calculate the width scaling factor
            height_scale = new_size[1] / original_size[1]  # Calculate the height scaling factor

            # Adjust text annotations
            for page, annotations in rescaled_text_annotations.items():
                for i, (rect, text) in enumerate(annotations):
                    if is_fullscreen:
                        # Adjust annotation position for fullscreen mode
                        x_adjust = ((new_window_size[0] - new_size[0]) / 2)
                        y_adjust = ((original_window_size[1] - original_image_size[1]) / 2)
                        new_rect = pygame.Rect(
                            int(round(x_adjust + rect.left * width_scale)),
                            int(round((rect.top - y_adjust) * height_scale)),
                            int(round(rect.width * width_scale)),
                            int(round(rect.height * height_scale))
                        )
                    else:
                        # Adjust annotation position for windowed mode
                        x_adjust = ((original_window_size[0] - original_size[0]) / 2)
                        y_adjust = ((new_window_size[1] - new_size[1]) / 2)
                        new_rect = pygame.Rect(
                            int(round((rect.left - x_adjust) * width_scale)),
                            int(round((rect.top * height_scale) + y_adjust)),
                            int(round(rect.width * width_scale)),
                            int(round(rect.height * height_scale))
                        )

                    # Update the annotation with the new position and size
                    rescaled_text_annotations[page][i] = (new_rect, text)

            # Adjust pen annotations
            for page, pen_strokes in rescaled_pen_annotations.items():
                for stroke in pen_strokes:
                    for i, (x, y) in enumerate(stroke):
                        if is_fullscreen:
                            # Adjust pen stroke position for fullscreen mode
                            x_adjust = ((new_window_size[0] - new_size[0]) / 2)
                            y_adjust = ((original_window_size[1] - original_image_size[1]) / 2)
                            stroke[i] = (
                                int(round(x_adjust + x * width_scale)), int(round((y - y_adjust) * height_scale)))
                        else:
                            # Adjust pen stroke position for windowed mode
                            x_adjust = ((original_window_size[0] - original_size[0]) / 2)
                            y_adjust = ((new_window_size[1] - new_size[1]) / 2)
                            stroke[i] = (
                                int(round((x - x_adjust) * width_scale)), int(round((y * height_scale) + y_adjust)))
        return rescaled_text_annotations, rescaled_pen_annotations

    @staticmethod
    def save_annotations_to_json(image, state, pdf_file):
        """
        Saves text and pen annotations to a JSON file.
        """
        rescaled_text_annotations, rescaled_pen_annotations = copy.deepcopy(state.text_annotations), copy.deepcopy(
            state.pen_annotations)
        if state.is_fullscreen:
            # Rescale annotations if in fullscreen mode
            fs_image_size = scale_image_to_fit(image, state.fullscreen_window_size)
            org_image_size = scale_image_to_fit(image, state.original_window_size)
            rescaled_text_annotations, rescaled_pen_annotations = AnnotationsConfig.rescale_annotations(
                state.text_annotations, state.pen_annotations, state.original_image_size,
                org_image_size.get_size(), fs_image_size.get_size(), state.original_window_size, state.fullscreen_window_size)
        annotations = {
            "text_annotations": {str(k): [{"rect": [r.left, r.top, r.width, r.height], "text": t} for r, t in v] for
                                 k, v in
                                 rescaled_text_annotations.items()},
            "pen_annotations": {str(k): [[(x, y) for x, y in points] for points in v] for k, v in
                                rescaled_pen_annotations.items()}
        }
        annotations_file = f"{Path(pdf_file).stem}_annotations.json"

        # Create the file if it doesn't exist
        if not os.path.exists(annotations_file):
            with open(annotations_file, 'w') as f:
                json.dump({}, f)  # Initialize an empty JSON object

        # Save annotations to the file
        with open(annotations_file, 'w') as f:
            json.dump(annotations, f, indent=4)  # Use indent for better readability
        print(f"Annotations saved to {annotations_file}")

    @staticmethod
    def load_annotations_from_json(pdf_file):
        """
        Loads text and pen annotations from a JSON file.
        """
        text_annotations, pen_annotations = {}, {}
        annotations_file = f"{Path(pdf_file).stem}_annotations.json"

        if os.path.exists(annotations_file):
            with open(annotations_file, 'r') as f:
                annotations = json.load(f)
                # Load text annotations from the JSON file
                text_annotations = {
                    int(k): [(pygame.Rect(a["rect"][0], a["rect"][1], a["rect"][2], a["rect"][3]), a["text"]) for a
                             in v]
                    for k, v in annotations.get("text_annotations", {}).items()}
                # Load pen annotations from the JSON file
                pen_annotations = {int(k): [points for points in v] for k, v in
                                   annotations.get("pen_annotations", {}).items()}
            print(f"Annotations loaded from {annotations_file}")
        else:
            print(f"No annotations file found at {annotations_file}")
        return text_annotations, pen_annotations
