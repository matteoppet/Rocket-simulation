if __name__ == "__main__":
    from setup.main import Setup_Window
    from tkinter import Tk

    root = Tk(screenName="Setup Window")
    root.geometry("600x880")
    root.title("Setup window")
    window = Setup_Window(root)
    window.run()
    