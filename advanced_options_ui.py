"""
Componentes de la interfaz de usuario para las opciones avanzadas
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Callable, Optional, Dict, Any
import os

from config import ADVANCED_OPTIONS_WINDOW_CONFIG, DEFAULT_JVM_ARGS

class AdvancedOptionsUI:
    """Clase para gestionar la interfaz de usuario de las opciones avanzadas."""

    def __init__(self, root: tk.Tk,
                 advanced_options_close_launcher_var: tk.BooleanVar,
                 advanced_options_memory_var: tk.StringVar,
                 advanced_options_directory_var: tk.StringVar,
                 java_executable_var: tk.StringVar,
                 hide_log_var: tk.BooleanVar,
                 enable_uuid_var: tk.BooleanVar,
                 resource_path_func: Callable[[str], str],
                 on_apply_callback: Callable[[], None],
                 on_cancel_callback: Callable[[], None],
                 on_select_java_executable: Callable[[], None],
                 on_select_minecraft_directory: Callable[[], None]):
        
        self.root = root
        self.advanced_options_window: Optional[tk.Toplevel] = None
        
        self.advanced_options_close_launcher_var = advanced_options_close_launcher_var
        self.advanced_options_memory_var = advanced_options_memory_var
        self.advanced_options_directory_var = advanced_options_directory_var
        self.java_executable_var = java_executable_var
        self.hide_log_var = hide_log_var
        self.enable_uuid_var = enable_uuid_var

        self.resource_path = resource_path_func
        self.on_apply_callback = on_apply_callback
        self.on_cancel_callback = on_cancel_callback
        self.on_select_java_executable = on_select_java_executable
        self.on_select_minecraft_directory = on_select_minecraft_directory

        self.java_executable_entry: Optional[ttk.Entry] = None

    def create_window(self) -> None:
        """Crea y muestra la ventana de opciones avanzadas."""
        if self.advanced_options_window and self.advanced_options_window.winfo_exists():
            self.advanced_options_window.destroy()

        window_width = ADVANCED_OPTIONS_WINDOW_CONFIG["width"]
        window_height = ADVANCED_OPTIONS_WINDOW_CONFIG["height"]
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)

        self.advanced_options_window = tk.Toplevel(self.root)
        self.advanced_options_window.withdraw()
        self.advanced_options_window.title(ADVANCED_OPTIONS_WINDOW_CONFIG["title"])
        self.advanced_options_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.advanced_options_window.resizable(
            ADVANCED_OPTIONS_WINDOW_CONFIG["resizable"],
            ADVANCED_OPTIONS_WINDOW_CONFIG["resizable"]
        )
        try:
            self.advanced_options_window.iconbitmap(self.resource_path(ADVANCED_OPTIONS_WINDOW_CONFIG["icon_path"]))
        except:
            pass # Ignorar si no se encuentra el icono
        
        self.advanced_options_window.transient(self.root)
        self.advanced_options_window.grab_set()
        self.advanced_options_window.protocol("WM_DELETE_WINDOW", self.on_cancel_callback)

        self._create_widgets()
        self.advanced_options_window.deiconify()

    def _create_widgets(self) -> None:
        """Crea los widgets dentro de la ventana de opciones avanzadas."""
        if self.advanced_options_window:
            main_frame = ttk.Frame(self.advanced_options_window)
            main_frame.place(x=5, y=2)
            
            self._create_jvm_args_widget(main_frame)
            self._create_java_executable_widget(main_frame)
            self._create_minecraft_directory_widget(main_frame)
            self._create_close_launcher_widget(main_frame)
            self._create_hide_log_widget(main_frame)
            self._create_enable_uuid_widget(main_frame)
            self._create_buttons_frame(main_frame)

    def _create_jvm_args_widget(self, main_frame: ttk.Frame) -> None:
        """Crea el widget para los argumentos JVM."""
        ttk.Label(main_frame, text="Argumentos JVM:", foreground="dark red").place(x=0, y=0)
        memory_entry = ttk.Entry(main_frame, textvariable=self.advanced_options_memory_var, width=54)
        memory_entry.place(x=0, y=20)
        if not self.advanced_options_memory_var.get():
            self.advanced_options_memory_var.set(" ".join(DEFAULT_JVM_ARGS))

    def _create_java_executable_widget(self, main_frame: ttk.Frame) -> None:
        """Crea el widget para el ejecutable de Java."""
        self.java_executable_entry = ttk.Entry(main_frame, textvariable=self.java_executable_var, width=41)
        ttk.Label(main_frame, text="Ejecutable de Java:", foreground="dark red").place(x=0, y=42)
        if self.java_executable_entry:
            self.java_executable_entry.place(x=0, y=62)
            self.java_executable_entry.configure(state="readonly")
        
        button_frame_select_java = ttk.Frame(main_frame)
        button_frame_select_java.place(x=255, y=60)
        ttk.Button(button_frame_select_java, text="Seleccionar", command=self.on_select_java_executable).grid(row=0, column=0)

    def _create_minecraft_directory_widget(self, main_frame: ttk.Frame) -> None:
        """Crea el widget para el directorio de Minecraft."""
        ttk.Label(main_frame, text="Directorio de Minecraft:", foreground="dark red").place(x=0, y=84)
        directory_entry = ttk.Entry(main_frame, textvariable=self.advanced_options_directory_var, state="readonly", width=41)
        directory_entry.place(x=0, y=104)
        
        button_frame_select = ttk.Frame(main_frame)
        button_frame_select.place(x=255, y=102)
        ttk.Button(button_frame_select, text="Seleccionar", command=self.on_select_minecraft_directory).grid(row=0, column=0)

    def _create_close_launcher_widget(self, main_frame: ttk.Frame) -> None:
        """Crea el widget para cerrar el launcher al iniciar el juego."""
        close_launcher_frame = ttk.Frame(main_frame)
        close_launcher_frame.place(x=0, y=128)
        ttk.Checkbutton(close_launcher_frame, text="Cerrar Minecito cuando inicie Minecraft.", variable=self.advanced_options_close_launcher_var).grid(row=0, column=0)

    def _create_hide_log_widget(self, main_frame: ttk.Frame) -> None:
        """Crea el widget para ocultar/mostrar el log."""
        ttk.Checkbutton(main_frame, text="Habilitar el registro.", variable=self.hide_log_var).place(x=0, y=148)

    def _create_enable_uuid_widget(self, main_frame: ttk.Frame) -> None:
        """Crea el widget para habilitar/deshabilitar UUID."""
        ttk.Checkbutton(main_frame, text="Habilitar UUID.", variable=self.enable_uuid_var).place(x=0, y=168)

    def _create_buttons_frame(self, main_frame: ttk.Frame) -> None:
        """Crea el frame con los botones Aplicar y Cancelar."""
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=0, column=0, pady=80, columnspan=2, sticky="S")
        
        apply_button = ttk.Button(main_frame, text="Aplicar", command=self.on_apply_callback)
        apply_button.grid(row=1, column=0, padx=(85, 0), pady=30, sticky="W")
        
        cancel_button = ttk.Button(main_frame, text="Cancelar", command=self.on_cancel_callback)
        cancel_button.grid(row=1, column=1, padx=(10, 85), pady=30, sticky="E")

    def destroy_window(self) -> None:
        """Destruye la ventana de opciones avanzadas si existe."""
        if self.advanced_options_window and self.advanced_options_window.winfo_exists():
            self.advanced_options_window.destroy()
            self.advanced_options_window = None
