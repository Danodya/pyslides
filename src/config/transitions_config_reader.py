import json

class TransitionsConfig:

    # Load the transitions configuration file
    def load_transitions_config():
        # Path to the transitions configuration file
        config_path = '/Users/danodyaweerasinghe/Documents/MSc/Dissertation/22-24_CE901-CE911-CF981-SU_weerasinghe_danodya/src/config/transitions_config.json'
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
        return {item["slide"]: item["transition"] for item in config["demo"]}

    # Function to get the transition type for a given slide
    def get_transition_type(slide_transitions, slide_number):
        return slide_transitions.get(slide_number, 'fade_in')  # Default transition is 'fade_in'
