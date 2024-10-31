from tkinter import *
import tkinter as ttk

from game.main import Simulation


class Setup_Window(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.font = "TkDefaultFont"
        self.master = master

        self.environment_settings = {
            "gravity": 9.81,
            "air density": 1.221,
            "wind velocity": 0,
        }
        self.rocket_settings = {
            1: {
                "dry mass": 22200,
                "propellant mass": 395700,
                "cd": 0.5,
            }
        }
        self.motor_settings = {
            1: {
                "engine identifier": "Default",
                "thrust power": 7607000,
                "isp": 282,
                "thrust vector angle": 15,
                "number engines": 1
            }
        }
        self.mission_settings = {
            "apogee": 0,
            "target": "moon",
            "launch planet": "earth",
            "initial flight angle": 0,
            "launch altitude": 0,
        }

        self.run()

    
    def run(self):
        frame = ttk.Frame(self.master)
        frame.grid()

        self.init_row = 0
        self.init_col = 0

        # environment 
        ttk.Label(master=frame, text="Environment Settings", font=(self.font, 16)).grid(row=self.init_row, column=self.init_col, sticky="w", pady=15, padx=10)
        self.init_row += 1
        self.draw_variables(self.environment_settings, frame)
        
        # rocket
        ttk.Label(master=frame, text="Rocket Settings", font=(self.font, 16)).grid(row=self.init_row, column=self.init_col, sticky="w", pady=15, padx=10)
        self.init_row += 1
        self.draw_second_variables(self.rocket_settings, frame)

        # motor
        ttk.Label(master=frame, text="Motor Settings", font=(self.font, 16)).grid(row=self.init_row, column=self.init_col, sticky="w", pady=15, padx=10)
        self.init_row += 1
        self.draw_second_variables(self.motor_settings, frame)

        # mission
        ttk.Label(master=frame, text="Mission Settings", font=(self.font, 16)).grid(row=self.init_row, column=self.init_col, sticky="w", pady=15, padx=10)
        self.init_row += 1
        self.draw_variables(self.mission_settings, frame)

        # launch button
        launch_button = ttk.Button(master=frame, text="launch", background="#76B355", command=lambda: self.run_simulation())
        launch_button.grid(row=0, column=2, sticky="n")
    

    def run_simulation(self):
        Simulation(self.rocket_settings, self.motor_settings, self.environment_settings, self.mission_settings)


    def modify_values(self, entry, dictionary_variables):
        name_variable = entry._name
        new_value = entry.get()
        dictionary_variables[name_variable] = new_value



    def draw_variables(self, dictionary_variables, frame):
        for key, value in dictionary_variables.items():
            ttk.Label(master=frame, text=key, font=(self.font, 11)).grid(column=self.init_col, row=self.init_row, sticky="w", pady=2, padx=10)

            entry = ttk.Entry(master=frame, width=20, name=key)
            entry.grid(column=self.init_col+1, row=self.init_row, pady=2)
            entry.insert(0, value)
            entry.bind("<Return>", lambda event, e=entry: self.modify_values(e, dictionary_variables))

            self.init_row += 1


    def draw_second_variables(self, dictionary_variables, frame):
        for stage in dictionary_variables.keys():
            for key, value in dictionary_variables[stage].items():
                ttk.Label(master=frame, text=key, font=(self.font, 11)).grid(column=self.init_col, row=self.init_row, sticky="w", pady=2, padx=10)

                entry = ttk.Entry(master=frame, width=20, name=key)
                entry.grid(column=self.init_col+1, row=self.init_row, pady=2)
                entry.insert(0, value)
                entry.bind("<Return>", lambda event, e=entry: self.modify_values(e, dictionary_variables))

                self.init_row += 1