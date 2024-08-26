import json
import os

import pyslides.constant as constant


class TransitionsConfig:
    """
    A class to handle the loading and retrieval of slide transition configurations.
    """

    # Class-level dictionary to store general settings applied across all slides
    general_settings = {}

    @staticmethod
    def load_transitions_config(config_path_abs):
        """
        Loads the transitions configuration from a JSON file.

        :param config_path_abs: The absolute path to the configuration file.
        :return: A dictionary with slide-specific transition settings.
        """
        config = {}
        if os.path.exists(config_path_abs):  # Check if the config file exists
            with open(config_path_abs, 'r') as config_file:
                config = json.load(config_file)  # Load the JSON configuration file

        # Extract general settings applicable to all slides if specific settings are not provided
        TransitionsConfig.general_settings = config.get("General", {
            "transition": "fade_in",  # Default transition type
            "transition-duration": "1s",  # Default transition duration
            "reversal-strategy": "invert-transition"  # Default reversal strategy
        })

        # Dictionary to store transitions for each slide
        slide_transitions = {}
        for key, value in config.items():
            if key.startswith("Slide"):  # Identify slide-specific settings
                slide_number = int(key.split()[1])  # Extract the slide number
                slide_transitions[slide_number] = {
                    # Use slide-specific settings or fallback to general settings
                    "transition": value.get("transition", TransitionsConfig.general_settings["transition"]),
                    "duration": value.get("transition-duration",
                                          TransitionsConfig.general_settings["transition-duration"]),
                    "reversal-strategy": value.get("reversal-strategy",
                                                   TransitionsConfig.general_settings["reversal-strategy"])
                }

        return slide_transitions  # Return the dictionary of slide-specific transition settings

    @staticmethod
    def get_transition_config(state):
        """
        Retrieves the transition configuration for the current slide.

        :param state: The AppState instance holding the current application state.
        :return: A dictionary with the transition type, duration, and reversal strategy for the current slide.
        """
        # Get the transition settings for the current slide or use general settings if not defined
        return state.slide_transitions.get(state.current_page, {
            "transition": TransitionsConfig.general_settings["transition"],
            "duration": TransitionsConfig.general_settings["transition-duration"],
            "reversal-strategy": TransitionsConfig.general_settings["reversal-strategy"]
        })

    @staticmethod
    def check_reversal_strategy(reversal_strategy_type):
        """
        Checks the reversal strategy for a given slide transition.

        :param reversal_strategy_type: The type of reversal strategy to check.
        :return: A boolean indicating whether to invert the transition based on the reversal strategy.
        """
        match reversal_strategy_type:
            # If the strategy is to invert the transition, return True
            case constant.INVERT_TRANSITION:
                return True
            # If the strategy is to keep the original transition, return False
            case constant.KEEP_ORIGINAL:
                return False
