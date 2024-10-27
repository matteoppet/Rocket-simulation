import pygame
import copy

class Setup:
    def __init__(self, window_size, rocket):
        self.rocket = rocket

        self.color_text = "black"
        self.color_background = "white"

        path_font_regular = "../assets/font/NotoSans-Light.ttf"
        path_font_bold = "../assets/font/NotoSans-SemiBold.ttf"
        
        self.font_title_application = pygame.font.Font(path_font_bold, 35)
        self.font_titles = pygame.font.Font(path_font_bold, 25)
        self.font_texts = pygame.font.Font(path_font_regular, 16)
        self.font_buttons = pygame.font.Font(path_font_regular, 14)
        self.font_buttons_bold = pygame.font.Font(path_font_bold, 14)

        self.pad_table = (6,2)
        self.margin_table = (15,6)
        self.id_count_stages = 1

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

        self.rect_title_application = pygame.Rect(100, 50, 1600, 150)
        self.line_divide_1 = pygame.Rect(100, 250, self.rect_title_application.width, 2)
        self.line_divide_2 = pygame.Rect(100, 660, self.rect_title_application.width, 2)

        self.current_stage_to_show = 1
        self.window_rect_environment = pygame.Rect(150, 300, 300, 300)
        self.environment_settings = {
            "gravity": {"value": 9.81, "rect": ..., "type": 'm/s'},
            "air density": {"value": 1.221, "rect": ..., "type": 'p'},
            "wind velocity": {"value": 0, "rect": ..., "type": 'm/s'}
        }
        
        self.window_rect_rocket = pygame.Rect(550, 300, 300, 300)
        self.rocket_settings = {
            1: {
                "dry mass": {"value": 1000, "rect": ..., "type": "kg"},
                "propellant mass": {"value": 500, "rect": ..., "type": "kg"},
                "cd": {"value": 0.5, "rect": ..., "type": ""}
            }
        }
        
        self.window_rect_engine = pygame.Rect(950, 300, 300, 300)
        self.engine_settings = {
            1: {
                "engine identifier": {"value": "Default", "rect": ..., "type": ""},
                "thrust power": {"value": 30000, "rect": ..., "type": "N"},
                "ISP": {"value": 300, "rect": ..., "type": "s"},
                "thrust vector angle": {"value": 15, "rect": ..., "type": "°"},
                "number engines": {"value": 1, "rect": ..., "type": ""}
            }
        }
        
        self.window_rect_mission = pygame.Rect(1350, 300, 300, 300)
        self.mission_settings = {
            "apogee": {"value": 0, "rect": ..., "type": "m"},
            "target": {"value": "Test", "rect": ..., "type": ""},
            "launch planet": {"value": "Earth", "rect": ..., "type": ""},
            "initial flight angle": {"value": 0, "rect": ..., "type": "°"},
            "launch altitude": {"value": 50, "rect": ..., "type": "m"}
        }
        
        self.rect_second_view = pygame.Rect(150, 700, 900, 250)
        self.rect_lsc_monitor = pygame.Rect(1000, 700, 400, 250)

        self.buttons = {
            "launch status check": {
                "environment": {'rect': '', 'status': True},
                "rocket": {'rect': '', 'status': True},
                "engine": {'rect': '', 'status': True},
                "mission": {'rect': '', 'status': True},
            },
            "launch": ...,
            "reset": ...,
            "add_stage": ...,
            "delete_stage": ...,
            "edit_stage": {}
        }


    def run(self, screen, clock):
        margin = 35
        size_input_value = pygame.Vector2(85, 23)

        screen.fill(self.color_background)

        # title application 
        pygame.draw.rect(screen, "#4379F2", self.rect_title_application)
        pos_text_title = (self.rect_title_application.topleft[0]+45, self.rect_title_application[1]+45)
        self.draw_text("Rocket Simulation", screen, self.color_text, self.font_title_application, pos_text_title)

        pygame.draw.rect(screen, "black", self.line_divide_1)
        pygame.draw.rect(screen, "black", self.line_divide_2)

        # environment settings
        self.draw_text("Environment Settings", screen, self.color_text, self.font_titles, self.window_rect_environment.topleft)
        size_title_environment = self.font_titles.size("Environment Settings")
        pos_variables_environment = pygame.Vector2(self.window_rect_environment.left, self.window_rect_environment.top+size_title_environment[1]+margin)
        pos_value_environment = pygame.Vector2(self.window_rect_environment.right, self.window_rect_environment.top+size_title_environment[1]+margin)
        for variable, dict_value in self.environment_settings.items():
            rect_value = pygame.Rect(pos_value_environment.x-size_input_value.x+4, pos_value_environment.y, size_input_value.x+4, size_input_value.y+4) 
            self.environment_settings[variable]["rect"] = rect_value

            self.draw_variables_inside_each_windoW(screen, rect_value, variable, f"{dict_value['value']} {dict_value['type']}", pos_variables_environment)

            pos_value_environment.y += margin
            pos_variables_environment.y += margin
        rect_go_button_environment = pygame.Rect(pos_variables_environment.x, pos_variables_environment.y+margin, self.window_rect_environment.width, 30)
        self.draw_rect_field(screen, self.color_background, rect_go_button_environment)
        if not self.buttons["launch status check"]["environment"]["rect"]:
            self.buttons["launch status check"]["environment"]["rect"] = rect_go_button_environment
        self.draw_text("GO", screen, self.color_text, self.font_buttons, (rect_go_button_environment.centerx-self.font_buttons.size("GO")[0]/2, rect_go_button_environment.centery-10))

        # rocket settings
        self.draw_text("Rocket Settings", screen, self.color_text, self.font_titles, self.window_rect_rocket.topleft)
        size_title_rocket = self.font_titles.size("Rocket Settings")
        self.draw_text(str(self.current_stage_to_show), screen, self.color_text, self.font_texts, self.window_rect_rocket.topright)
        pos_variables_rocket = pygame.Vector2(self.window_rect_rocket.left, self.window_rect_rocket.top+size_title_rocket[1]+margin)
        pos_value_rocket = pygame.Vector2(self.window_rect_rocket.right, self.window_rect_rocket.top+size_title_rocket[1]+margin)
        for variable, dict_value in self.rocket_settings[self.current_stage_to_show].items():
            rect_value = pygame.Rect(pos_value_rocket.x-size_input_value.x+4, pos_value_rocket.y, size_input_value.x+4, size_input_value.y+4) 
            self.rocket_settings[self.current_stage_to_show][variable]["rect"] = rect_value

            self.draw_variables_inside_each_windoW(screen, rect_value, variable, f"{dict_value['value']} {dict_value['type']}", pos_variables_rocket)

            pos_variables_rocket.y += margin
            pos_value_rocket.y += margin
        rect_go_button_rocket = pygame.Rect(pos_variables_rocket.x, pos_variables_rocket.y+margin, self.window_rect_rocket.width, 30)
        self.draw_rect_field(screen, self.color_background, rect_go_button_rocket)
        if not self.buttons["launch status check"]["rocket"]["rect"]:
            self.buttons["launch status check"]["rocket"]["rect"] = rect_go_button_rocket
        self.draw_text("GO", screen, self.color_text, self.font_buttons, (rect_go_button_rocket.centerx-self.font_buttons.size("GO")[0]/2, rect_go_button_rocket.centery-10))

            
        # engine settings
        self.draw_text("Engine Settings", screen, self.color_text, self.font_titles, self.window_rect_engine.topleft)
        size_title_engine = self.font_titles.size("Rocket Settings")
        self.draw_text(str(self.current_stage_to_show), screen, self.color_text, self.font_texts, self.window_rect_engine.topright)
        pos_variables_engine = pygame.Vector2(self.window_rect_engine.left, self.window_rect_engine.top+size_title_engine[1]+margin)
        pos_value_engine = pygame.Vector2(self.window_rect_engine.right, self.window_rect_engine.top+size_title_engine[1]+margin)
        for variable, dict_value in self.engine_settings[self.current_stage_to_show].items():
            rect_value = pygame.Rect(pos_value_engine.x-size_input_value.x+4, pos_value_engine.y, size_input_value.x+4, size_input_value.y+4) 
            self.engine_settings[self.current_stage_to_show][variable]["rect"] = rect_value

            self.draw_variables_inside_each_windoW(screen, rect_value, variable, f"{dict_value['value']} {dict_value['type']}", pos_variables_engine)

            pos_variables_engine.y += margin
            pos_value_engine.y += margin
        rect_go_button_engine = pygame.Rect(pos_variables_engine.x, pos_variables_engine.y+margin, self.window_rect_engine.width, 30)
        self.draw_rect_field(screen, self.color_background, rect_go_button_engine)
        if not self.buttons["launch status check"]["engine"]["rect"]:
            self.buttons["launch status check"]["engine"]["rect"] = rect_go_button_engine
        self.draw_text("GO", screen, self.color_text, self.font_buttons, (rect_go_button_engine.centerx-self.font_buttons.size("GO")[0]/2, rect_go_button_engine.centery-10))


        # mission settings
        self.draw_text("Mission Settings", screen, self.color_text, self.font_titles, self.window_rect_mission.topleft)
        size_title_mission = self.font_titles.size("Rocket Settings")
        pos_variables_mission = pygame.Vector2(self.window_rect_mission.left, self.window_rect_mission.top+size_title_mission[1]+margin)
        pos_value_mission = pygame.Vector2(self.window_rect_mission.right, self.window_rect_mission.top+size_title_mission[1]+margin)
        for variable, dict_value in self.mission_settings.items():
            rect_value = pygame.Rect(pos_value_mission.x-size_input_value.x+4, pos_value_mission.y, size_input_value.x+4, size_input_value.y+4) 
            self.mission_settings[variable]["rect"] = rect_value

            self.draw_variables_inside_each_windoW(screen, rect_value, variable, f"{dict_value['value']} {dict_value['type']}", pos_variables_mission)

            pos_variables_mission.y += margin
            pos_value_mission.y += margin
        rect_go_button_mission = pygame.Rect(pos_variables_mission.x, pos_variables_mission.y+margin, self.window_rect_mission.width, 30)
        self.draw_rect_field(screen, self.color_background, rect_go_button_mission)
        if not self.buttons["launch status check"]["mission"]["rect"]:
            self.buttons["launch status check"]["mission"]["rect"] = rect_go_button_mission
        self.draw_text("GO", screen, self.color_text, self.font_buttons, (rect_go_button_mission.centerx-self.font_buttons.size("GO")[0]/2, rect_go_button_mission.centery-10))
        
        # second view
        self.draw_table_bottom_window(screen)

        # launch status check
        self.draw_launch_status_check(screen)

        # draw rect input field bottom
        self.draw_rect_field(screen, self.color_background, self.rect_input_user_field)
        self.draw_text(self.user_new_value, screen, self.color_text, self.font_texts, (self.rect_input_user_field.left+3, self.rect_input_user_field.top+2))

        # launch button
        size_text_launch = self.font_buttons.size("Launch")
        rect_launch_button = pygame.Rect(1500,800, size_text_launch[0]+self.margin_table[0], size_text_launch[1]+self.margin_table[1])
        self.buttons["launch"] = rect_launch_button
        self.draw_rect_field(screen, "green", rect_launch_button)
        self.draw_text("Launch", screen, self.color_text, self.font_buttons, (rect_launch_button.left+self.pad_table[0], rect_launch_button.top+self.pad_table[1]))

        # FPS
        self.draw_text(round(clock.get_fps(),1), screen, "black", self.font_texts, (10, 10))


    def draw_launch_status_check(self, screen):
        self.draw_text("Launch status check", screen, self.color_text, self.font_titles, self.rect_lsc_monitor.topleft)

        size_text_name_monitor = self.font_buttons_bold.size("environment")
        size_text_status = self.font_buttons.size("NO-GO")
        start_pos = pygame.Vector2(self.rect_lsc_monitor.left, self.rect_lsc_monitor.top+self.font_titles.size("Launch status check")[1]+35)
        for monitor in self.buttons["launch status check"].keys():
            rect_name_monitor = pygame.Rect(start_pos, (size_text_name_monitor[0]+self.margin_table[0], size_text_name_monitor[1]+self.margin_table[1]))
            self.draw_rect_field(screen, self.color_background, rect_name_monitor)
            self.draw_text(monitor, screen, self.color_text, self.font_buttons_bold, (rect_name_monitor.left+self.pad_table[0], rect_name_monitor.top+self.pad_table[1]))

            status = self.buttons['launch status check'][monitor]['status']
            rect_status = pygame.Rect((start_pos.x+rect_name_monitor.width, start_pos.y), (size_text_status[0]+self.margin_table[0], size_text_status[1]+self.margin_table[1]))
            if status:
                self.draw_rect_field(screen, "green", rect_status)
                self.draw_text("GO", screen, self.color_text, self.font_buttons, (rect_status.left+self.pad_table[0], rect_status.top+self.pad_table[1]))
            else:
                self.draw_rect_field(screen, "#ff3d3d", rect_status)
                self.draw_text("NO-GO", screen, self.color_text, self.font_buttons, (rect_status.left+self.pad_table[0], rect_status.top+self.pad_table[1]))

            start_pos.y += rect_name_monitor.height


    def draw_table_bottom_window(self, screen):
        table_variables = {
            "delta-v": 0,
            "cd": 0,
            "engine identifier": self.engine_settings,
            "propellant mass": self.rocket_settings,
            "dry mass": self.rocket_settings,
            "total mass": 0
        }

        # draw first cell 
        size_text_first_cell = self.font_buttons_bold.size("Stage")
        rect_first_cell = pygame.Rect(self.rect_second_view.left+10, self.rect_second_view.top+10, size_text_first_cell[0]+self.margin_table[0], size_text_first_cell[1]+self.margin_table[1])
        self.draw_rect_field(screen, self.color_background, rect_first_cell)
        self.draw_text("Stage", screen, self.color_text, self.font_buttons_bold, (rect_first_cell.left+self.pad_table[0], rect_first_cell.top+self.pad_table[1]))

        # draw horizontal title cells
        start_pos_horizontal_title = pygame.Vector2(rect_first_cell.right+1, rect_first_cell.top)
        for name_var in table_variables:
            size_text = self.font_buttons_bold.size(name_var)
            rect_text = pygame.Rect(start_pos_horizontal_title.x, start_pos_horizontal_title.y, size_text[0]+self.margin_table[0], size_text[1]+self.margin_table[1])
            self.draw_rect_field(screen, self.color_background, rect_text)
            self.draw_text(name_var, screen, self.color_text, self.font_buttons_bold, (rect_text.left+self.pad_table[0], rect_text.top+self.pad_table[1]))

            start_pos_horizontal_title.x += rect_text.width+1

        # draw vertical cells and each value 
        start_pos_vertical_stage_num = pygame.Vector2(rect_first_cell.left, rect_first_cell.bottom+1)
        start_pos_internal_values = pygame.Vector2(rect_first_cell.right+1, rect_first_cell.bottom+1)
        for number_stage in range(1, self.id_count_stages+1):
            rect_num_stage = pygame.Rect(start_pos_vertical_stage_num, rect_first_cell.size)
            if number_stage == self.current_stage_to_show: color = self.color_background
            else: color = "#dddddd"

            self.draw_rect_field(screen, color, rect_num_stage)
            self.draw_text(str(number_stage), screen, self.color_text, self.font_buttons_bold, rect_num_stage.topleft)
            self.buttons["edit_stage"][number_stage] = rect_num_stage

            for variable, dictionary in table_variables.items():
                if isinstance(dictionary, dict): value = self.get_value_based_on_the_stage(dictionary, variable, number_stage)
                else: 
                    if variable == "total mass":
                        value = self.get_value_based_on_the_stage(self.rocket_settings, "dry mass", number_stage) + self.get_value_based_on_the_stage(self.rocket_settings, "propellant mass", number_stage)
                    else:
                        value = dictionary

                size_rect = self.font_buttons_bold.size(variable)
                rect_value = pygame.Rect(start_pos_internal_values, (size_rect[0]+self.margin_table[0], size_rect[1]+self.margin_table[1]))
                self.draw_rect_field(screen, color, rect_value)
                self.draw_text(value, screen, self.color_text, self.font_buttons, start_pos_internal_values)

                start_pos_internal_values.x += rect_value.width+1
        
            start_pos_vertical_stage_num.y += rect_num_stage.height+1
            start_pos_internal_values.y += rect_num_stage.height+1
            start_pos_internal_values.x = rect_first_cell.right+1

        # buttons
        button_add_new_stage = pygame.Rect(start_pos_vertical_stage_num, rect_first_cell.size)
        self.buttons["add_stage"] = button_add_new_stage
        self.draw_rect_field(screen, "green", button_add_new_stage)

        button_delete_stage = pygame.Rect(button_add_new_stage.right+1, button_add_new_stage.top, button_add_new_stage.width, button_add_new_stage.height)
        self.buttons["delete_stage"] = button_delete_stage
        self.draw_rect_field(screen, "red", button_delete_stage)


    def get_value_based_on_the_stage(self, dict, variable, current_stage):
        return dict[current_stage][variable]["value"]


    def draw_rect_field(self, screen, color, rect_hover):
        rect_background = pygame.Rect(rect_hover.topleft[0]-1, rect_hover.topleft[1]-1, rect_hover.width+2, rect_hover.height+2)
        if self.color_background == "black":
            color_background_rect = "white"
        else:
            color_background_rect = "black"

        pygame.draw.rect(screen, color_background_rect, rect_background)
        pygame.draw.rect(screen, color, rect_hover)


    def draw_variables_inside_each_windoW(self, screen, rect_value, text_variable, text_value, pos_variables):
        self.draw_text(text_variable, screen, self.color_text, self.font_texts, pos_variables)
        self.draw_rect_field(screen, self.color_background, rect_value)
        self.draw_text(text_value, screen, self.color_text, self.font_buttons, (rect_value.left+3, rect_value.top+3))


    def draw_text(self, text, screen, color, font, pos):
        text_render = font.render(str(text), True, color)
        screen.blit(text_render, pos)


    def check_event_edit_variable(self, mouse_pos):
        def set_value(name_monitor, dict_monitor):
            for key, dict_value in dict_monitor.items():
                if dict_value["rect"].collidepoint(mouse_pos):
                    self.input_field_values["window"] = name_monitor
                    self.input_field_values["name_var"] = key 
                    self.input_field_values["value"] = dict_value["value"]
                    break

            self.user_new_value = f"{self.input_field_values['name_var']}: {self.input_field_values['value']}"

        if self.window_rect_environment.collidepoint(mouse_pos):
            set_value("environment", self.environment_settings)

        elif self.window_rect_rocket.collidepoint(mouse_pos):
            set_value("rocket", self.rocket_settings[self.current_stage_to_show])

        elif self.window_rect_engine.collidepoint(mouse_pos):
            set_value("engine", self.engine_settings[self.current_stage_to_show])

        elif self.window_rect_mission.collidepoint(mouse_pos):
            set_value("mission", self.mission_settings)


    def edit_variable(self, event):
        def process_text_from_input(text):
            text, value = text.split(": ")
            try:
                value = float(value)
            except ValueError:
                value = str(value)

            if self.input_field_values["window"] == "environment":
                self.environment_settings[self.input_field_values["name_var"]]["value"] = value
                self.buttons["launch status check"]["environment"]["status"] = False
            elif self.input_field_values["window"] == "rocket":
                self.rocket_settings[self.current_stage_to_show][self.input_field_values["name_var"]]["value"] = value
                self.buttons["launch status check"]["rocket"]["status"] = False
            elif self.input_field_values["window"] == "engine":
                self.engine_settings[self.current_stage_to_show][self.input_field_values["name_var"]]["value"] = value
                self.buttons["launch status check"]["engine"]["status"] = False
            elif self.input_field_values["window"] == "mission":
                self.mission_settings[self.input_field_values["name_var"]]["value"] = value
                self.buttons["launch status check"]["mission"]["status"] = False
            
            self.input_field_values = self.input_field_values.fromkeys(self.input_field_values, None)
            self.user_new_value = ''
 

        if event.key == pygame.K_BACKSPACE:
            try:
                if len(self.user_new_value) > len(self.input_field_values["name_var"])+2:
                    self.user_new_value = self.user_new_value[:-1]
            except TypeError: pass
        elif event.key == pygame.K_RETURN:
            if self.input_field_active:
                self.input_field_active = False
                process_text_from_input(self.user_new_value)
        else:
            self.input_field_active = True
            self.user_new_value += event.unicode


    def validation_monitor(self, monitor):
        def check_value_below_0(value):
            if value < 0:
                return True
            return False
        
        problem = False
            
        if monitor == "environment":
            for variable in self.environment_settings.keys():
                problem = check_value_below_0(self.environment_settings[variable]["value"])
                if problem: break

            if not problem: self.buttons['launch status check'][monitor]['status'] = True

        elif monitor == "rocket":
            for variable in self.rocket_settings[self.current_stage_to_show].keys():
                value = self.rocket_settings[self.current_stage_to_show][variable]["value"]

                if check_value_below_0(value) or value == 0: problem = True
                if problem: break

            if not problem: self.buttons['launch status check'][monitor]['status'] = True

        elif monitor == "engine": 
            for variable in self.engine_settings[self.current_stage_to_show].keys():
                value = self.engine_settings[self.current_stage_to_show][variable]["value"]

                if variable not in ["thrust vector angle", "engine identifier"]: 
                    problem = check_value_below_0(value)
                    if problem: break

                if variable == "thrust power":
                    current_mass = self.rocket_settings[self.current_stage_to_show]["dry mass"]["value"] + self.rocket_settings[self.current_stage_to_show]["propellant mass"]["value"]
                    gravity = self.environment_settings["gravity"]["value"]
                    vertical_weight = current_mass * gravity

                    if float(vertical_weight) > float(value):
                        problem = True
                        break

            if not problem: self.buttons['launch status check'][monitor]['status'] = True
            

        elif monitor == "mission":
            for variable in self.mission_settings.keys():
                if variable in ["launch altitude", "apogee"]:
                    problem = check_value_below_0(self.mission_settings[variable]["value"])
                    if problem:
                        break

            if not problem: self.buttons['launch status check'][monitor]['status'] = True