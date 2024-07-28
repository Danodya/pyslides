import json
import pyslides.constant as constant


class TransitionsConfig:

    general_settings = {}
    
    # Load the transitions configuration file
    @staticmethod
    def load_transitions_config(config_file_name):
        # Path to the transitions configuration file
        config_path = f'pyslides/config/{config_file_name}'
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)

        # Extract general settings
        TransitionsConfig.general_settings = config.get("General", {
            "transition": "fade_in",
            "transition-duration": "1s",
            "reversal-strategy": "invert-transition"
        })

        # Load transitions for each slide and apply general settings if specific settings are missing
        slide_transitions = {}
        for key, value in config.items():
            if key.startswith("Slide"):
                slide_number = int(key.split()[1])
                slide_transitions[slide_number] = {
                    "transition": value.get("transition", TransitionsConfig.general_settings["transition"]),
                    "duration": value.get("transition-duration", TransitionsConfig.general_settings["transition-duration"]),
                    "reversal-strategy": value.get("reversal-strategy", TransitionsConfig.general_settings["reversal-strategy"])
                }
        # breakpoint()
        return slide_transitions

    # Function to get the transition type and duration for a given slide
    @staticmethod
    def get_transition_config(slide_transitions, slide_number):
        return slide_transitions.get(slide_number,
                                     {"transition": TransitionsConfig.general_settings["transition"],
                                      "duration": TransitionsConfig.general_settings["transition-duration"],
                                      "reversal-strategy": TransitionsConfig.general_settings["reversal-strategy"]})
        # Default transition, duration and reverse strategy

    # Function to check the reversal strategy of a given slide
    @staticmethod
    def check_reversal_strategy(reversal_strategy_type):
        match reversal_strategy_type:
            case constant.INVERT_TRANSITION:
                return True
            case constant.KEEP_ORIGINAL:
                return False

