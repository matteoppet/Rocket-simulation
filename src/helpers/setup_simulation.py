import pygame
import copy

class Setup:
    def __init__(self, window_size, rocket):
        self.rocket = rocket

        path_font_regular = "../assets/font/OpenSans-Light.ttf"
        path_font_bold = "../assets/font/OpenSans-SemiBold.ttf"

        self.font_titles = pygame.font.Font(path_font_bold, 25)
        self.font_texts = pygame.font.Font(path_font_regular, 16)
        self.font_buttons = pygame.font.Font(path_font_regular, 14)

        self.pad_bottom_texts = 35
        self.pad_bottom_from_title_window = 55
        self.pad_right_from_rect_field = 200

        self.red_button_color = "#FF0000"
        self.green_button_color = "#50D890"
        self.black_background_button_color = "#272727"

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
                "rect_window": pygame.Rect(150, 100, 300, 300),
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
                "rect_window": pygame.Rect(550, 100, 300, 300),
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
                "rect_window": pygame.Rect(950, 100, 300, 300),
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
                "rect_window": pygame.Rect(1350, 100, 300, 300),
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
        self.create_rect_for_values()
        self.systems = {
            "NO-GO/GO system": {
                "rect_window": pygame.Rect(500, 500, 300, 300),
                "variables": {
                    "environment": "NO-GO",
                    "rocket": "GO",
                    "engine": "NO-GO",
                    "mission": "NO-GO"
                }
            },
        }

        self.buttons = {
            "launch": pygame.Rect(window_size[0]-100, window_size[1]-100, 60, 40)
        }

        self.problems_for_no_go = {}


    def create_rect_for_values(self):
        def place_values_by_window(name_window, rect_window, values):
            start_y = rect_window.y+self.pad_bottom_from_title_window
            start_x = rect_window.x+rect_window.width-90

            width_rect_field = 50
            height_rect_field = 25
            for subkey, subvalue in values.items():
                rect_value = pygame.Rect(start_x, start_y, width_rect_field, height_rect_field)
                self.variables[name_window]["variables"][subkey]["rect"] = rect_value
                start_y += self.pad_bottom_texts
        
        for key, value in self.variables.items():
            place_values_by_window(key, self.variables[key]["rect_window"], self.variables[key]["variables"])
                
        
    
    def run(self, screen, clock):
        for key, value in self.variables.items():
            # draw title window
            self.draw_text(key.capitalize(), screen, self.font_titles, self.variables[key]["rect_window"].topleft)

            # draw: variable, rect background value, values inside, type of the value
            for subkey in self.variables[key]["variables"].keys():
                # draw variable
                pos_subkey = (
                    self.variables[key]["variables"][subkey]["rect"].topleft[0]-self.pad_right_from_rect_field,
                    self.variables[key]["variables"][subkey]["rect"].topleft[1]
                ) 
                self.draw_text(subkey, screen, self.font_texts, pos_subkey)

                # draw rect field (and background)
                self.draw_rect_field(screen, "white", self.variables[key]["variables"][subkey]["rect"])
                # draw value inside rect field
                self.draw_text(
                    f"{self.variables[key]['variables'][subkey]['value']}",
                    screen, self.font_texts, (self.variables[key]["variables"][subkey]["rect"].topleft[0]+2, self.variables[key]["variables"][subkey]["rect"].topleft[1])
                )
                # draw type of the value outside rect field
                if self.variables[key]['variables'][subkey]['type'] != None:
                    pos = (
                        self.variables[key]['variables'][subkey]['rect'].topright[0]+5,
                        self.variables[key]['variables'][subkey]['rect'].topright[1]
                    )
                    self.draw_text(
                        self.variables[key]['variables'][subkey]['type'], screen, self.font_texts, pos
                    )

        # draw windows systems dict
        for key, value in self.systems.items():
            self.draw_text(key.capitalize(), screen, self.font_titles, self.systems[key]["rect_window"].topleft)

            start_y_subvalue_systems = self.systems[key]["rect_window"].topleft[1]+self.pad_bottom_from_title_window
            for subkey, subvalue in self.systems[key]["variables"].items():
                self.draw_text(subkey, screen, self.font_texts, ( self.systems[key]["rect_window"].topleft[0], start_y_subvalue_systems))
                rect_value = pygame.Rect(self.systems[key]["rect_window"].topleft[0]+self.pad_right_from_rect_field, start_y_subvalue_systems, 50, 30)

                if subvalue.upper() == "NO-GO":
                    self.draw_rect_field(screen, self.red_button_color, rect_value)
                    self.draw_text(subvalue.upper(), screen, self.font_buttons, (rect_value.topleft[0]+2, rect_value.topleft[1]+4))
                if subvalue.upper() == "GO":
                    self.draw_rect_field(screen, self.green_button_color, rect_value)
                    self.draw_text(subvalue.upper(), screen, self.font_buttons, (rect_value.topleft[0]+14, rect_value.topleft[1]+4))

                self.validation_variables()

                start_y_subvalue_systems += self.pad_bottom_texts


        self.draw_rect_field(screen, "white", self.rect_input_user_field)
        self.draw_text(f"> {self.user_new_value}", screen, self.font_texts, (self.rect_input_user_field.x, self.rect_input_user_field.y+3))

        # draw other buttons
        for key, value in self.buttons.items():
            if key == "reset":
                self.draw_rect_field(screen, self.red_button_color, value)
            else:
                self.draw_rect_field(screen, self.green_button_color, value)
            
            text_button = self.font_buttons.render(key, True, self.black_background_button_color)
            screen.blit(text_button, (value.topleft[0]+8, value.topleft[1]+9))


    def draw_rect_field(self, screen, color, rect_hover):
        rect_background = pygame.Rect(rect_hover.topleft[0]-1, rect_hover.topleft[1]-1, rect_hover.width+2, rect_hover.height+2)
        pygame.draw.rect(screen, self.black_background_button_color, rect_background)
        pygame.draw.rect(screen, color, rect_hover)


    def draw_text(self, text, screen, font, pos):
        text_render = font.render(text, True, self.black_background_button_color)
        screen.blit(text_render, pos)


    def check_event_edit_variable(self, mouse_pos):
        for key in self.variables.keys():
            for subkey in self.variables[key]["variables"].keys():
                if self.variables[key]["variables"][subkey]["rect"].collidepoint(mouse_pos):
                    self.input_field_values["window"] = key
                    self.input_field_values["name_var"] = subkey
                    self.input_field_values["value"] = self.variables[key]["variables"][subkey]["value"]
                    self.user_new_value = f"{self.input_field_values['name_var']}: {self.input_field_values['value']}"
                    break


    def edit_variable(self, event):
        def process_text_from_input(text):
            text, value = text.split(" ")
            try:
                value = float(value)
                self.variables[self.input_field_values["window"]]["variables"][self.input_field_values["name_var"]]["value"] = value
                self.user_new_value = ''
                self.input_field_values["window"] = None
                self.input_field_values["name_var"] = None
                self.input_field_values["value"] = None
            except ValueError:
                print("Not working")
        
        if event.key == pygame.K_BACKSPACE:
            if len(self.user_new_value) > len(self.input_field_values["name_var"])+2:
                self.user_new_value = self.user_new_value[:-1]
        elif event.key == pygame.K_RETURN:
            if self.input_field_active:
                self.input_field_active = False
                process_text_from_input(self.user_new_value)
        else:
            self.input_field_active = True
            self.user_new_value += event.unicode


    def validation_variables(self):
        for key in self.variables.keys():
            for subkey in self.variables[key]["variables"].keys():
                # negative values
                try:
                    value = int(self.variables[key]["variables"][subkey]["value"])
                    if value < 0:
                        self.problems_for_no_go[key] = f"{subkey} has a negative number."
                except Exception as e:
                    pass
                
                # power engine too low for the rocket
                downwards_power = self.variables["rocket-specific-settings"]["variables"]["dry-mass"]["value"]*self.variables["environmental-settings"]["variables"]["gravity"]["value"]
                power_engine = self.variables["engine-settings"]["variables"]["power"]["value"]
                if subkey == "power" and key == "engine-settings" and downwards_power > power_engine:
                    self.problems_for_no_go[key] = f"Thrust power too low for the weight of the rocket: {round(power_engine-downwards_power, 1)}"