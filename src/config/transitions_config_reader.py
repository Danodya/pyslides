import json
import src.constant as constant


class TransitionsConfig:
    
    # Load the transitions configuration file
    @staticmethod
    def load_transitions_config(config_file_name):
        # Path to the transitions configuration file
        config_path = f'/Users/danodyaweerasinghe/Documents/MSc/Dissertation/22-24_CE901-CE911-CF981-SU_weerasinghe_danodya/src/config/{config_file_name}'
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
        
        # Load transitions for the slides in the provided configuration
        return {int(key.split()[1]): {"transition": value["transition"], "duration": value["transition-duration"],
                                      "reversal-strategy": value["reversal-strategy"]} for key, value in config.items()}

    # Function to get the transition type and duration for a given slide
    @staticmethod
    def get_transition_config(slide_transitions, slide_number):
        return slide_transitions.get(slide_number,
                                     {"transition": "fade_in", "duration": "1s", "reversal-strategy": "keep-original"})
        # Default transition, duration and reverse strategy

    # Function to check the reversal strategy of a given slide
    @staticmethod
    def check_reversal_strategy(reversal_strategy_type):
        match reversal_strategy_type:
            case constant.INVERT_TRANSITION:
                return True
            case constant.KEEP_ORIGINAL:
                return False

