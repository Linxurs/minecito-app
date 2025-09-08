"""
Lanzador de Minecraft
"""
import os
import signal
import subprocess
import threading
import uuid
from typing import Any, Dict, List, Optional
import minecraft_launcher_lib
from minecraft_launcher_lib.types import CallbackDict, MinecraftOptions


class MinecraftLauncher:
    """Lanzador de Minecraft"""
    
    def __init__(self, minecraft_directory: str):
        self.minecraft_directory = minecraft_directory
        self.process: Optional[subprocess.Popen[str]] = None
        self.game_launched = False
        self.current_max = 0
        self.update_buttons_thread: Optional[threading.Thread] = None
        self.is_launcher_closed = False
    
    def generate_uuid_for_username(self, username: str) -> uuid.UUID:
        """Genera un UUID para el nombre de usuario"""
        return uuid.uuid5(uuid.NAMESPACE_DNS, username)
    
    def get_launch_options(self, username: str, jvm_args: List[str]) -> Dict[str, Any]:
        """Obtiene las opciones de lanzamiento"""
        return {
            "username": username,
            "uuid": str(self.generate_uuid_for_username(username)),
            "token": "0",
            "jvmArguments": jvm_args,
        }
    
    def install_version(self, selected_version: str, callback_functions: Dict[str, Any]) -> bool:
        """Instala una versión de Minecraft"""
        try:
            callback: CallbackDict = {
                "setStatus": callback_functions.get("set_status", lambda x: None),
                "setProgress": callback_functions.get("set_progress", lambda x: None),
                "setMax": callback_functions.get("set_max", lambda x: None),
            }
            
            minecraft_launcher_lib.install.install_minecraft_version(
                selected_version, self.minecraft_directory, callback=callback
            )
            return True
            
        except minecraft_launcher_lib.exceptions.VersionNotFound:
            raise Exception(f"La versión '{selected_version}' no fue encontrada o no es válida.")
        except minecraft_launcher_lib.exceptions.FileOutsideMinecraftDirectory:
            raise Exception("Error Crítico de Seguridad: Se intentó escribir un archivo fuera del directorio de Minecraft.")
        except minecraft_launcher_lib.exceptions.InvalidChecksum:
            raise Exception("Un archivo descargado está corrupto. Por favor, inténtalo de nuevo.")
        except (subprocess.SubprocessError, OSError) as e:
            raise Exception(f"Error de sistema durante la instalación: {e}")
        except Exception as e:
            raise Exception(f"Error inesperado durante la instalación: {e}")
    
    def run_minecraft(self, selected_version: str, options: Dict[str, Any], java_executable: str) -> subprocess.Popen[str]:
        """Ejecuta Minecraft"""
        minecraft_command = minecraft_launcher_lib.command.get_minecraft_command(
            selected_version, self.minecraft_directory, options
        )
        
        minecraft_command[0] = java_executable
        
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
        
        self.game_launched = True
        
        # Iniciar hilo para monitorear el proceso
        self.update_buttons_thread = threading.Thread(
            target=self._check_process, args=(self.process,), daemon=True
        )
        self.update_buttons_thread.start()
        
        return self.process
    
    def _check_process(self, process: subprocess.Popen[str]) -> None:
        """Monitorea el proceso de Minecraft"""
        process.wait()
        self.game_launched = False
        self.update_buttons_thread = None
    
    def close_game(self) -> bool:
        """Cierra el juego"""
        try:
            if self.process and self.process.poll() is None:
                os.kill(self.process.pid, signal.SIGTERM)
                self.game_launched = False
                return True
            return False
        except (ProcessLookupError, PermissionError, Exception):
            self.game_launched = False
            return False
    
    def get_minecraft_command_string(self, command: List[str]) -> str:
        """Formatea el comando de Minecraft para logging"""
        return " ".join(command)
    
    def format_command_message(self, message: str) -> str:
        """Formatea el mensaje del comando para el log"""
        cmd: str = message.split(": ", 1)[1]
        parts: List[str] = cmd.split()
        formatted: List[str] = ["INFORMACIÓN DE LA SESIÓN:"]

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

        formatted.extend(self._format_java_section(parts, java_index))
        formatted.extend(self._format_cp_section(parts, cp_index))
        formatted.extend(self._format_user_section(parts, user_index))
        formatted.extend(self._format_options_section(parts, options_start))

        return "".join(formatted)
    
    def _format_java_section(self, parts: List[str], java_index: int) -> List[str]:
        """Formatea la sección de Java"""
        return ["\n\n=== Java ===", f"\n{parts[java_index].replace('/', '\\')}"]
    
    def _format_cp_section(self, parts: List[str], cp_index: int) -> List[str]:
        """Formatea la sección de classpath"""
        if cp_index == -1:
            return []

        formatted: List[str] = [
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
    
    def _format_user_section(self, parts: List[str], user_index: int) -> List[str]:
        """Formatea la sección de usuario"""
        if user_index == -1:
            return []

        return [
            "\n\n=== Usuario ===",
            f"\n  {parts[user_index]}",
            f"\n  {parts[user_index + 1]}",
        ]
    
    def _format_options_section(self, parts: List[str], options_start: int) -> List[str]:
        """Formatea la sección de opciones"""
        if options_start == -1:
            return []

        formatted = ["\n\n=== Opciones ==="]
        for i in range(options_start, len(parts), 2):
            if i + 1 < len(parts):
                formatted.append(f"\n  {parts[i]} {parts[i + 1].replace('/', '\\')}")

        return formatted