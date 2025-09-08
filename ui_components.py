"""
Componentes de la interfaz de usuario
"""
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Dict, List, Optional
from config import UI_CONFIG


class UIComponents:
    """Componentes de la interfaz de usuario"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.frame: Optional[ttk.Frame] = None
        
        # Widgets principales
        self.label_username: Optional[ttk.Label] = None
        self.entry_username: Optional[ttk.Combobox] = None
        self.button_generate_random_username: Optional[ttk.Button] = None
        self.label_version: Optional[ttk.Label] = None
        self.combobox_version: Optional[ttk.Combobox] = None
        self.label_uuid: Optional[ttk.Label] = None
        self.entry_uuid: Optional[ttk.Entry] = None
        self.button_launch: Optional[ttk.Button] = None
        self.button_close_game: Optional[ttk.Button] = None
        self.button_advanced_options: Optional[ttk.Button] = None
        self.log_frame: Optional[ttk.Frame] = None
        self.log_text: Optional[tk.Text] = None
        
        # Variables de estado
        self.version_vars: Dict[str, tk.BooleanVar] = {}
    
    def create_main_frame(self) -> None:
        """Crea el frame principal"""
        self.frame = ttk.Frame(self.root)
        self.frame.pack(expand=True, fill="both")
    
    def create_username_widgets(self, on_user_selected: Callable, 
                               on_generate_random: Callable) -> None:
        """Crea los widgets de nombre de usuario"""
        if not self.frame:
            return
        
        self.label_username = ttk.Label(self.frame, text="Nombre de Usuario:")
        self.entry_username = ttk.Combobox(self.frame, width=UI_CONFIG["entry_width"])
        self.entry_username.bind("<<ComboboxSelected>>", on_user_selected)
        
        self.label_username.place(x=5, y=5)
        self.entry_username.place(x=120, y=5)
        
        self.button_generate_random_username = ttk.Button(
            self.frame, text="R", command=on_generate_random, width=3
        )
        self.button_generate_random_username.place(x=270, y=3)
    
    def create_version_widgets(self, version_vars: Dict[str, tk.BooleanVar],
                              on_checkbox_change: Callable) -> None:
        """Crea los widgets de versión"""
        if not self.frame:
            return
        
        self.label_version = ttk.Label(self.frame, text="Versión:")
        self.combobox_version = ttk.Combobox(self.frame, state="readonly", width=20)
        
        self.label_version.place(x=35, y=35)
        self.combobox_version.place(x=120, y=35)
        
        # Crear checkboxes de versión
        checkbox_frame = ttk.Frame(self.frame)
        checkbox_frame.place(x=25, y=65)
        
        self.version_vars = version_vars
        
        checkboxes = [
            ("Snapshot", version_vars["snapshot"]),
            ("Beta", version_vars["beta"]),
            ("Alpha", version_vars["alpha"]),
            ("Especial", version_vars["especial"]),
        ]
        
        for idx, (text, var) in enumerate(checkboxes):
            ttk.Checkbutton(
                checkbox_frame,
                text=text,
                variable=var,
                command=lambda v=var: on_checkbox_change(v),
            ).grid(row=0, column=idx, padx=2)
    
    def create_uuid_widgets(self) -> None:
        """Crea los widgets de UUID"""
        if not self.frame:
            return
        
        self.label_uuid = ttk.Label(self.frame, text="UUID:")
        self.entry_uuid = ttk.Entry(self.frame, width=UI_CONFIG["uuid_entry_width"], state=tk.NORMAL)
        
        self.label_uuid.place(x=40, y=95)
        self.entry_uuid.place(x=120, y=95)
        
        # Ocultar inicialmente
        self.label_uuid.place_forget()
        self.entry_uuid.place_forget()
    
    def create_buttons(self, on_launch: Callable, on_close_game: Callable,
                      on_advanced_options: Callable) -> None:
        """Crea los botones principales"""
        if not self.frame:
            return
        
        self.button_launch = ttk.Button(
            self.frame, text="¡Iniciar Minecraft!", command=on_launch
        )
        self.button_launch.place(x=45, y=96)
        
        self.button_close_game = ttk.Button(
            self.frame,
            text="¡Cerrar Minecraft!",
            state="disabled",
            command=on_close_game,
        )
        self.button_close_game.place(x=155, y=96)
        
        self.button_advanced_options = ttk.Button(
            self.frame,
            text="Opciones Avanzadas",
            command=on_advanced_options,
        )
        self.button_advanced_options.place(x=90, y=130)
    
    def create_log_frame(self, enable_uuid: bool = False) -> None:
        """Crea el frame de log"""
        if not self.frame:
            return
        
        height = UI_CONFIG["log_frame_height_with_uuid"] if enable_uuid else UI_CONFIG["log_frame_height_normal"]
        
        self.log_frame = ttk.Frame(self.frame)
        self.log_frame.place(x=305, y=5, width=520, height=height)
        
        log_height = UI_CONFIG["log_height_with_uuid"] if enable_uuid else UI_CONFIG["log_height_normal"]
        
        self.log_text = tk.Text(
            self.log_frame, 
            height=log_height, 
            width=UI_CONFIG["log_width"], 
            state=tk.DISABLED, 
            wrap="none"
        )
        
        scrollbar = ttk.Scrollbar(self.log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    def show_uuid_widgets(self, uuid_value: str = "") -> None:
        """Muestra los widgets de UUID"""
        if self.label_uuid and self.entry_uuid:
            self.label_uuid.place(x=40, y=95)
            self.entry_uuid.place(x=120, y=95)
            
            if uuid_value:
                self.entry_uuid.delete(0, tk.END)
                self.entry_uuid.insert(0, uuid_value)
            
            self._move_buttons_for_uuid_visible()
    
    def hide_uuid_widgets(self) -> None:
        """Oculta los widgets de UUID"""
        if self.label_uuid and self.entry_uuid:
            self.label_uuid.place_forget()
            self.entry_uuid.place_forget()
            self._restore_buttons_original_position()
    
    def _move_buttons_for_uuid_visible(self) -> None:
        """Mueve los botones cuando UUID es visible"""
        if self.button_launch:
            self.button_launch.place(x=45, y=127)
        if self.button_close_game:
            self.button_close_game.place(x=155, y=127)
        if self.button_advanced_options:
            self.button_advanced_options.place(x=90, y=161)
    
    def _restore_buttons_original_position(self) -> None:
        """Restaura la posición original de los botones"""
        if self.button_launch:
            self.button_launch.place(x=45, y=96)
        if self.button_close_game:
            self.button_close_game.place(x=155, y=96)
        if self.button_advanced_options:
            self.button_advanced_options.place(x=90, y=130)
    
    def update_button_states(self, game_launched: bool) -> None:
        """Actualiza el estado de los botones"""
        if game_launched:
            if self.button_launch:
                self.button_launch["state"] = "disabled"
            if self.button_close_game:
                self.button_close_game["state"] = "normal"
        else:
            if self.button_launch:
                self.button_launch["state"] = "normal"
            if self.button_close_game:
                self.button_close_game["state"] = "disabled"
    
    def set_username_values(self, values: List[str]) -> None:
        """Establece los valores del combobox de usuario"""
        if self.entry_username:
            self.entry_username["values"] = values
    
    def set_version_values(self, values: List[str]) -> None:
        """Establece los valores del combobox de versión"""
        if self.combobox_version:
            self.combobox_version["values"] = values
    
    def get_username(self) -> str:
        """Obtiene el nombre de usuario"""
        return self.entry_username.get().strip() if self.entry_username else ""
    
    def get_version(self) -> str:
        """Obtiene la versión seleccionada"""
        return self.combobox_version.get().strip() if self.combobox_version else ""
    
    def get_uuid(self) -> str:
        """Obtiene el UUID"""
        return self.entry_uuid.get().strip() if self.entry_uuid else ""
    
    def set_username(self, username: str) -> None:
        """Establece el nombre de usuario"""
        if self.entry_username:
            self.entry_username.delete(0, tk.END)
            self.entry_username.insert(0, username)
    
    def set_version(self, version: str) -> None:
        """Establece la versión"""
        if self.combobox_version:
            self.combobox_version.set(version)
    
    def set_uuid(self, uuid_str: str) -> None:
        """Establece el UUID"""
        if self.entry_uuid:
            self.entry_uuid.delete(0, tk.END)
            self.entry_uuid.insert(0, uuid_str)