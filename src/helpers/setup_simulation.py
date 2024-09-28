import pygame

class Setup:
    def __init__(self, window_size):
        path_font = "../assets/font/OpenSans-Light.ttf"
        self.font_titles = pygame.font.Font(path_font, 23)
        self.font_texts = pygame.font.Font(path_font, 16)

        width_rect = window_size[0]
        height_rect = 30
        self.rect_input_user_field = pygame.Rect(0, window_size[1]-height_rect, width_rect, height_rect)
        self.input_field_active = False
        self.user_new_value = ''
        self.input_field_values = {
            "window": None,
            "name_var": None,
            "value": None,
        }

        self.variables = {
            "environmental-settings": {
                "rect_window": pygame.Rect(100, 100, 300, 300),
                "variables": {
                        "gravity": {
                        "value": 9.81,
                        "rect": None,
                        "type": "m/s²"
                    },
                    "air-density-sea-level": {
                        "value": 1.221,
                        "rect": None,
                        "type": "kg/m³"
                    },
                    "wind": {
                        "value": 0,
                        "rect": None,
                        "type": None
                    },
                },
            },
            "rocket-specific-settings": {
                "rect_window": pygame.Rect(500, 100, 300, 300),
                "variables": {
                        "dry-mass": {
                        "value": 10.0,
                        "rect": None,
                        "type": "kg"
                    },
                    "fuel-mass": {
                        "value": 0,
                        "rect": None,
                        "type": "kg"
                    },
                    "cd": {
                        "value": 0.7,
                        "rect": None,
                        "type": None
                    },
                },
            },
            "engine-settings": {
                "rect_window": pygame.Rect(1000, 100, 300, 300),
                "variables": {
                        "name": {
                        "value": "test_1",
                        "rect": None,
                        "type": None
                    },
                    "power": {
                        "value": 120,
                        "rect": None,
                        "type": "N"
                    },
                    "isp": { 
                        # (specific impulse) solid engine = 200-300 seconds, liquid engine = 300-450 change in get_mass_flow_rate
                        "value": 300,
                        "rect": None,
                        "type": "s",
                    },
                    "thrust_vectoring": {
                        # maximum angle by which the negine can gimbal
                        "value": 0,
                        "rect": None,
                        "type": "°",
                    },
                    "num_engines": {
                        "value": 0,
                        "rect": None,
                        "type": None
                    }
                },
            },
            "mission-specific-parameters": {
                "rect_window": pygame.Rect(1400, 100, 300, 300),
                "variables": {
                    "target-altitude": {
                        "value": None,
                        "rect": None,
                        "type": "m",
                    },
                    "target-orbit": {
                        "value": None,
                        "rect": None,
                        "type": None,
                    },
                    "start-planet": {
                        "value": None,
                        "rect": None,
                        "type": None,
                    },
                    "start-angle": {
                        "value": 0,
                        "rect": None,
                        "type": "°"
                    },
                    "start-altitude": {
                        "value": 0,
                        "rect": None,
                        "type": "m"
                    },
                },
            },
        }
        self.variables_for_reset = self.variables.copy()
        

    def create_rect_for_values(self):
        def place_values_by_window(name_window, rect_window, values):
            start_y = rect_window.y+55
            start_x = rect_window.x+rect_window.width-90

            for subkey, subvalue in values.items():
                rect_value = pygame.Rect(start_x, start_y, 45, 25)
                self.variables[name_window]["variables"][subkey]["rect"] = rect_value
                start_y += 35
        
        for key, value in self.variables.items():
            place_values_by_window(key, self.variables[key]["rect_window"], self.variables[key]["variables"])
                
        
    
    def run(self, screen):
        for key, value in self.variables.items():
            # draw background window
            pygame.draw.rect(screen, "yellow", self.variables[key]["rect_window"])

            # draw title window
            self.draw_text(key.capitalize(), screen, self.font_titles, self.variables[key]["rect_window"].topleft)

            # draw: variable, rect background value, values inside, type of the value
            for subkey in self.variables[key]["variables"].keys():
                # draw variable
                pos_subkey = (
                    self.variables[key]["variables"][subkey]["rect"].topleft[0]-200,
                    self.variables[key]["variables"][subkey]["rect"].topleft[1]
                ) 
                self.draw_text(subkey, screen, self.font_texts, pos_subkey)

                # draw rect field
                pygame.draw.rect(screen, "orange", self.variables[key]["variables"][subkey]["rect"])
                # draw value inside rect field
                self.draw_text(
                    f"{self.variables[key]['variables'][subkey]['value']}",
                    screen, self.font_texts, (self.variables[key]["variables"][subkey]["rect"].topleft[0]+2, self.variables[key]["variables"][subkey]["rect"].topleft[1])
                )
                # draw type of the value outside rect field
                if self.variables[key]['variables'][subkey]['type'] != None:
                    pos = (
                        self.variables[key]['variables'][subkey]['rect'].topright[0]+2,
                        self.variables[key]['variables'][subkey]['rect'].topright[1]
                    )
                    self.draw_text(
                        self.variables[key]['variables'][subkey]['type'], screen, self.font_texts, pos
                    )

            # draw user input field
        pygame.draw.rect(screen, "gray", self.rect_input_user_field)
        self.draw_text(f"> {self.user_new_value}", screen, self.font_texts, (self.rect_input_user_field.x, self.rect_input_user_field.y+3))


    def draw_text(self, text, screen, font, pos):
        text_render = font.render(text, True, "black")
        screen.blit(text_render, pos)


    def check_event_edit_variable(self, mouse_pos):
        for key, value in self.variables.items():
            for subkey, subvalue in self.variables[key]["variables"].items():
                if self.variables[key]["variables"][subkey]["rect"].collidepoint(mouse_pos):
                    self.input_field_active = True
                    self.input_field_values["window"] = key
                    self.input_field_values["name_var"] = subkey
                    self.input_field_values["value"] = self.variables[key]["variables"][subkey]["value"]

                    self.user_new_value = f"{self.input_field_values['name_var']}: {self.input_field_values['value']}"

                    break
                else:
                    self.input_field_active = False
                    

    def edit_variable(self, event):
        def process_text_from_input(text):
            text, value = text.split(" ")
            try:
                value = float(value)
                self.variables[self.input_field_values["window"]]["variables"][self.input_field_values["name_var"]]["value"] = value
            except ValueError:
                print("Not working")
        
        if event.key == pygame.K_BACKSPACE:
            if len(self.user_new_value) > len(self.input_field_values["name_var"])+2:
                self.user_new_value = self.user_new_value[:-1]
        elif event.key == pygame.K_RETURN:
            process_text_from_input(self.user_new_value)
        else:
            self.user_new_value += event.unicode
