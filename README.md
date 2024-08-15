# PDF Viewer with Slide Transitions

## Overview

This PDF Viewer with Slide Transitions is a Python-based tool designed to provide an enhanced experience for presenting PDF documents. Built on the `pygame` and `PyMuPDF (fitz)` libraries, this software allows users to navigate through PDF slides with smooth transitions, annotate slides with text and pen tools, and utilize features like fullscreen mode, zoom, and spotlight. The viewer also supports saving and loading annotations, making it ideal for lecture presentations, workshops, or any situation where interactive PDF viewing is needed.

## Features

- **Slide Transitions:** Smooth slide transitions for a professional presentation experience.
- **Fullscreen Mode:** Toggle fullscreen mode for an immersive presentation.
- **Annotations:** Add text and pen annotations directly onto the slides. Annotations are saved and can be loaded for future sessions.
- **Zoom Functionality:** Zoom in and out on slides with adjustable zoom levels.
- **Spotlight Mode:** Highlight specific areas of a slide with an adjustable spotlight.
- **Highlight Mode:** Highlight portions of the slide with a semi-transparent overlay.
- **Overview Mode:** Quickly navigate to any slide using the thumbnail overview.
- **Partial Slide Transition:** Smoothly scroll between portions of a slide.

## Requirements

- Python 3.6 or higher
- `pygame`
- `PyMuPDF (fitz)`

You can install the required Python packages using pip:

```bash
pip install pygame PyMuPDF
```

## Usage

### Command Line Arguments

- **`pdf_file`**: The path to the PDF file you want to present.
- **`--config_file`**: (Optional) The path to the configuration file for custom slide transitions.

### Running the Viewer

To start the PDF Viewer, run the following command:

```bash
python viewer.py your_pdf_file.pdf --config_file your_config.json
```
### Key Features

- **PDF to Image Conversion**: Converts each page of the provided PDF into an image, which is then displayed as a slide in the viewer.
  
- **Slide Transitions**: The viewer supports a variety of slide transitions, which can be customized through a configuration file.

- **Annotations**: You can add text and pen annotations to your slides, which are saved and can be reloaded with the presentation.

- **Spotlight and Highlight Modes**: These modes allow you to emphasize parts of your slide during the presentation.

- **Fullscreen and Windowed Modes**: Easily toggle between fullscreen and windowed modes with proper scaling of annotations.

### Shortcuts

- **RIGHT ARROW / PAGE DOWN**: Next slide
- **LEFT ARROW / PAGE UP**: Previous slide
- **UP ARROW**: Scroll up (for partial slides)
- **DOWN ARROW**: Scroll down (for partial slides)
- **S**: Toggle spotlight mode
- **R**: Toggle highlight mode
- **+ / =**: Increase spotlight radius
- **-**: Decrease spotlight radius
- **F**: Toggle fullscreen mode
- **TAB**: Toggle overview mode
- **RETURN**: Select slide in overview mode
- **H**: Toggle help menu
- **Ctrl + Mouse Wheel**: Zoom in/out
- **T**: Add text annotation
- **P**: Toggle pen mode for freehand drawing
- **RETURN**: Stop entering text in text annotation mode
- **Ctrl + S**: Save annotations

### Annotations

When in fullscreen mode, annotations are rescaled to fit the original windowed size, ensuring consistent placement when switching between windowed and fullscreen modes. Annotations are saved in JSON format and can be loaded upon reopening the PDF file.

### Spotlight and Highlight Modes

Use the spotlight and highlight features to emphasize areas of your slide. Adjust the spotlight size with `+` and `-` keys.

## Custom Transitions

The software supports custom slide transitions, which can be defined in a JSON configuration file passed via the `--config_file` argument.

## Example Transition Configuration

Here is a sample configuration:

```json
{
  "General": {
    "transition": "fade_in",
    "transition-duration": "1s",
    "reversal-strategy": "invert-transition"
  },
  "Slide 1": {
    "transition": "pull",
    "transition-duration": "1s",
    "reversal-strategy": "invert-transition"
  },
  "Slide 2": {
    "transition": "fade_out_slide_in",
    "transition-duration": "1s",
    "reversal-strategy": "invert-transition"
  }
}
```
This configuration applies a fade transition as the General transition that applies to all slides. from slide 1 (except the starting slide) there applies the specified transitions. If a transition is not specified for a slide, general transition will be applied.