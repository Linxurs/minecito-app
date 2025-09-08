"""
Launcher de Minecraft - Aplicación principal refactorizada
"""
import os
import sys
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Any, Dict, List, Optional

# Importar módulos refactorizados
from config import (
    DEFAULT_JVM_ARGS, MAIN_WINDOW_CONFIG, CONFIG_FILE_NAME, 
    VERSION_TYPES, USERNAME_LIMITS
)
from file_manager import FileManager
from java_manager import JavaManager
from version_manager import VersionManager
from minecraft_launcher import MinecraftLauncher
from user_data_manager import UserDataManager
from username_generator import UsernameGenerator
from ui_components import UIComponents


class Launchercito:
    """Launcher principal de Minecraft"""

    def __init__(self, main_root: tk.Tk) -> None:
        self.root = main_root
        
        # Variables de estado de la UI
        self.enable_uuid_var: tk.BooleanVar = tk.BooleanVar()
        self.snapshot_var: tk.BooleanVar = tk.BooleanVar()
        self.alpha_var: tk.BooleanVar = tk.BooleanVar()
        self.beta_var: tk.BooleanVar = tk.BooleanVar()
        self.especial_var: tk.BooleanVar = tk.BooleanVar()
        self.advanced_options_close_launcher_var: tk.BooleanVar = tk.BooleanVar()
        self.advanced_options_memory_var: tk.StringVar = tk.StringVar()
        self.advanced_options_directory_var: tk.StringVar = tk.StringVar()
        self.java_executable_var: tk.StringVar = tk.StringVar()
        self.hide_log_var: tk.BooleanVar = tk.BooleanVar()
        
        # Variables para opciones avanzadas
        self._original_close_launcher_var_value: bool = False
        from ui_components import UIComponents
from advanced_options_ui import AdvancedOptionsUI


class Launchercito:
    """Launcher principal de Minecraft"""

    def __init__(self, main_root: tk.Tk) -> None:
        self.root = main_root
        
        # Variables de estado de la UI
        self.enable_uuid_var: tk.BooleanVar = tk.BooleanVar()
        self.snapshot_var: tk.BooleanVar = tk.BooleanVar()
        self.alpha_var: tk.BooleanVar = tk.BooleanVar()
        self.beta_var: tk.BooleanVar = tk.BooleanVar()
        self.especial_var: tk.BooleanVar = tk.BooleanVar()
        self.advanced_options_close_launcher_var: tk.BooleanVar = tk.BooleanVar()
        self.advanced_options_memory_var: tk.StringVar = tk.StringVar()
        self.advanced_options_directory_var: tk.StringVar = tk.StringVar()
        self.java_executable_var: tk.StringVar = tk.StringVar()
        self.hide_log_var: tk.BooleanVar = tk.BooleanVar()
        
        # Variables para opciones avanzadas
        self._original_close_launcher_var_value: bool = False
        self._original_memory_var_value: str = """
        # Ventanas (gestionadas por AdvancedOptionsUI)
        # self.advanced_options_window: Optional[tk.Toplevel] = None # Removido, gestionado por AdvancedOptionsUI
        
        # Estado del juego
        self.game_launched: bool = False
        self.previous_username: str = ""
        self.is_launcher_closed: bool = False
        self.minecraft_directory: str = ""
        
        # Inicializar gestores
        self._initialize_managers()
        
        # Inicializar UI
        self.ui_components = UIComponents(self.root)
        self.advanced_options_ui = AdvancedOptionsUI(
            self.root,
            self.advanced_options_close_launcher_var,
            self.advanced_options_memory_var,
            self.advanced_options_directory_var,
            self.java_executable_var,
            self.hide_log_var,
            self.enable_uuid_var,
            self.resource_path,
            self.apply_advanced_options,
            self.cancel_advanced_options,
            self.select_java_executable,
            self.select_minecraft_directory
        )
        
        # Inicializar launcher
        self.root.withdraw()
        self.root.after(0, self._initialize_launcher)

    def _initialize_managers(self) -> None:
        """Inicializa todos los gestores"""
        # Inicializar file manager temporalmente para obtener el directorio
        temp_file_manager = FileManager("", CONFIG_FILE_NAME)
        self.minecraft_directory = temp_file_manager.initialize_minecraft_directory()
        
        # Inicializar gestores con el directorio correcto
        self.file_manager = FileManager(self.minecraft_directory, CONFIG_FILE_NAME)
        self.java_manager = JavaManager(self.minecraft_directory)
        self.version_manager = VersionManager(self.minecraft_directory)
        self.minecraft_launcher = MinecraftLauncher(self.minecraft_directory)
        self.user_data_manager = UserDataManager(self.file_manager)
        self.username_generator = UsernameGenerator()

    def _initialize_launcher(self) -> None:
        """Inicializa el launcher"""
        self._configure_root_window()
        self.create_widgets()
        self._initialize_configuration()
        self.initialize_user_data()
        
        if self.root:
            self.root.protocol("WM_DELETE_WINDOW", self.close_launcher)
            self.root.deiconify()

    @staticmethod
    def resource_path(relative_path: str) -> str:
        """Obtiene la ruta del recurso"""
        base_path: str
        try:
            base_path = sys._MEIPASS  # type: ignore
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def _configure_root_window(self) -> None:
        """Configura la ventana principal"""
        if self.root:
            self.root.resizable(MAIN_WINDOW_CONFIG["resizable"])
            self.root.title(MAIN_WINDOW_CONFIG["title"])
            self.root.geometry(MAIN_WINDOW_CONFIG["geometry"])
            try:
                self.root.iconbitmap(self.resource_path(MAIN_WINDOW_CONFIG["icon_path"]))
            except:
                pass  # Ignorar si no se encuentra el icono

    def _initialize_configuration(self) -> None:
        """Inicializa la configuración"""
        try:
            self.file_manager.ensure_launcher_profiles_exists()
            self.advanced_options_directory_var.set(self.minecraft_directory)
        except Exception as e:
            messagebox.showerror("Error de Configuración", str(e))

    def create_widgets(self) -> None:
        """Crea todos los widgets de la UI"""
        self.ui_components.create_main_frame()
        
        # Crear widgets con callbacks
        self.ui_components.create_username_widgets(
            self.on_user_selected, 
            self.generate_random_user_data
        )
        
        # Crear variables de versión
        version_vars = {
            "snapshot": self.snapshot_var,
            "alpha": self.alpha_var,
            "beta": self.beta_var,
            "especial": self.especial_var,
        }
        
        self.ui_components.create_version_widgets(
            version_vars, 
            self.handle_checkbox_change
        )
        
        self.ui_components.create_uuid_widgets()
        
        self.ui_components.create_buttons(
            self.launch_minecraft,
            self.close_game,
            self.create_advanced_options_window
        )
        
        self.ui_components.create_log_frame()
        
        # Configurar eventos adicionales
        self._setup_additional_events()

    def _setup_additional_events(self) -> None:
        """Configura eventos adicionales"""
        if self.ui_components.entry_username:
            self.ui_components.entry_username.bind("<FocusOut>", lambda event: self.update_uuid_entry())
            self.ui_components.entry_username.bind("<KeyRelease>", lambda event: self.update_uuid_entry())

    def handle_checkbox_change(self, selected_var: tk.BooleanVar) -> None:
        """Maneja el cambio de checkboxes de versión"""
        if selected_var.get():
            # Desmarcar otros checkboxes
            for var in [self.snapshot_var, self.alpha_var, self.beta_var, self.especial_var]:
                if var != selected_var:
                    var.set(False)
        
        self.update_version_list()

    def log_message(self, message: str) -> None:
        """Registra un mensaje en el log"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        if self.ui_components.log_text:
            self.ui_components.log_text.config(state=tk.NORMAL)
            
            if "Comando de Minecraft ejecutado:" in message:
                formatted_message = self.minecraft_launcher.format_command_message(message)
                self.ui_components.log_text.insert(tk.END, f"[{timestamp}] {formatted_message}\n\n")
            elif message.startswith("Advertencia:"):
                self.ui_components.log_text.insert(tk.END, f"[{timestamp}] WARNING: {message}\n\n")
            else:
                self.ui_components.log_text.insert(tk.END, f"[{timestamp}] {message}\n\n")
            
            self.ui_components.log_text.config(state=tk.DISABLED)
            self.ui_components.log_text.yview(tk.END)

    def _run_on_main_thread(self, func: Any, *args: Any, **kwargs: Any) -> None:
        """Ejecuta una función en el hilo principal"""
        try:
            if self.root and self.root.winfo_exists():
                self.root.after(0, lambda: func(*args, **kwargs))
        except RuntimeError:
            pass  # Ignorar errores de hilo

    def generate_random_user_data(self) -> None:
        """Genera datos de usuario aleatorios"""
        random_username = self.username_generator.generate_random_username()
        self.ui_components.set_username(random_username)
        
        if self.ui_components.entry_username:
            self.ui_components.entry_username.config(foreground="gray")
        
        self.update_uuid_entry()

    def update_uuid_entry(self) -> None:
        """Actualiza la entrada de UUID"""
        username = self.ui_components.get_username()
        
        if not username:
            self.ui_components.set_uuid("Random")
        elif username.lower() != "random" and username != self.previous_username:
            uuid_value = str(self.minecraft_launcher.generate_uuid_for_username(username))
            self.ui_components.set_uuid(uuid_value)
        
        if username or username.lower() == "random":
            self.previous_username = username

    def on_user_selected(self, event: Optional[tk.Event] = None) -> None:
        """Maneja la selección de usuario"""
        selected_username = self.ui_components.get_username()
        if selected_username:
            self.load_user_data_from_directory()

    def initialize_user_data(self) -> None:
        """Inicializa los datos de usuario"""
        self.advanced_options_directory_var.set(self.minecraft_directory)
        user_data_list = self.user_data_manager.load_user_data_from_directory(self.minecraft_directory)
        
        if user_data_list:
            last_user_data = user_data_list[-1]
            self._set_user_data(last_user_data)
            self.ui_components.set_username(last_user_data.get("username", ""))
        else:
            self.generate_random_user_data()
        
        self.hide_show_log()

    def load_user_data_from_directory(self, directory: Optional[str] = None) -> None:
        """Carga datos de usuario desde directorio"""
        try:
            directory = directory or self.advanced_options_directory_var.get().strip()
            user_data_list = self.user_data_manager.load_user_data_from_directory(directory)
            
            if user_data_list:
                valid_users = self.user_data_manager.get_valid_usernames(user_data_list)
                self.ui_components.set_username_values(valid_users)
                
                current_username = self.ui_components.get_username()
                selected_user = self.user_data_manager.find_user_by_username(user_data_list, current_username)
                
                if selected_user:
                    self._set_user_data(selected_user)
        except Exception as e:
            self.log_message(f"Error cargando datos: {str(e)}")

    def _set_user_data(self, user_data: Dict[str, Any]) -> None:
        """Establece los datos del usuario en la UI"""
        # Establecer tipo de versión
        version_type = user_data.get("type_version", "release")
        self.snapshot_var.set(version_type == "snapshot")
        self.alpha_var.set(version_type == "alpha")
        self.beta_var.set(version_type == "beta")
        self.especial_var.set(version_type == "especial")
        
        # Actualizar lista de versiones
        self.update_version_list()
        
        # Establecer versión seleccionada
        saved_version = user_data.get("selected_version", "")
        self.ui_components.set_version(saved_version)
        
        # Establecer otras opciones
        self.advanced_options_close_launcher_var.set(user_data.get("advanced_options_close_launcher", False))
        self.advanced_options_directory_var.set(user_data.get("advanced_options_directory", ""))
        self.java_executable_var.set(user_data.get("java_executable", ""))
        self.java_manager.set_java_executable(user_data.get("java_executable", ""))
        self.advanced_options_memory_var.set(user_data.get("jvm_args", " ".join(DEFAULT_JVM_ARGS)))
        
        # Configurar log y UUID
        hide_log_value = user_data.get("hide_log", False)
        self.hide_log_var.set(hide_log_value)
        self.hide_show_log()
        
        enable_uuid_value = user_data.get("enable_uuid", False)
        self.enable_uuid_var.set(enable_uuid_value)
        self._update_uuid_visibility(enable_uuid_value, user_data.get("uuid", ""))

    def _update_uuid_visibility(self, enable_uuid_value: bool, uuid_value: str) -> None:
        """Actualiza la visibilidad del UUID"""
        if enable_uuid_value:
            self.ui_components.show_uuid_widgets(uuid_value)
        else:
            self.ui_components.hide_uuid_widgets()
        
        self.adjust_window_size()

    def hide_show_log(self) -> None:
        """Muestra u oculta el log"""
        if self.hide_log_var.get():
            if self.ui_components.log_frame:
                height = 182 if self.enable_uuid_var.get() else 150
                self.ui_components.log_frame.place(x=305, y=5, width=520, height=height)
        else:
            if self.ui_components.log_frame:
                self.ui_components.log_frame.place_forget()
        
        self.adjust_window_size()

    def adjust_window_size(self) -> None:
        """Ajusta el tamaño de la ventana"""
        base_width = 830 if self.hide_log_var.get() else 305
        base_height = 192 if self.enable_uuid_var.get() else 160
        
        if self.root:
            self.root.geometry(f"{base_width}x{base_height}")
            self.root.update_idletasks()
            self.center_window(base_width, base_height)

    def center_window(self, width: int, height: int) -> None:
        """Centra la ventana en la pantalla"""
        if self.root and self.root.winfo_exists():
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            x = (screen_width // 2) - (width // 2)
            y = (screen_height // 2) - (height // 2)
            self.root.geometry(f"+{x}+{y}")

    def update_version_list(self) -> None:
        """Actualiza la lista de versiones"""
        if self.root and self.root.winfo_exists():
            self.root.after(0, self._update_version_list_internal)

    def _update_version_list_internal(self) -> None:
        """Actualiza la lista de versiones internamente"""
        try:
            all_versions = self.version_manager.get_available_versions()
            selected_types = self._get_selected_version_types()
            available_versions = self.version_manager.filter_versions_by_type(all_versions, selected_types)
            version_names = [version["id"] for version in available_versions]
            
            self.ui_components.set_version_values(version_names)
            
            current_selection = self.ui_components.get_version()
            if current_selection not in version_names and version_names:
                self.ui_components.set_version(version_names[0])
                
        except Exception as e:
            self.log_message(f"Error actualizando versiones: {str(e)}")

    def _get_selected_version_types(self) -> List[str]:
        """Obtiene los tipos de versión seleccionados"""
        selected_types: List[str] = []
        
        if self.snapshot_var.get():
            selected_types.append("snapshot")
        if self.alpha_var.get():
            selected_types.append("old_alpha")
        if self.beta_var.get():
            selected_types.append("old_beta")
        if self.especial_var.get():
            selected_types.append("especial")
            
        return selected_types

    def launch_minecraft(self) -> None:
        """Lanza Minecraft"""
        if not self.validate_inputs():
            return
        
        selected_version = self.ui_components.get_version()
        if not self.version_manager.is_valid_version(selected_version):
            messagebox.showerror("Error", f"La versión '{selected_version}' no es válida.")
            return
        
        self.prepare_ui_for_launch()
        self.handle_modloader(selected_version)
        
        username_input = self.ui_components.get_username()
        
        if not self.version_manager.version_directory_exists(selected_version):
            threading.Thread(target=self.install_version, args=(selected_version,), daemon=True).start()
        else:
            threading.Thread(target=self.run_minecraft, args=(selected_version, username_input), daemon=True).start()

    def validate_inputs(self) -> bool:
        """Valida las entradas del usuario"""
        username_input = self.ui_components.get_username()
        
        if not username_input or username_input.lower() == "random":
            self.generate_random_user_data()
            username_input = self.ui_components.get_username()
        
        is_valid, warning_message = self.username_generator.validate_username_length(username_input)
        
        if not is_valid:
            user_response = messagebox.askquestion(
                "¡ADVERTENCIA!", 
                warning_message + "\n¿Continuar de todos modos?",
                icon="warning"
            )
            return user_response == "yes"
        
        return True

    def prepare_ui_for_launch(self) -> None:
        """Prepara la UI para el lanzamiento"""
        self.ui_components.update_button_states(False)
        if self.ui_components.button_close_game:
            self.ui_components.button_close_game["state"] = "disabled"

    def handle_modloader(self, selected_version: str) -> None:
        """Maneja versiones con modloader"""
        if self.version_manager.has_modloader(selected_version):
            base_version = self.file_manager.extract_base_version(selected_version)
            self.version_manager.copy_jar_for_modloader(selected_version, base_version)

    def install_version(self, selected_version: str) -> None:
        """Instala una versión de Minecraft"""
        def set_status(status: str) -> None:
            self.log_message(f"Estado: {status}")

        def set_progress(progress: int) -> None:
            if self.minecraft_launcher.current_max != 0:
                self.log_message(f"Progreso: {progress}/{self.minecraft_launcher.current_max}")

        def set_max(new_max: int) -> None:
            self.minecraft_launcher.current_max = new_max

        callback_functions = {
            "set_status": set_status,
            "set_progress": set_progress,
            "set_max": set_max,
        }

        try:
            self.log_message(f"Iniciando la instalación de '{selected_version}'...")
            
            if self.minecraft_launcher.install_version(selected_version, callback_functions):
                self.log_message(f"La versión '{selected_version}' se instaló correctamente.")
                username_for_launch = self.ui_components.get_username()
                self.run_minecraft(selected_version, username_for_launch)
                
        except Exception as e:
            self.log_message(f"Error: {str(e)}")
            self._run_on_main_thread(messagebox.showerror, "Error de Instalación", str(e))
        finally:
            if not self.game_launched:
                self._run_on_main_thread(self.ui_components.update_button_states, False)

    def run_minecraft(self, selected_version: str, username_input: str) -> None:
        """Ejecuta Minecraft"""
        try:
            self.log_message("Iniciando Minecraft...")
            
            # Obtener ejecutable de Java
            is_alpha_beta = self.alpha_var.get() or self.beta_var.get()
            java_executable = self.java_manager.get_java_executable_path(selected_version, is_alpha_beta)
            
            # Log de versión de Java
            java_version = self.java_manager.get_java_version(java_executable)
            if java_version:
                self.log_message(f"Versión de Java: {java_version}")
            
            # Obtener argumentos JVM
            jvm_args_str = self.advanced_options_memory_var.get().strip()
            jvm_arguments = jvm_args_str.split() if jvm_args_str else DEFAULT_JVM_ARGS
            
            # Obtener opciones de lanzamiento
            options = self.minecraft_launcher.get_launch_options(username_input, jvm_arguments)
            
            # Ejecutar Minecraft
            process = self.minecraft_launcher.run_minecraft(selected_version, options, java_executable)
            
            # Log del comando
            command_str = self.minecraft_launcher.get_minecraft_command_string([java_executable] + jvm_arguments)
            self.log_message(f"Comando de Minecraft ejecutado: {command_str}")
            
            # Cerrar launcher si está configurado
            if self.advanced_options_close_launcher_var.get():
                if self.root:
                    self._run_on_main_thread(self.root.destroy)
            
            self._run_on_main_thread(self.ui_components.update_button_states, True)
            
        except Exception as e:
            error_msg = f"Error al lanzar Minecraft: {str(e)}"
            self.log_message(error_msg)
            self._run_on_main_thread(messagebox.showerror, "Error de Lanzamiento", error_msg)
            self._run_on_main_thread(self.ui_components.update_button_states, False)

    def close_game(self) -> None:
        """Cierra el juego"""
        try:
            if self.minecraft_launcher.close_game():
                self.log_message("Minecraft cerrado correctamente.")
            else:
                self.log_message("No se encontró ningún proceso de Minecraft para cerrar.")
            
            self.ui_components.update_button_states(False)
            
        except Exception as e:
            self.log_message(f"Error al cerrar el juego: {e}")

    def create_advanced_options_window(self) -> None:
        """Crea la ventana de opciones avanzadas"""
        # TODO: Implementar ventana de opciones avanzadas
        # Por ahora, mostrar un mensaje
        messagebox.showinfo("Opciones Avanzadas", "Funcionalidad en desarrollo")

    def close_launcher(self) -> None:
        """Cierra el launcher"""
        self._save_user_data()
        self.is_launcher_closed = True
        if self.root:
            self.root.destroy()

    def _save_user_data(self) -> None:
        """Guarda los datos del usuario"""
        username = self.ui_components.get_username()
        
        if self.username_generator.is_randomly_generated(username):
            return
        
        # Determinar tipo de versión
        version_type = "release"
        if self.snapshot_var.get():
            version_type = "snapshot"
        elif self.alpha_var.get():
            version_type = "alpha"
        elif self.beta_var.get():
            version_type = "beta"
        elif self.especial_var.get():
            version_type = "especial"
        
        user_data = self.user_data_manager.create_user_data_dict(
            username=username,
            uuid_str=self.ui_components.get_uuid(),
            selected_version=self.ui_components.get_version(),
            version_type=version_type,
            directory=self.advanced_options_directory_var.get().strip(),
            close_launcher=self.advanced_options_close_launcher_var.get(),
            hide_log=self.hide_log_var.get(),
            enable_uuid=self.enable_uuid_var.get(),
            jvm_args=self.advanced_options_memory_var.get().strip(),
            java_executable=self.java_executable_var.get().strip()
        )
        
        self.user_data_manager.save_user_data(user_data)


def main():
    """Función principal"""
    root = tk.Tk()
    launcher = Launchercito(root)
    root.mainloop()


if __name__ == "__main__":
    main()