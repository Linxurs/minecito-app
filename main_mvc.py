import tkinter as tk
from minecito_launcher.config_manager import ConfigManager
from minecito_launcher.model import LauncherModel
from minecito_launcher.view import LauncherView
from minecito_launcher.controller import LauncherController
def main():
    root = tk.Tk()
    root.title("Minecito Launcher")
    config_manager = ConfigManager("minecito_launcher")
    model = LauncherModel(config_manager)
    view = LauncherView(root)
    controller = LauncherController(model, view)
    controller.start()
if __name__ == "__main__":
    main()
