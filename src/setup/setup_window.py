from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import csv
import json

from game.game_window import Simulation

class Setup_Window(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        self.font = "TkDefaultFont"
        self.current_stage = 1

        self.path_json_rocket_config = "config/rocket_config.json"
        with open(self.path_json_rocket_config, "r") as file:
            self.rocket_config = json.load(file)
        file.close()

        self.path_json_environment_config = "config/environment_config.json"
        with open(self.path_json_environment_config, "r") as file:
            self.environment_config = json.load(file)
        file.close()

        self.launch_pad_settings = {
            "elevation": 0,
            "launch angle": 0,
        }
    
    def run(self):
        self.create_notebook()

        self.load_rocket_setup_frame(self.setup_rocket_frame)
        self.load_environment_setup_frame(self.setup_environment_frame)
        self.load_frame_flight_simulation(self.flight_frame)

        self.master.mainloop()

    def create_notebook(self):
        notebook = ttk.Notebook(self.master)
        notebook.grid()

        self.setup_rocket_frame = ttk.Frame(notebook)
        self.setup_rocket_frame.grid()

        self.setup_environment_frame = ttk.Frame(notebook)
        self.setup_environment_frame.grid()

        self.flight_frame = ttk.Frame(notebook)
        self.flight_frame.grid()

        notebook.add(self.setup_rocket_frame, text="Rocket")
        notebook.add(self.setup_environment_frame, text="Environment")
        notebook.add(self.flight_frame, text="Simulation")

    def load_rocket_setup_frame(self, frame):
        init_row = 0
        init_col = 0

        ttk.Label(master=frame, text="Rocket Settings", font=(self.font, 16)).grid(row=init_row, column=init_col, sticky="w", pady=15, padx=10)
        init_row += 1
        for component, attrib in self.rocket_config["parts"][str(self.current_stage)]["parts"].items():
            ttk.Label(master=frame, text=f"{component}:", font=(self.font, 11)).grid(row=init_row, column=init_col, sticky="w", pady=2, padx=10)
            init_row += 1

            for each_attrib, value in attrib.items():
                ttk.Label(master=frame, text=f"{each_attrib}:", font=(self.font, 11)).grid(row=init_row, column=init_col+1, sticky="w", pady=2, padx=10)

                entry = ttk.Entry(master=frame, width=20, name=f"{component},{each_attrib}")
                entry.grid(row=init_row, column=init_col+2, pady=2)
                entry.insert(0, value)
                entry.bind("<Return>", lambda event, e=entry: self.modify_rocket_values(e))

                init_row += 1

    def load_environment_setup_frame(self, frame):
        init_row = 0
        init_col = 0

        ttk.Label(master=frame, text="Environment settings", font=(self.font, 16)).grid(row=init_row, column=init_col, sticky="w", pady=15, padx=10)
        init_row += 1
        for planet, settings in self.environment_config.items():
            for setting, value in settings.items():
                ttk.Label(master=frame, text=f"{setting}:", font=(self.font, 11)).grid(row=init_row, column=init_col, sticky="w", pady=2, padx=10)

                entry = ttk.Entry(master=frame, width=20, name=f"{planet},{setting}")
                entry.grid(row=init_row, column=init_col+1, pady=2)
                entry.insert(0, value)
                entry.bind("<Return>", lambda event, e=entry: self.modify_environment_values(e))

                init_row += 1

    def load_frame_flight_simulation(self, frame):
        def run_simulation():
            sim = Simulation()
            sim.restart(self.launch_pad_settings)

        launch_button = Button(master=frame, text="launch", background="#76B355", command=lambda: run_simulation())
        launch_button.grid(row=0, column=0)

    def modify_rocket_values(self, e):
        name_component, name_attrib = e._name.split(",")
        new_value = float(e.get())
        
        self.rocket_config["parts"][str(self.current_stage)]["parts"][name_component][name_attrib] = new_value

        with open(self.path_json_rocket_config, "w") as file:
            json.dump(self.rocket_config, file, indent=4)

    def modify_environment_values(self, e):
        name_planet, name_setting = e._name.split(",")
        new_value = float(e.get())

        self.environment_config[name_planet][name_setting] = new_value

        with open(self.path_json_environment_config, "w") as file:
                json.dump(self.environment_config, file, indent=4)