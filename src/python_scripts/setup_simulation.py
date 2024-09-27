import pygame 

class Setup:
    def __init__(self, window_size):

        path_font = "assets/font/Roboto-Regular.ttf"
        self.font_title = pygame.font.Font(path_font, 25)
        self.font_text = pygame.font.Font(path_font, 16)

        self.variables = {
            "environment": {
                "gravity": 9.81,
                "air-density-sea-level": 1.225,
                "wind": 0,
            },
            "rocket": {
                "initial-mass": 10.0,
                "fuel-capacity": 0,
                "cd": 0.7,
            },
            "engine": {
                "power": 120,
                "name": "test_1",
                "isp": 300, # (specific impulse) solid engine = 200-300 seconds, liquid engine = 300-450 change un get_mass_flow_rate
                "thrust_vectoring": 0, # maximum angle by which the negine can gimbal
                "num_engines": 0,
            },
            "mission-parameters": {
                "angle": 0,
                "position": 0,
                "altitude": 0,
                "planet": "earth",
            },
        }

        self.user_text = ''
        self.active = False

        width_rect = window_size[0]
        height_rect = 30
        self.rect_input_text = pygame.Rect(0, window_size[1]-height_rect, width_rect, height_rect)

        self.environment_rect_window = pygame.Rect(100, 100, 400, 200)
        self.rocket_rect_window = pygame.Rect(700, 100, 400, 200)
        self.engine_rect_window = pygame.Rect(1300, 100, 400, 200)
        self.mission_parameters_rect_window = pygame.Rect(100, 600, 300, 200)


    def run(self, screen):
        for key, value in self.variables.items():

            if key == "environment":
                pygame.draw.rect(screen, "gray", self.environment_rect_window)
                self.draw_text(key.title(), "black", self.font_title, self.environment_rect_window.topleft, screen)
                start_pos_text_x = self.environment_rect_window.topleft[0]
                start_pos_text_y = self.environment_rect_window.topleft[1]+20
            elif key == "rocket":
                pygame.draw.rect(screen, "gray", self.rocket_rect_window)
                self.draw_text(key.title(), "black", self.font_title, self.rocket_rect_window.topleft, screen)
                start_pos_text_x = self.rocket_rect_window[0]
                start_pos_text_y = self.rocket_rect_window[1]+20
            elif key == "engine":
                pygame.draw.rect(screen, "gray", self.engine_rect_window)
                self.draw_text(key.title(), "black", self.font_title, self.engine_rect_window.topleft, screen)
                start_pos_text_x = self.engine_rect_window[0]
                start_pos_text_y = self.engine_rect_window[1]+20
            elif key == "mission-parameters":
                pygame.draw.rect(screen, "gray", self.mission_parameters_rect_window)
                self.draw_text(key.title(), "black", self.font_title, self.mission_parameters_rect_window.topleft, screen)
                start_pos_text_x = self.mission_parameters_rect_window[0]
                start_pos_text_y = self.mission_parameters_rect_window[1]+20


            for subkey, subvalue in value.items():
                start_pos_text_y += 20
                self.draw_text(f"{subkey.capitalize()}", "black", self.font_text, (start_pos_text_x, start_pos_text_y), screen)
                self.draw_value(f" {subvalue}", "black", self.font_text, (start_pos_text_x+200, start_pos_text_y), screen)

        pygame.draw.rect(screen, "gray", self.rect_input_text)
        self.draw_text(f"> {self.user_text}", "black", self.font_text, (self.rect_input_text.x, self.rect_input_text.y+5), screen)

        buttons_rect = self.buttons()
        for button_rect in buttons_rect:
            pygame.draw.rect(screen, "gray", button_rect)

    def draw_text(self, text, color, font, pos, screen):
        img = font.render(text, True, color)
        screen.blit(img, pos)


    def draw_value(self, text, color, font, pos, screen):
        background_rect = pygame.Rect(pos[0], pos[1], 60, 18)
        pygame.draw.rect(screen, "grey", background_rect)
        img = font.render(text, True, color)
        screen.blit(img, pos)


    def user_input_text(self, event):
        if self.active:
            if event.key == pygame.K_BACKSPACE:
                self.user_text = self.user_text[:-1]
            elif event.key == pygame.K_RETURN:
                self.process_text_from_input(self.user_text)
            else:
                self.user_text += event.unicode

    
    def process_text_from_input(self, text):
        try:
            section, variable, value = text.split(" ")
            section = str(section)
            variable = str(variable)
            value = float(value)

            self.variables[section][variable] = value
            print("Value changed")
            self.user_text = ''
        except ValueError:
            print("ERROR values") 

    
    def buttons(self):
        reset_button_rect = pygame.Rect(1600, self.mission_parameters_rect_window.bottomright[1], 30, 30)
        launch_button_rect = pygame.Rect(1640, self.mission_parameters_rect_window.bottomright[1], 30, 30)

        return [reset_button_rect, launch_button_rect]

# continue update graphic in setup
# then system everything in simulation