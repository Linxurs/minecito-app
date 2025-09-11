import json
import os
import random
import subprocess
import sys
import shutil
import threading
import time
import tkinter as tk
import uuid
from tkinter import filedialog, messagebox, ttk
from minecraft_launcher_lib.types import MinecraftVersionInfo, CallbackDict, MinecraftOptions
import minecraft_launcher_lib
from typing import Any, Optional, cast

_ADJECTIVES = sorted(
    [
        "Bill", "Cal", "Dar", "Fun", "Gen", "Gol", "Happy", "Hol", "Krit",
        "Mig",  "Nus", "Sad", "Ser", "Shy", "Sil", "Smad", "Swy", "Thom",
    ]
)
_NOUNS = sorted(
    [
        "Bird", "Blast", "Cat", "Dog", "Dolly", "Don", "Elephy", "Fish",
        "Gra", "Lio", "Moo", "Nick", "Nill", "Phel", "Star", "Story",
        "Turly", "Vey", "White", "Win", "Znack",
    ]
)

class Launchercito:

    default_jvm_args = [
        "-Xmx2G",
        "-XX:+UnlockExperimentalVMOptions",
        "-XX:+UseG1GC",
        "-XX:G1NewSizePercent=20",
        "-XX:G1ReservePercent=20",
        "-XX:MaxGCPauseMillis=50",
        "-XX:G1HeapRegionSize=32M",
    ]
    java_executable = ""
    
    def __init__(self, main_root: tk.Tk) -> None:
        self.root = main_root
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
        self._original_close_launcher_var_value: bool = False
        self._original_memory_var_value: str = ""
        self._original_directory_var_value: str = ""
        self._original_java_executable_var_value: str = ""
        self._original_hide_log_var_value: bool = False
        self._original_delete_user_on_apply_var_value: bool = False
        self.delete_user_on_apply_var: tk.BooleanVar = tk.BooleanVar()
        self.advanced_options_window: Optional[tk.Toplevel] = None
        self.log_frame: Optional[ttk.Frame] = None
        self.java_executable: str = ""
        self.hide_log_checkbox: Optional[ttk.Checkbutton] = None
        self.enable_uuid_checkbox: Optional[ttk.Checkbutton] = None
        self.delete_user_checkbox: Optional[ttk.Checkbutton] = None
        self.frame: Optional[ttk.Frame] = None
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
        self.log_text: Optional[tk.Text] = None
        self.process: Optional[subprocess.Popen[str]] = None
        self.game_launched: bool = False
        self.previous_username: str = ""
        self.update_buttons_thread: Optional[threading.Thread] = None
        self.current_max: int = 0
        self.hide_log_var_original: Optional[bool] = None
        self.minecraft_directory: str = ""
        self.config_file: str = "minecito_config.json"
        self.version_vars: dict[str, tk.BooleanVar] = {}
        self.is_launcher_closed: bool = False
        self.root.withdraw()
        self.root.after(0, self._initialize_launcher)

    def _run_on_main_thread(self, func: Any, *args: Any, **kwargs: Any) -> None:
        try:
            if self.root and self.root.winfo_exists():
                self.root.after(0, lambda: func(*args, **kwargs))
            else:
                self.log_message(f"Advertencia: No se pudo programar la función {func.__name__} en el hilo principal, la ventana raíz no existe o ya fue destruida.")
        except RuntimeError as e:
            self.log_message(f"Advertencia: Error al intentar programar la función {func.__name__} en el hilo principal: {e}")

    def _initialize_launcher(self) -> None:
        self._configure_root_window()
        self.create_widgets()
        
        self._initialize_configuration()
        self.initialize_user_data()
        assert self.root is not None
        self.root.protocol("WM_DELETE_WINDOW", self.close_launcher)
        self.root.deiconify()

    @staticmethod
    def resource_path(relative_path: str) -> str:
        base_path: str
        try:
            base_path = cast(str, sys._MEIPASS)  # type: ignore
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def _configure_root_window(self) -> None:
        if self.root:
            self.root.resizable(False, False)
            self.root.title("Minecito v1.5")
            self.root.geometry("305x160")
            self.root.iconbitmap(self.resource_path("icons/minecito_launcher.ico"))  # type: ignore

    def _initialize_configuration(self) -> None:
        default_minecraft_directory = minecraft_launcher_lib.utils.get_minecraft_directory()
        
        if not os.access(default_minecraft_directory, os.W_OK):
            local_appdata_path = os.path.join(os.environ.get("LOCALAPPDATA", ""), ".minecito")
            
            if not os.path.exists(local_appdata_path):
                os.makedirs(local_appdata_path)
            
            self.minecraft_directory = local_appdata_path
            messagebox.showwarning(
                "Permisos Insuficientes",
                f"No se tienen permisos para escribir en el directorio predeterminado de Minecraft: {default_minecraft_directory}. "
                f"Se utilizará el directorio: {self.minecraft_directory} en su lugar."
            )
        else:
            self.minecraft_directory = default_minecraft_directory
        
        self._ensure_launcher_profiles_exists()

    def log_message(self, message: str) -> None:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        if self.log_text:
            self.log_text.config(state=tk.NORMAL)

        if "Comando de Minecraft ejecutado:" in message:
            formatted_message = self.format_command_message(message)
            if self.log_text:
                self.log_text.insert(tk.END, f"[{timestamp}] {formatted_message}\n\n")
        elif message.startswith("Advertencia:"):
            if self.log_text:
                self.log_text.insert(tk.END, f"[{timestamp}] WARNING: {message}\n\n")
        else:
            if self.log_text:
                self.log_text.insert(tk.END, f"[{timestamp}] {message}\n\n")

        if self.log_text:
            self.log_text.config(state=tk.DISABLED)
            self.log_text.yview(tk.END)  # type: ignore

    def _show_error_message_on_main_thread(self, title: str, message: str) -> None:
        self._run_on_main_thread(messagebox.showerror, title, message)
        self._run_on_main_thread(self._reset_ui_after_error)

    def format_command_message(self, message: str) -> str:
        cmd: str = message.split(": ", 1)[1]
        parts: list[str] = cmd.split()
        formatted: list[str] = ["INFORMACIÓN DE LA SESIÓN:"]

        java_index = 0
        cp_index: int = parts.index("-cp") if "-cp" in parts else -1
        user_index = -1
        options_start = -1

        for i, part in enumerate(parts):
            if part == "net.minecraft.launchwrapper.Launch":
                user_index = i + 1
            elif part.startswith("--"):
                options_start = i
                break

        formatted.extend(self.format_java_section(parts, java_index))
        formatted.extend(self.format_cp_section(parts, cp_index))
        formatted.extend(self.format_user_section(parts, user_index))
        formatted.extend(self.format_options_section(parts, options_start))

        return "".join(formatted)

    def format_java_section(self, parts: list[str], java_index: int) -> list[str]:
        return ["\n\n=== Java ===", f"\n{parts[java_index].replace('/', '\\')}"]

    def format_cp_section(self, parts: list[str], cp_index: int) -> list[str]:
        if cp_index == -1:
            return []

        formatted: list[str] = [
            "\n\n=== Parámetros ===",
            f"\n  -Djava.library.path={parts[cp_index - 1].replace('/', '\\')}",
            "\n  -cp",
        ]
        unique_jars: set[str] = set()
        for jar in parts[cp_index + 1].split(";"):
            clean_jar = jar.strip().replace("/", "\\")
            if clean_jar and clean_jar not in unique_jars:
                formatted.append(f"\n    {clean_jar}")
                unique_jars.add(clean_jar)

        return formatted

    def format_user_section(self, parts: list[str], user_index: int) -> list[str]:
        if user_index == -1:
            return []

        return [
            "\n\n=== Usuario ===",
            f"\n  {parts[user_index]}",
            f"\n  {parts[user_index + 1]}",
        ]

    def format_options_section(self, parts: list[str], options_start: int) -> list[str]:
        if options_start == -1:
            return []

        formatted = ["\n\n=== Opciones ==="]
        for i in range(options_start, len(parts), 2):
            if i + 1 < len(parts):
                formatted.append(f"\n  {parts[i]} {parts[i + 1].replace('/', '\\')}")

        return formatted

    def _save_user_data(self) -> None:
        if self.entry_username:
            username = self.entry_username.get().strip()
        else:
            username = ""
        if self._is_randomly_generated(username):
            return
        user_data = self._create_user_data_dict()
        config_file_path = self._get_config_file_path(user_data)
        if os.path.exists(config_file_path):
            user_data_list = self._read_config_file(config_file_path)
        else:
            user_data_list = []
        user_data_list = self._remove_duplicate_user_data(user_data_list, user_data)
        user_data_list.append(user_data)
        self._write_config_file(config_file_path, user_data_list)
        self._update_delete_user_checkbox_state(user_data_list)

    def _create_user_data_dict(self) -> dict[str, Any]:
        return {
            "index": self._generate_user_index(),
            "username": self.entry_username.get().strip() if self.entry_username else "",
            "uuid": self.entry_uuid.get().strip() if self.entry_uuid else "",
            "selected_version": self.combobox_version.get().strip() if self.combobox_version else "",
            "type_version": (
                "snapshot"
                if self.snapshot_var.get()
                else (
                    "alpha"
                    if self.alpha_var.get()
                    else (
                        "beta"
                        if self.beta_var.get()
                        else "especial" if self.especial_var.get() else "release"
                    )
                )
            ),
            "advanced_options_directory": self.advanced_options_directory_var.get().strip(),
            "advanced_options_close_launcher": self.advanced_options_close_launcher_var.get(),
            "hide_log": self.hide_log_var.get(),
            "enable_uuid": self.enable_uuid_var.get(),
            "jvm_args": self.advanced_options_memory_var.get().strip(),
            "java_executable": self.java_executable_var.get().strip(),
        }

    def _get_config_file_path(self, user_data: dict[str, Any]) -> str:
        return os.path.join(
            user_data["advanced_options_directory"], "minecito_config.json"
        )

    def _read_config_file(self, config_path: str) -> list[dict[str, Any]]:
        try:
            with open(config_path, "r", encoding="utf-8") as json_file:
                data = json.load(json_file)
                if not isinstance(data, list):
                    return [data]
                return cast(list[dict[str, Any]], data)
        except json.JSONDecodeError:
            self.log_message(f"Archivo JSON corrupto: {config_path}")
            return cast(list[dict[str, Any]], [])
        except FileNotFoundError:
            return cast(list[dict[str, Any]], [])
        except IOError as e:
            self.log_message(f"Error de E/S al cargar configuración: {e}")
            return cast(list[dict[str, Any]], [])
        except Exception as e:
            self.log_message(f"Error inesperado al cargar configuración: {e}")
            return cast(list[dict[str, Any]], [])

    def _remove_duplicate_user_data(self, user_data_list: list[dict[str, Any]], user_data: dict[str, Any]) -> list[dict[str, Any]]:
        return [data for data in user_data_list if data["username"] != user_data["username"]]

    def _write_config_file(self, config_file_path: str, user_data_list: list[dict[str, Any]]) -> None:
        try:
            os.makedirs(os.path.dirname(config_file_path), exist_ok=True)
            with open(config_file_path, "w", encoding="utf-8") as json_file:
                json.dump(user_data_list, json_file, indent=2)
        except IOError as e:
            error_msg = f"Error de E/S al guardar la configuración en {config_file_path}: {e}"
            self.log_message(error_msg)
            self._show_error_message_on_main_thread("Error al Guardar", f"No se pudo guardar la configuración en {config_file_path}. Verifique los permisos.")
        except Exception as e:
            error_msg = f"Error inesperado al guardar la configuración: {e}"
            self.log_message(error_msg)
            self._show_error_message_on_main_thread("Error Inesperado", f"Ocurrió un error inesperado al guardar la configuración: {e}")

    def _generate_user_index(self) -> int:
        config_file_path = os.path.join(
            self.advanced_options_directory_var.get().strip(), "minecito_config.json"
        )
        if os.path.exists(config_file_path):
            with open(config_file_path, "r", encoding="utf-8") as json_file:
                user_data_list = json.load(json_file)
                return len(user_data_list) + 1
        return 1

    def load_user_data_from_directory(self, directory: Optional[str] = None) -> None:
        try:
            directory = directory or self.advanced_options_directory_var.get().strip()
            config_file_path = os.path.join(directory, self.config_file)
            if not os.path.exists(config_file_path):
                return
            user_data_list = self._read_config_file(config_file_path)
            self._process_user_data(user_data_list)
        except Exception as e:
            self.log_message(f"Error cargando datos: {str(e)}")

    def _process_user_data(self, user_data_list: list[dict[str, Any]]) -> None:
        if not user_data_list:
            self.log_message("No se encontraron datos de usuario.")
            return

        self._set_username_dropdown(user_data_list)
        self._apply_selected_user_data(user_data_list)

    def _set_username_dropdown(self, user_data_list: list[dict[str, Any]]) -> None:
        valid_users = [
            user["username"]
            for user in user_data_list
            if not self._is_randomly_generated(user.get("username", ""))
        ]
        if self.entry_username:
            self.entry_username["values"] = valid_users

    def _apply_selected_user_data(self, user_data_list: list[dict[str, Any]]) -> None:
        if self.entry_username:
            current_username = self.entry_username.get().strip()
        else:
            current_username = ""
        selected_user = self._find_user_by_username(user_data_list, current_username)
        if selected_user:
            self._set_user_data(selected_user)

    def _find_user_by_username(self, user_data_list: list[dict[str, Any]], username: str) -> Optional[dict[str, Any]]:
        return next(
            (user for user in user_data_list if user.get("username") == username), None
        )

    def _set_user_data(self, user_data: dict[str, Any]) -> None:
        version_type = user_data.get("type_version", "release")
        if self.snapshot_var:
            self.snapshot_var.set(version_type == "snapshot")
        if self.alpha_var:
            self.alpha_var.set(version_type == "alpha")
        if self.beta_var:
            self.beta_var.set(version_type == "beta")
        if self.especial_var:
            self.especial_var.set(version_type == "especial")
        self.update_version_list()

        saved_version = user_data.get("selected_version", "")

        if self.combobox_version:
            self.combobox_version.set(saved_version)
            if not self.combobox_version.get() and self.combobox_version["values"]:
                self.combobox_version.set(self.combobox_version["values"][0])

        if self.advanced_options_close_launcher_var:
            self.advanced_options_close_launcher_var.set(
                user_data.get("advanced_options_close_launcher", False)
            )
        if self.advanced_options_directory_var:
            self.advanced_options_directory_var.set(
                user_data.get("advanced_options_directory", "")
            )
        if self.java_executable_var:
            self.java_executable_var.set(user_data.get("java_executable", ""))
        self.java_executable = user_data.get("java_executable", "")
        self.advanced_options_memory_var.set(
            user_data.get("jvm_args", " ".join(self.default_jvm_args))
        )
        self.update_version_list()

        hide_log_value = user_data.get("hide_log", False)
        enable_uuid_value = user_data.get("enable_uuid", False)

        if self.hide_log_var:
            self.hide_log_var.set(hide_log_value)
        if self.enable_uuid_var:
            self.enable_uuid_var.set(enable_uuid_value)

        self.hide_show_log()
        self._update_uuid_visibility(enable_uuid_value, user_data.get("uuid", ""))
        

    def _update_uuid_visibility(self, enable_uuid_value: bool, uuid_value: str) -> None:
        if enable_uuid_value:
            if self.label_uuid:
                self.label_uuid.place(x=40, y=95)
            if self.entry_uuid:
                self.entry_uuid.place(x=120, y=95)
                self.entry_uuid.delete(0, tk.END)
                self.entry_uuid.insert(0, uuid_value)
            self.move_buttons_for_uuid_visible()
        else:
            if self.label_uuid:
                self.label_uuid.place_forget()
            if self.entry_uuid:
                self.entry_uuid.place_forget()
            self.restore_buttons_original_position()
        self.adjust_window_size()
        if enable_uuid_value:
            if self.log_text:
                self.log_text.config(height=11, width=63)
        else:
            if self.log_text:
                self.log_text.config(height=9, width=63)

    def update_minecraft_directory(self, new_directory: str) -> None:
        if os.path.isdir(new_directory):
            self.minecraft_directory = new_directory
            self.advanced_options_directory_var.set(new_directory.replace("/", "\\"))
            self.load_user_data_from_directory(new_directory)
            self.update_java_executable_path()

    def select_minecraft_directory(self) -> None:
        selected_directory = filedialog.askdirectory(
            initialdir=self.minecraft_directory,
            title="Seleccionar directorio de Minecraft",
        )
        if selected_directory:
            self.advanced_options_directory_var.set(
                selected_directory
            )
            self.update_minecraft_directory(selected_directory)
        if self.advanced_options_window and self.advanced_options_window.winfo_exists():
            self.advanced_options_window.lift()  # type: ignore

    def hide_show_log(self) -> None:
        if self.hide_log_var and self.hide_log_var.get():
            if self.log_frame:
                self.log_frame.place(x=305, y=5, width=520, height=self._get_log_frame_height())
        else:
            if self.log_frame:
                self.log_frame.place_forget()
        self.adjust_window_size()

    def adjust_window_size(self) -> None:
        base_width = 830 if self.hide_log_var and self.hide_log_var.get() else 305
        base_height = 192 if self.enable_uuid_var and self.enable_uuid_var.get() else 160
        if self.root:
            self.root.geometry(f"{base_width}x{base_height}")
            self.root.update_idletasks()
            self.center_window(base_width, base_height)

    def center_window(self, width: int, height: int) -> None:
        screen_width = 0
        screen_height = 0
        if self.root and self.root.winfo_exists():
            root_window: tk.Tk = self.root
            screen_width = root_window.winfo_screenwidth()
            screen_height = root_window.winfo_screenheight()
            x = (screen_width // 2) - (width // 2)
            y = (screen_height // 2) - (height // 2)
            self.root.geometry(f"+{x}+{y}")

    def _get_log_frame_height(self) -> int:
        return 182 if self.enable_uuid_var.get() else 150

    def close_launcher(self) -> None:
        self._save_user_data()
        self.is_launcher_closed = True
        if self.root:
            self.root.destroy()
            self.root = None

    def close_game(self) -> None:
        try:
            self._terminate_process()
            self.game_launched = False
            self._update_button_states()
        except ProcessLookupError:
            self._handle_process_lookup_error()
        except PermissionError:
            self.log_message("No tienes permisos para terminar el proceso.")
        except Exception as e:
            self.log_message(f"Error al cerrar el juego: {e}")

    def _terminate_process(self) -> None:
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.log_message("Minecraft cerrado correctamente.")
        else:
            self.log_message("No se encontró ningún proceso de Minecraft para cerrar.")

    def _handle_process_lookup_error(self) -> None:
        self.log_message("El proceso ya ha terminado.")
        self.game_launched = False
        if self.root:
            self._update_button_states()

    def generate_uuid_for_username(self, username: str) -> uuid.UUID:
        return uuid.uuid5(uuid.NAMESPACE_DNS, username)

    def launch_minecraft(self) -> None:
        if not self.validate_inputs():
            return
        selected_version = ""
        if self.combobox_version is not None:
            selected_version = self.combobox_version.get()
        if not self.is_valid_version(selected_version):
            self.show_invalid_version_error(selected_version)
            return
        self.prepare_ui_for_launch()
        self.handle_modloader(selected_version)
        username_input = self.entry_username.get().strip() if self.entry_username else ""
        if not self.version_directory_exists(selected_version):
            threading.Thread(
                target=self.install_version, args=(selected_version,), daemon=True
            ).start()
        else:
            threading.Thread(
                target=self.run_minecraft,
                args=(selected_version, self.get_launch_options(username_input)), daemon=True
            ).start()

    def validate_inputs(self) -> bool:
        username_input = self.entry_username.get().strip() if self.entry_username else ""
        if not self.validate_username(username_input):
            return False
        return True

    def prepare_ui_for_launch(self) -> None:
        if self.button_close_game:
            self.button_close_game["state"] = "disabled"
        self.disable_buttons()
        self.enable_close_button()

    def handle_modloader(self, selected_version: str) -> None:
        if any(
            modloader in selected_version.lower()
            for modloader in ["fabric", "quilt", "forge"]
        ):
            self.copy_jar_for_modloader(selected_version)

    def validate_username(self, username_input: str) -> bool:
        username_input = self.handle_random_username(username_input)
        if not self.validate_short_username(username_input):
            return False
        if not self.validate_long_username(username_input):
            return False
        return True

    def handle_random_username(self, username_input: str) -> str:
        if not username_input or username_input.lower() == "random":
            self.generate_random_user_data()
            return self.entry_username.get().strip() if self.entry_username else ""
        return username_input

    def validate_short_username(self, username_input: str) -> bool:
        if len(username_input) <= 2:
            warning_message = "No podrás jugar en modo online con un nombre tan corto."
            return self.confirm_warning(warning_message)
        return True

    def validate_long_username(self, username_input: str) -> bool:
        if len(username_input) > 15:
            warning_message = (
                "No podrás jugar en modo online con un nombre mayor a 15 caracteres."
            )
            return self.confirm_warning(warning_message)
        return True

    def confirm_warning(self, warning_message: str) -> bool:
        user_response = messagebox.askquestion(
            "¡ADVERTENCIA!",
            warning_message,
            detail="¿Continuar de todos modos?",
            icon="warning",
        )
        return user_response == "yes"

    def get_launch_options(self, username_input: str) -> dict[str, Any]:
        jvm_args_str = self.advanced_options_memory_var.get().strip()
        jvm_arguments = jvm_args_str.split() if jvm_args_str else []

        return {
            "username": username_input,
            "uuid": str(self.generate_uuid_for_username(username_input)),
            "token": "0",
            "jvmArguments": jvm_arguments,
        }

    def is_valid_version(self, selected_version: str) -> bool:
        return minecraft_launcher_lib.utils.is_version_valid(  # type: ignore
            selected_version, self.minecraft_directory
        )

    def show_invalid_version_error(self, selected_version: str) -> None:
        messagebox.showerror(
            "Error",
            f"La versión '{selected_version}' no es válida. Por favor, elija otra versión.",
        )

    def version_directory_exists(self, selected_version: str) -> bool:
        version_directory = os.path.join(
            self.minecraft_directory, "versions", selected_version
        )
        return os.path.exists(version_directory)

    def disable_buttons(self) -> None:
        if self.button_launch:
            self.button_launch["state"] = "disabled"
        if self.button_close_game:
            self.button_close_game["state"] = "disabled"

    def enable_close_button(self) -> None:
        if self.button_close_game:
            self.button_close_game["state"] = "normal"

    def run_minecraft(self, selected_version: str, options: dict[str, Any]) -> None:
        minecraft_command = minecraft_launcher_lib.command.get_minecraft_command(  # type: ignore
            selected_version, self.minecraft_directory, cast(MinecraftOptions, options)
        )
        threading.Thread(
            target=self.run_minecraft_thread, args=(minecraft_command,)
        ).start()

    def run_minecraft_thread(self, minecraft_command: list[str]) -> None:
        try:
            self.log_message("Iniciando Minecraft...")
            self.java_executable = self.get_or_set_java_executable()
            self.log_java_version()
            minecraft_command[0] = self.java_executable

            self.execute_minecraft_command(minecraft_command)
            if self.advanced_options_close_launcher_var.get():
                if self.root:
                    self._run_on_main_thread(self.root.destroy)
            self._run_on_main_thread(self.update_buttons_after_launch)
        except FileNotFoundError:
            error_msg = f"El ejecutable de Java no se encontró en la ruta: '{self.java_executable}'. Por favor, verifica la ruta en Opciones Avanzadas."
            self.log_message(f"Error: {error_msg}")
            self._show_error_message_on_main_thread("Java no encontrado", error_msg)
        except (subprocess.CalledProcessError, OSError) as e:
            error_msg = f"No se pudo iniciar Minecraft. Error del proceso: {e}"
            self.log_message(f"Error: {error_msg}")
            self._show_error_message_on_main_thread("Error de Lanzamiento", error_msg)
        except Exception as e:
            error_msg = f"Ocurrió un error inesperado al intentar lanzar Minecraft: {e}"
            self.log_message(f"Error: {error_msg}")
            self._show_error_message_on_main_thread("Error Inesperado", error_msg)

    def get_or_set_java_executable(self) -> str:
        if not self.java_executable or not os.path.isfile(self.java_executable):
            self.java_executable = self.get_java_executable_path()
        return self.java_executable

    def log_java_version(self) -> None:
        if not self.java_executable:
            self.log_message("Ruta del ejecutable de Java no definida.")
            return
        java_version_command = [self.java_executable, "-version"]
        try:
            java_version_output = subprocess.check_output(
                java_version_command, stderr=subprocess.STDOUT, text=True
            )
            self.log_message(f"Versión de Java: {java_version_output.splitlines()[0]}")
        except FileNotFoundError:
            self.log_message(f"Advertencia: No se pudo encontrar Java en '{self.java_executable}' para verificar la versión.")
        except (subprocess.CalledProcessError, OSError) as e:
            self.log_message(f"Error al verificar la versión de Java: {e}")

    def execute_minecraft_command(self, minecraft_command: list[str]) -> None:
        creationflags = subprocess.CREATE_NO_WINDOW
        self.process = subprocess.Popen(
            minecraft_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            cwd=self.minecraft_directory,
            creationflags=creationflags,
        )
        self.log_message(
            f"Comando de Minecraft ejecutado:: {' '.join(minecraft_command)}"
        )
        self.update_buttons_thread = threading.Thread(
            target=self._check_process, args=(self.process,), daemon=True
        )
        self.update_buttons_thread.start()

    def _check_process(self, process: subprocess.Popen[str]) -> None:
        process.wait()
        self.game_launched = False
        self.update_buttons_thread = None
        if self.root and not self.is_launcher_closed:
            self._run_on_main_thread(self._reset_ui_after_error)
        else:
            print("Launcher already closed or root is None, skipping UI update.")

    def _reset_ui_after_error(self) -> None:
        self.game_launched = False
        if self.button_launch:
            self.button_launch.config(state="normal")
        if self.button_close_game:
            self.button_close_game.config(state="disabled")

    def update_buttons_after_launch(self) -> None:
        if self.button_launch:
            self.button_launch.config(state="disabled")
        if self.button_close_game:
            self.button_close_game.config(state="normal")
        self.game_launched = True

    def on_user_selected(self, event: Optional[tk.Event] = None) -> None:
        selected_username = self.entry_username.get() if self.entry_username else ""
        if selected_username:
            self.load_user_data_from_directory()

    def generate_random_user_data(self) -> str:
        random_username = self.get_random_username()

        default_user_data: dict[str, Any] = {
            "username": random_username,
            "uuid": str(self.generate_uuid_for_username(random_username)),
            "selected_version": "",
            "type_version": "release",
            "advanced_options_directory": self.minecraft_directory,
            "advanced_options_close_launcher": False,
            "hide_log": False,
            "enable_uuid": False,
            "jvm_args": " ".join(self.default_jvm_args),
            "java_executable": "",
        }
        self._set_user_data(default_user_data)

        if self.entry_username:
            self.entry_username.set(random_username)

        self.update_uuid_entry()
        self.update_username_color(random_username)

        return random_username

    def initialize_user_data(self) -> None:
        self.advanced_options_directory_var.set(self.minecraft_directory)
        config_file_path = os.path.join(self.minecraft_directory, self.config_file)
        user_data_list: list[dict[str, Any]] = self._read_config_file(config_file_path)

        if user_data_list:
            self._process_user_data(user_data_list)
            last_user_data: dict[str, Any] = user_data_list[-1]
            self._set_user_data(last_user_data)
            if self.entry_username:
                self.entry_username.set(last_user_data.get("username", ""))
                self.update_username_color(last_user_data.get("username", ""))
                self.update_uuid_entry()
        else:
            random_username = self.get_random_username()
            default_user_data: dict[str, Any]
            default_user_data = {
                "username": random_username,
                "uuid": str(self.generate_uuid_for_username(random_username)),
                "selected_version": "",
                "type_version": "release",
                "advanced_options_directory": self.minecraft_directory,
                "advanced_options_close_launcher": False,
                "hide_log": False,
                "enable_uuid": False,
                "jvm_args": " ".join(self.default_jvm_args),
                "java_executable": "",
            }
            self._set_user_data(default_user_data)
            if self.entry_username:
                self.entry_username.set(random_username)
            self.update_uuid_entry()

        self._update_delete_user_checkbox_state(user_data_list)

    def _update_delete_user_checkbox_state(self, user_data_list: list[dict[str, Any]]) -> None:
        if self.delete_user_checkbox and self.delete_user_checkbox.winfo_exists():
            username = self.entry_username.get().strip() if self.entry_username else ""
            
            user_exists_in_config = any(user.get("username") == username for user in user_data_list)

            if not user_data_list or not user_exists_in_config:
                self.delete_user_checkbox.config(state=tk.DISABLED)
                self.delete_user_on_apply_var.set(False)
            else:
                self.delete_user_checkbox.config(state=tk.NORMAL)

    def update_uuid_entry(self) -> None:
        username = self.entry_username.get().strip() if self.entry_username else ""
        if self.is_empty_username(username):
            self.set_uuid_to_random()
        elif self.is_username_changed(username):
            self.update_uuid_based_on_username(username)
        self.update_previous_username(username)
        self.update_username_color(username)

    def is_empty_username(self, username: str) -> bool:
        return len(username) == 0

    def set_uuid_to_random(self) -> None:
        if self.entry_uuid:
            self.entry_uuid.delete(0, tk.END)
            self.entry_uuid.insert(0, "Random")

    def is_username_changed(self, username: str) -> bool:
        return username.lower() != "random" and username != self.previous_username

    def update_uuid_based_on_username(self, username: str) -> None:
        uuid_value = str(self.generate_uuid_for_username(username))
        if self.entry_uuid:
            self.entry_uuid.delete(0, tk.END)
            self.entry_uuid.insert(0, uuid_value)

    def update_previous_username(self, username: str) -> None:
        if username or username.lower() == "random":
            self.previous_username = username

    def on_change_random_user_data(self) -> None:
        full_username = self.entry_username.get().strip() if self.entry_username else ""
        self.update_username_color(full_username)
        self.update_uuid_entry()

    def update_username_color(self, full_username: str) -> None:
        color = self.determine_username_color(full_username)
        self.set_username_and_uuid_color(color)

    def determine_username_color(self, full_username: str) -> str:
        if self.is_username_too_short(full_username):
            return "red"
        if self.is_username_random_or_empty(full_username):
            return "gray"
        if self._is_randomly_generated(full_username):
            return "gray"
        if self.is_username_too_long(full_username):
            return "red"
        return "black"

    def is_username_too_short(self, full_username: str) -> bool:
        return len(full_username) <= 2

    def is_username_random_or_empty(self, full_username: str) -> bool:
        return len(full_username) == 0 or full_username.lower() == "random"

    def is_username_too_long(self, full_username: str) -> bool:
        return len(full_username) > 15

    def set_username_and_uuid_color(self, color: str) -> None:
        if self.entry_username:
            self.entry_username.config(foreground=color)
        if self.entry_uuid:
            self.entry_uuid.config(foreground=color)

    def get_random_username(self) -> str:
        random_number = random.randint(10, 99)
        adj = random.choice(_ADJECTIVES)
        noun = random.choice(_NOUNS)
        generated_name = f"{adj}as{noun}{random_number}"
        max_length = 16
        truncated_name = generated_name[:max_length]
        return truncated_name

    def _is_randomly_generated(self, username: str) -> bool:
        return username in _RANDOM_USERNAMES_SET

    def on_focus_in(self, event: tk.Event, default_text: str) -> None:
        widget = cast(ttk.Entry, event.widget)
        current_text = widget.get().lower()
        if current_text == default_text.lower():
            widget.delete(0, tk.END)
            widget.config(foreground="black")

    def on_focus_out(self, event: tk.Event, default_text: str) -> None:
        widget = cast(ttk.Entry, event.widget)
        current_text = widget.get().lower()
        if not current_text or current_text == default_text.lower():
            widget.delete(0, tk.END)
            widget.insert(0, default_text)
            widget.config(foreground="gray")

    def on_change(self, event: tk.Event, default_text: str) -> None:
        widget = cast(ttk.Entry, event.widget)
        current_text = widget.get().lower()
        if current_text != default_text.lower():
            widget.config(foreground="black")

    def copy_jar_for_modloader(self, selected_version: str) -> None:
        try:
            base_version = self.extract_base_version(selected_version)
            if not base_version:
                self._handle_missing_base_version(selected_version)
                return

            vanilla_jar_path = self._build_vanilla_jar_path(base_version)
            modloader_jar_path = self._build_modloader_jar_path(selected_version)

            if not self._validate_vanilla_jar(vanilla_jar_path):
                return

            self._prepare_modloader_directory(modloader_jar_path)
            self._perform_jar_copy(vanilla_jar_path, modloader_jar_path)
        except FileNotFoundError as e:
            error_msg = f"No se encontró un archivo o directorio necesario para la versión con mods: {e}"
            self.log_message(f"Error: {error_msg}")
            self._show_error_message_on_main_thread("Archivo no Encontrado", error_msg)
        except OSError as e:
            error_msg = f"Error del sistema al copiar archivos para la versión con mods: {e}"
            self.log_message(f"Error: {error_msg}")
            self._show_error_message_on_main_thread("Error de Archivo", error_msg)
        except Exception as e:
            error_msg = f"Error inesperado al preparar la versión con mods: {e}"
            self.log_message(f"Error: {error_msg}")
            self._show_error_message_on_main_thread("Error Inesperado", error_msg)

    def _handle_missing_base_version(self, selected_version: str) -> None:
        self.log_message(f"Versión base no encontrada para {selected_version}")

    def _build_vanilla_jar_path(self, base_version: str) -> str:
        return os.path.join(
            self.minecraft_directory, "versions", base_version, f"{base_version}.jar"
        )

    def _build_modloader_jar_path(self, selected_version: str) -> str:
        modloader_folder = os.path.join(
            self.minecraft_directory, "versions", selected_version
        )
        return os.path.join(modloader_folder, f"{selected_version}.jar")

    def _validate_vanilla_jar(self, vanilla_jar_path: str) -> bool:
        if not os.path.exists(vanilla_jar_path):
            self.log_message(f"Archivo base no encontrado: {vanilla_jar_path}")
            return False
        return True

    def _prepare_modloader_directory(self, modloader_jar_path: str) -> None:
        modloader_folder = os.path.dirname(modloader_jar_path)
        if not os.path.exists(modloader_folder):
            os.makedirs(modloader_folder)
            self.log_message(f"Carpeta creada: {modloader_folder}")

    def _perform_jar_copy(self, src: str, dst: str) -> None:
        if os.path.exists(dst):
            self.log_message(f"Archivo ya existe: {dst}")
        else:
            shutil.copy2(src, dst)
            self.log_message(f"Archivo copiado: {dst}")

    def extract_base_version(self, version_name: str) -> Optional[str]:
        parts = version_name.split("-")
        for part in reversed(parts):
            if part.count(".") == 2 and part.replace(".", "").isdigit():
                return part
        return None

    def _ensure_launcher_profiles_exists(self) -> None:
        profiles_path = os.path.join(self.minecraft_directory, "launcher_profiles.json")
        try:
            if not os.path.exists(profiles_path):
                self.log_message(f"No se encontró '{profiles_path}', creando uno nuevo.")
                default_profiles: dict[str, Any] = {
                    "profiles": {},
                    "clientToken": str(uuid.uuid4()),
                    "settings": {"crashAssistance": True, "enableAnalytics": False},
                    "launcherVersion": {"name": "Minecito-1.5", "format": 21},
                }
                os.makedirs(os.path.dirname(profiles_path), exist_ok=True)
                with open(profiles_path, "w", encoding="utf-8") as f:
                    json.dump(default_profiles, f, indent=4)
                self.log_message("launcher_profiles.json creado exitosamente.")
        except OSError as e:
            self.log_message(f"Error de sistema al crear launcher_profiles.json: {e}")
            self._show_error_message_on_main_thread("Error de Archivo", f"No se pudo crear el archivo de perfiles de Minecraft necesario en '{self.minecraft_directory}'. Verifica los permisos.")
            raise
        except Exception as e:
            self.log_message(f"Error inesperado creando launcher_profiles.json: {e}")
            self._show_error_message_on_main_thread("Error Inesperado", f"Ocurrió un error inesperado al configurar los archivos de perfil: {e}")
            raise

    def create_widgets(self) -> None:
        self.create_main_frame()
        self.create_username_widgets()
        self.create_version_widgets()
        self.create_uuid_widgets()
        self.create_buttons()
        self.create_log_frame()

    def create_main_frame(self) -> None:
        frame = ttk.Frame(self.root)
        frame.pack(expand=True, fill="both")
        self.frame = frame

    def create_username_widgets(self) -> None:
        entry_width = 20
        if self.frame:
            self.label_username = ttk.Label(self.frame, text="Nombre de Usuario:")
            self.entry_username = ttk.Combobox(self.frame, width=entry_width)
            self.entry_username.bind("<<ComboboxSelected>>", self.on_user_selected)
            self.label_username.place(x=5, y=5)
            self.entry_username.place(x=120, y=5)
            self.entry_username.bind("<FocusOut>", lambda event: self.update_uuid_entry())
            self.entry_username.bind("<KeyRelease>", lambda event: self.update_uuid_entry())
            self.button_generate_random_username = ttk.Button(
                self.frame, text="R", command=self.generate_random_user_data, width=3
            )
            self.button_generate_random_username.place(x=270, y=3)

    def create_version_widgets(self) -> None:
        if self.frame:
            self.label_version = ttk.Label(self.frame, text="Versión:")
            self.combobox_version = ttk.Combobox(self.frame, state="readonly", width=20)
            self.label_version.place(x=35, y=35)
            self.combobox_version.place(x=120, y=35)
        self.create_version_checkboxes()
        self.update_version_list()

    def create_version_checkboxes(self) -> None:
        if self.frame:
            checkbox_frame = ttk.Frame(self.frame)
            checkbox_frame.place(x=25, y=65)
            self.version_vars = {
                "snapshot": self.snapshot_var,
                "alpha": self.alpha_var,
                "beta": self.beta_var,
                "especial": self.especial_var,
            }

            def handle_checkbox_change(selected_var: tk.BooleanVar) -> None:
                if selected_var.get():
                    for _, var in self.version_vars.items():
                        if var != selected_var:
                            var.set(False)
                if not any(var.get() for var in self.version_vars.values()):
                    self.update_version_list()
                    return
                self.update_version_list()

            checkboxes = [
                ("Snapshot", self.snapshot_var, "snapshot"),
                ("Beta", self.beta_var, "beta"),
                ("Alpha", self.alpha_var, "alpha"),
                ("Especial", self.especial_var, "especial"),
            ]
            for idx, (text, var, _) in enumerate(checkboxes):
                ttk.Checkbutton(
                    checkbox_frame,
                    text=text,
                    variable=var,
                    command=lambda v=var: handle_checkbox_change(v),
                ).grid(row=0, column=idx, padx=2)
            self.snapshot_var.set(False)
            self.alpha_var.set(False)
            self.beta_var.set(False)
            self.especial_var.set(False)
            self.update_version_list()

    def create_uuid_widgets(self) -> None:
        if self.frame:
            uuid_entry_width = 23
            self.label_uuid = ttk.Label(self.frame, text="UUID:")
            self.entry_uuid = ttk.Entry(self.frame, width=uuid_entry_width, state=tk.NORMAL)
            self.label_uuid.place(x=40, y=95)
            self.entry_uuid.place(x=120, y=95)
            self.label_uuid.place_forget()
            self.entry_uuid.place_forget()

    def create_buttons(self) -> None:
        if self.frame:
            self.button_launch = ttk.Button(
                self.frame, text="¡Iniciar Minecraft!", command=self.launch_minecraft
            )
            self.button_launch.place(x=45, y=96)
            self.button_close_game = ttk.Button(
                self.frame,
                text="¡Cerrar Minecraft!",
                state="disabled",
                command=self.close_game,
            )
            self.button_close_game.place(x=155, y=96)
            self.button_advanced_options = ttk.Button(
                self.frame,
                text="Opciones Avanzadas",
                command=self.create_advanced_options_window,
            )
            self.button_advanced_options.place(x=90, y=130)

    def create_log_frame(self) -> None:
        if self.frame:
            log_frame = ttk.Frame(self.frame)
            log_frame.place(x=305, y=5, width=520, height=self._get_log_frame_height())
            self.log_frame = log_frame
            self.log_text = tk.Text(
                log_frame, height=9, width=63, state=tk.DISABLED, wrap="none"
            )
            scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)  # type: ignore
            self.log_text.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def create_advanced_options_window(self) -> None:
        if self.advanced_options_window and self.advanced_options_window.winfo_exists():
            self.advanced_options_window.destroy()

        window_width = 340
        window_height = 243
        screen_width = self.root.winfo_screenwidth()  # type: ignore
        screen_height = self.root.winfo_screenheight()  # type: ignore
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)

        self.advanced_options_window = tk.Toplevel(self.root)
        self.advanced_options_window.withdraw()
        self.advanced_options_window.title("Opciones Avanzadas")
        self.advanced_options_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.advanced_options_window.resizable(False, False)
        self.advanced_options_window.iconbitmap(self.resource_path("icons/crafting_table.ico"))  # type: ignore
        self.advanced_options_window.transient(self.root)
        self.advanced_options_window.grab_set()
        self._original_close_launcher_var_value = self.advanced_options_close_launcher_var.get()
        self._original_memory_var_value = self.advanced_options_memory_var.get()
        self._original_directory_var_value = self.advanced_options_directory_var.get()
        self._original_java_executable_var_value = self.java_executable_var.get()
        self._original_hide_log_var_value = self.hide_log_var.get()
        self._original_delete_user_on_apply_var_value = self.delete_user_on_apply_var.get()

        self.create_advanced_options_widgets()
        config_file_path = os.path.join(self.minecraft_directory, self.config_file)
        user_data_list = self._read_config_file(config_file_path)
        self._update_delete_user_checkbox_state(user_data_list)
        self.advanced_options_window.deiconify()

    def create_advanced_options_widgets(self) -> None:
        if self.advanced_options_window:
            main_frame = ttk.Frame(self.advanced_options_window)
            main_frame.place(x=5, y=2, width=330, height=246)
            self.create_jvm_args_widget(main_frame)
            self.create_java_executable_widget(main_frame)
            self.create_minecraft_directory_widget(main_frame)
            self.create_close_launcher_widget(main_frame)
            self.create_hide_log_widget(main_frame)
            self.create_enable_uuid_widget(main_frame)
            self.create_delete_user_widget(main_frame)
            self.create_buttons_frame(main_frame)

    def create_jvm_args_widget(self, main_frame: ttk.Frame) -> None:
        ttk.Label(main_frame, text="Argumentos JVM:", foreground="dark red").place(
            x=0, y=0
        )
        memory_entry = ttk.Entry(
            main_frame, textvariable=self.advanced_options_memory_var, width=54
        )
        memory_entry.place(x=0, y=20)
        if self.advanced_options_memory_var and not self.advanced_options_memory_var.get():
            self.advanced_options_memory_var.set(" ".join(self.default_jvm_args))

    def create_java_executable_widget(self, main_frame: ttk.Frame) -> None:
        self.java_executable_var = tk.StringVar()
        java_executable_path = self.get_java_executable_path()
        self.java_executable_var.set(java_executable_path)
        self.java_executable_entry = ttk.Entry(
            main_frame, textvariable=self.java_executable_var, width=41
        )
        ttk.Label(main_frame, text="Ejecutable de Java:", foreground="dark red").place(
            x=0, y=42
        )
        if self.java_executable_entry:
            self.java_executable_entry.place(x=0, y=62)
            self.java_executable_entry.configure(state="readonly")
        button_frame_select_java = ttk.Frame(main_frame)
        button_frame_select_java.place(x=255, y=60)
        ttk.Button(
            button_frame_select_java,
            text="Seleccionar",
            command=self.select_java_executable,
        ).grid(row=0, column=0)

    def create_minecraft_directory_widget(self, main_frame: ttk.Frame) -> None:
        ttk.Label(
            main_frame, text="Directorio de Minecraft:", foreground="dark red"
        ).place(x=0, y=84)
        directory_entry = ttk.Entry(
            main_frame,
            textvariable=self.advanced_options_directory_var,
            state="readonly",
            width=41,
        )
        directory_entry.place(x=0, y=104)
        button_frame_select = ttk.Frame(main_frame)
        button_frame_select.place(x=255, y=102)
        ttk.Button(
            button_frame_select,
            text="Seleccionar",
            command=self.select_minecraft_directory,
        ).grid(row=0, column=0)

    def create_close_launcher_widget(self, main_frame: ttk.Frame) -> None:
        close_launcher_frame = ttk.Frame(main_frame)
        close_launcher_frame.place(x=0, y=128)
        close_launcher_checkbox = ttk.Checkbutton(
            close_launcher_frame, 
            text="Cerrar Minecito cuando inicie Minecraft.", 
            variable=self.advanced_options_close_launcher_var,
        )
        close_launcher_checkbox.grid(row=0, column=0)

    def create_hide_log_widget(self, main_frame: ttk.Frame) -> None:
        self.hide_log_checkbox = ttk.Checkbutton(
            main_frame, text="Habilitar el registro.", variable=self.hide_log_var
        )
        self.hide_log_checkbox.place(x=0, y=148)

    def create_enable_uuid_widget(self, main_frame: ttk.Frame) -> None:
        if self.label_uuid and self.label_uuid.winfo_ismapped():
            self.enable_uuid_var.set(True)
        else:
            self.enable_uuid_var.set(False)
        self.enable_uuid_checkbox = ttk.Checkbutton(
            main_frame, text="Habilitar UUID.", variable=self.enable_uuid_var
        )
        self.enable_uuid_checkbox.place(x=0, y=168)

    def create_delete_user_widget(self, main_frame: ttk.Frame) -> None:
        self.delete_user_checkbox = ttk.Checkbutton(
            main_frame,
            text="Eliminar usuario actual.",
            variable=self.delete_user_on_apply_var,
            command=self.on_delete_user_checkbox_toggle
        )
        self.delete_user_checkbox.place(x=0, y=188)

    def on_delete_user_checkbox_toggle(self) -> None:
        pass

    def create_buttons_frame(self, main_frame: ttk.Frame) -> None:
        apply_button = ttk.Button(
            main_frame, text="Aplicar", command=self.apply_advanced_options
        )
        apply_button.place(x=85, y=210)
        cancel_button = ttk.Button(
            main_frame, text="Cancelar", command=self.cancel_advanced_options
        )
        cancel_button.place(x=185, y=210)

    def center_advanced_options_window(self) -> None:
        if self.advanced_options_window:
            self.advanced_options_window.update_idletasks()
            window_width = self.advanced_options_window.winfo_width()
            window_height = self.advanced_options_window.winfo_height()
            screen_width = 0
            screen_height = 0
            if self.root and self.root.winfo_exists():
                root_window: tk.Tk = self.root
                screen_width = root_window.winfo_screenwidth()
                screen_height = root_window.winfo_screenheight()
            x = (screen_width // 2) - (window_width // 2)
            y = (screen_height // 2) - (window_height // 2)
            self.advanced_options_window.geometry(f"+{x}+{y}")
            self.advanced_options_window.protocol(
                "WM_DELETE_WINDOW", self.cancel_advanced_options
            )

    def move_buttons_for_uuid_visible(self) -> None:
        if self.button_launch:
            self.button_launch.place(x=45, y=127)
        if self.button_close_game:
            self.button_close_game.place(x=155, y=127)
        if self.button_advanced_options:
            self.button_advanced_options.place(x=90, y=161)

    def restore_buttons_original_position(self) -> None:
        if self.button_launch:
            self.button_launch.place(x=45, y=96)
        if self.button_close_game:
            self.button_close_game.place(x=155, y=96)
        if self.button_advanced_options:
            self.button_advanced_options.place(x=90, y=130)

    def get_java_executable_path(self) -> str:
        if self.java_executable and os.path.isfile(self.java_executable):
            return self.java_executable
        selected_version = self.combobox_version.get() if self.combobox_version else ""
        if not selected_version:
            return "javaw"
        if self._is_alpha_or_beta(selected_version):
            return self._get_minecraft_jre_path("jre-legacy")
        return self._get_minecraft_jre_path("java-runtime-gamma")

    def _is_alpha_or_beta(self, version_id: str) -> bool:
        return (
            version_id.startswith(("a1.", "b1.", "infdev"))
            or self.alpha_var.get()
            or self.beta_var.get()
        )

    def _get_minecraft_jre_path(self, runtime_name: str) -> str:
        runtime_path = os.path.join(
            self.minecraft_directory,
            "runtime",
            runtime_name,
            "windows-x64",
            runtime_name,
            "bin",
            "javaw.exe",
        )
        if os.path.isfile(runtime_path):
            return runtime_path
        return runtime_path

    def select_java_executable(self) -> None:
        selected_file = filedialog.askopenfilename(
            filetypes=[("Ejecutables Java", "java.exe javaw.exe")],
            title="Seleccionar ejecutable de Java",
        )
        if selected_file:
            valid_file = os.path.basename(selected_file).lower() in (
                "java.exe",
                "javaw.exe",
            )
            if valid_file:
                self.java_executable_var.set(selected_file)
                self.java_executable = selected_file
            else:
                self._show_error_message_on_main_thread("Error", "Debe seleccionar java.exe o javaw.exe")
        if self.advanced_options_window and self.advanced_options_window.winfo_exists():
            self.advanced_options_window.lift()  # type: ignore

    def apply_advanced_options(self) -> None:
        custom_directory = self.advanced_options_directory_var.get().strip()
        if not os.path.isdir(custom_directory):
            self._show_error_message_on_main_thread("Error", "El directorio personalizado no es válido.")
            return
        
        if self.delete_user_on_apply_var.get():
            selected_username = self.entry_username.get().strip() if self.entry_username else ""
            
            if not selected_username:
                
                messagebox.showwarning("Eliminar Usuario", "Por favor, selecciona un usuario para eliminar.")
                self.delete_user_on_apply_var.set(False)
                return

            if messagebox.askyesno(
                "Confirmar Eliminación",
                f"¿Estás seguro de que quieres eliminar el usuario '{selected_username}'?",
                detail="Al eliminar este usuario, se borrarán todas sus configuraciones guardadas, incluyendo:\n\n" \
                       "• Argumentos JVM personalizados\n" \
                       "• Directorio de Minecraft\n" \
                       "• Versión de Minecraft seleccionada\n" \
                       "• Configuración de cierre del lanzador\n" \
                       "• Configuración de UUID\n\n" \
                       "Todas estas configuraciones se restablecerán a sus valores predeterminados. ¿Deseas continuar?",
                icon="warning"
            ):
                try:
                    config_file_path = os.path.join(self.minecraft_directory, self.config_file)
                    user_data_list = self._read_config_file(config_file_path)
                    updated_user_data_list = [
                        user for user in user_data_list if str(user.get("username", "")) != selected_username
                    ]
                    self._write_config_file(config_file_path, updated_user_data_list)
                    if updated_user_data_list:
                        last_user_data = updated_user_data_list[-1]
                        self._set_user_data(last_user_data)
                        if self.entry_username:
                            self.entry_username.set(last_user_data.get("username", ""))
                    else:
                        generated_username = self.generate_random_user_data()
                        updated_user_data_list: list[dict[str, Any]] = [{
                            "username": generated_username,
                            "uuid": str(self.generate_uuid_for_username(generated_username)),
                            "selected_version": "",
                            "type_version": "release",
                            "advanced_options_directory": self.minecraft_directory,
                            "advanced_options_close_launcher": False,
                            "hide_log": False,
                            "enable_uuid": False,
                            "jvm_args": "",
                            "java_executable": ""
                        }]
                    self._process_user_data(updated_user_data_list)
                    self._update_delete_user_checkbox_state(updated_user_data_list)
                    if updated_user_data_list:
                        if self.entry_username:
                            self.entry_username.set(updated_user_data_list[0].get("username", ""))
                    else:
                        if self.entry_username:
                            self.entry_username.set("")
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo eliminar el usuario: {e}")
            self.delete_user_on_apply_var.set(False)


        if self.enable_uuid_var.get():
            if self.label_uuid:
                self.label_uuid.place(x=40, y=95)
            if self.entry_uuid:
                self.entry_uuid.place(x=120, y=95)
            self.move_buttons_for_uuid_visible()
            if self.root:
                self.root.geometry("305x192")
            if self.log_text:
                self.log_text.config(height=11, width=63)
        else:
            if self.label_uuid:
                self.label_uuid.place_forget()
            if self.entry_uuid:
                self.entry_uuid.place_forget()
            self.restore_buttons_original_position()
            if self.root:
                self.root.geometry("305x160")
            if self.log_text:
                self.log_text.config(height=9, width=63)
        self.hide_show_log()
        self.adjust_window_size()
        self.hide_log_var_original = self.hide_log_var.get()
        if self.java_executable_var:
            self.java_executable = self.java_executable_var.get()
        self.update_java_executable_path()
        if self.advanced_options_window and self.advanced_options_window.winfo_exists():
            self.advanced_options_window.destroy()

    def cancel_advanced_options(self) -> None:
        self.advanced_options_close_launcher_var.set(self._original_close_launcher_var_value)
        self.advanced_options_memory_var.set(self._original_memory_var_value)
        self.advanced_options_directory_var.set(self._original_directory_var_value)
        self.java_executable_var.set(self._original_java_executable_var_value)
        self.hide_log_var.set(self._original_hide_log_var_value)
        self.delete_user_on_apply_var.set(self._original_delete_user_on_apply_var_value)

        if self.advanced_options_window and self.advanced_options_window.winfo_exists():
            self.advanced_options_window.destroy()

    def update_version_list(self) -> None:
        if self.root and self.root.winfo_exists():
            self.root.after(0, self._update_version_list_internal)

    def _update_version_list_internal(self) -> None:
        try:
            
            assert self.minecraft_directory is not None, "Minecraft directory should be initialized"
            all_versions: list[MinecraftVersionInfo] = minecraft_launcher_lib.utils.get_available_versions(  # type: ignore
                self.minecraft_directory
            )
            selected_types = self._get_selected_version_types()
            available_versions = self._filter_versions(all_versions, selected_types)
            version_names = [version["id"] for version in available_versions]
            if self.combobox_version:
                self.combobox_version["values"] = version_names
                current_selection = self.combobox_version.get()
                if current_selection not in version_names:
                    self.combobox_version.set("")
                    if version_names:
                        self.combobox_version.set(version_names[0])
                
        except Exception as e:
            self.log_message(f"Error actualizando versiones: {str(e)}")

    def _get_selected_version_types(self) -> list[str]:
        selected_types: list[str] = []
        if self.snapshot_var.get():
            selected_types.append("snapshot")
        if self.alpha_var.get():
            selected_types.append("old_alpha")
        if self.beta_var.get():
            selected_types.append("old_beta")
        if self.especial_var.get():
            selected_types.append("especial")
        return selected_types

    def _filter_versions(self, all_versions: list[MinecraftVersionInfo], selected_types_list: list[str]) -> list[MinecraftVersionInfo]:
        modloaders = ["forge", "fabric", "quilt"]

        if "especial" in selected_types_list:
            return self._filter_special_versions(all_versions, modloaders)

        if selected_types_list:
            return self._filter_by_selected_types(
                all_versions, selected_types_list, modloaders
            )

        return self._filter_release_versions(all_versions, modloaders)

    def _get_selected_types(self, type_mapping: dict[str, str]) -> list[str]:
        return [
            type_mapping[name] for name, var in self.version_vars.items() if var.get()
        ]

    def _filter_special_versions(self, all_versions: list[MinecraftVersionInfo], modloaders: list[str]) -> list[MinecraftVersionInfo]:
        return [v for v in all_versions if any(ml in v["id"] for ml in modloaders)]

    def _filter_by_selected_types(
        self, all_versions: list[MinecraftVersionInfo], actual_selected_types: list[str], modloaders: list[str]
    ) -> list[MinecraftVersionInfo]:
        return [
            v
            for v in all_versions
            if v["type"] in actual_selected_types
            and not any(ml in v["id"] for ml in modloaders)
        ]

    def _filter_release_versions(self, all_versions: list[MinecraftVersionInfo], modloaders: list[str]) -> list[MinecraftVersionInfo]:
        return [
            v
            for v in all_versions
            if v["type"] == "release" and not any(ml in v["id"] for ml in modloaders)
        ]

    def _update_button_states(self) -> None:
        if self.game_launched:
            if self.button_launch:
                self.button_launch["state"] = "disabled"
            if self.button_close_game:
                self.button_close_game["state"] = "normal"
        else:
            if self.button_launch:
                self.button_launch["state"] = "normal"
            if self.button_close_game:
                self.button_close_game["state"] = "disabled"

    def install_version(self, selected_version: str) -> None:

        def set_status(status: str) -> None:
            self.log_message(f"Estado: {status}")

        def set_progress(progress: int) -> None:
            if self.current_max != 0:
                self.log_message(f"Progreso: {progress}/{self.current_max}")

        def set_max(new_max: int) -> None:
            self.current_max = new_max

        if self.button_close_game:
            self.button_close_game["state"] = "disabled"
        self.current_max = 0
        callback: CallbackDict = {
            "setStatus": set_status,
            "setProgress": set_progress,
            "setMax": set_max,
        }
        try:
            self.log_message(f"Iniciando la instalación de '{selected_version}'...")
            minecraft_launcher_lib.install.install_minecraft_version(  # type: ignore
                selected_version, self.minecraft_directory, callback=callback
            )
            self.log_message(
                f"La versión '{selected_version}' se instaló correctamente."
            )
            username_for_launch: str = ""
            if self.entry_username:
                username_for_launch = self.entry_username.get().strip()
            self.run_minecraft(selected_version, self.get_launch_options(username_for_launch))
        except minecraft_launcher_lib.exceptions.VersionNotFound:
            error_msg = f"La versión '{selected_version}' no fue encontrada o no es válida."
            self.log_message(f"Error: {error_msg}")
            self._show_error_message_on_main_thread("Versión no encontrada", error_msg)
        except minecraft_launcher_lib.exceptions.FileOutsideMinecraftDirectory:
            error_msg = "Error Crítico de Seguridad: Se intentó escribir un archivo fuera del directorio de Minecraft. Instalación abortada."
            self.log_message(error_msg)
            self._show_error_message_on_main_thread("Error de Seguridad", error_msg)
        except minecraft_launcher_lib.exceptions.InvalidChecksum:
            error_msg = "Un archivo descargado está corrupto. Por favor, inténtalo de nuevo."
            self.log_message(f"Error de Descarga: {error_msg}")
            self._show_error_message_on_main_thread("Error de Descarga", error_msg)
        except (subprocess.SubprocessError, OSError) as e:
            error_msg = f"Error de sistema durante la instalación: {e}"
            self.log_message(error_msg)
            self._show_error_message_on_main_thread("Error del Sistema", error_msg)
        except Exception as e:
            error_msg = f"Ocurrió un error inesperado durante la instalación: {e}"
            self.log_message(error_msg)
            self._show_error_message_on_main_thread("Error Inesperado", error_msg)
        finally:
            if not self.game_launched:
                if self.button_launch:
                    self.button_launch["state"] = "normal"
                if self.button_close_game:
                    self.button_close_game["state"] = "disabled"

    def update_java_executable_path(self) -> None:
        selected_version = self.combobox_version.get() if self.combobox_version else ""
        if not selected_version:
            return
        java_path = self.get_java_executable_path()
        self.java_executable = java_path

def _create_random_usernames_set() -> set[str]:
    max_length = 16
    return {
        f"{adjective}as{noun}{i:02d}"[:max_length]
        for adjective in _ADJECTIVES
        for noun in _NOUNS
        for i in range(100)
    }

_RANDOM_USERNAMES_SET = _create_random_usernames_set()

if __name__ == "__main__":
    root = tk.Tk()
    launcher = Launchercito(root)
    root.mainloop()