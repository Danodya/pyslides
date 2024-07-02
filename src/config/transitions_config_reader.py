import json

class TransitionsConfig:
    
    # Load the transitions configuration file
    @staticmethod
    def load_transitions_config(pdf_name):
        # Path to the transitions configuration file
        config_path = '/home/danodya/Documents/22-24_CE901-CE911-CF981-SU_weerasinghe_danodya/src/config/transitions_config.json'
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
        
        # Load transitions for the specified PDF
        pdf_config = config.get(pdf_name, {})
        return {int(key.split()[1]): {"transition": value["transition"], "duration": value["transition-duration"]} for key, value in pdf_config.items()}

    #Function to get the transition type and duration for a given slide
    @staticmethod
    def get_transition_config(slide_transitions, slide_number):
        return slide_transitions.get(slide_number, {"transition": "fade_in", "duration": "1s"})  # Default transition and duration
