from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import csv
import json

from game.main import Simulation

class Setup_Window(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        self.font = "TkDefaultFont"
        self.current_stage = 1

        self.path_json_config = "../assets/rocket_files/rocket_config.json"
        with open(self.path_json_config, "r") as file:
            self.rocket_config = json.load(file)
        file.close()

        self.launch_pad_settings = {  ##### TEMPORARY
            "elevation": 0,
            "temperature": 15,
            "air density": 1.221,
            "wind speed": 0,
            "wind angle": 0,
            "launch angle": 0,
            "gravity": 9.81,
        }
    
    def run(self):
        self.create_notebook()

        self.load_frame_setup(self.setup_frame)
        self.load_frame_flight_simulation(self.flight_frame)

        self.master.mainloop()

    def create_notebook(self):
        notebook = ttk.Notebook(self.master)
        notebook.grid()

        self.setup_frame = ttk.Frame(notebook)
        self.setup_frame.grid()

        self.flight_frame = ttk.Frame(notebook)
        self.flight_frame.grid()

        notebook.add(self.setup_frame, text="Setup")
        notebook.add(self.flight_frame, text="Flight Simulation")

    def load_frame_setup(self, frame):
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
                entry.bind("<Return>", lambda event, e=entry: self.modify_values(e))

                init_row += 1

    def load_frame_flight_simulation(self, frame):
        def run_simulation():
            sim = Simulation()
            sim.restart(self.launch_pad_settings)

        launch_button = Button(master=frame, text="launch", background="#76B355", command=lambda: run_simulation())
        launch_button.grid(row=0, column=0)

    def modify_values(self, e):
        name_component, name_attrib = e._name.split(",")
        new_value = float(e.get())
        
        self.rocket_config["parts"][str(self.current_stage)]["parts"][name_component][name_attrib] = new_value

        with open(self.path_json_config, "w") as file:
            json.dump(self.rocket_config, file, indent=4)