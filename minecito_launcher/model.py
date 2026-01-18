import os
import subprocess
import threading
import uuid
import shutil
import random
import logging
from typing import Optional, List, Dict, Any, Callable
import minecraft_launcher_lib
from .config_manager import ConfigManager, UserData
logger = logging.getLogger(__name__)
class LauncherModel:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.minecraft_directory = self._determine_minecraft_directory()
        self.process: Optional[subprocess.Popen] = None
        self.game_running = False
        if not os.path.exists(self.minecraft_directory):
            try:
                os.makedirs(self.minecraft_directory)
            except OSError as e:
                logger.error(f"Failed to create minecraft directory: {e}")
    def _determine_minecraft_directory(self) -> str:
        if self.config_manager.current_user and self.config_manager.current_user.advanced_options_directory:
             dir_path = self.config_manager.current_user.advanced_options_directory
             if os.path.exists(dir_path):
                 return dir_path
        default_dir = minecraft_launcher_lib.utils.get_minecraft_directory()
        if not os.access(os.path.dirname(default_dir), os.W_OK):
             local_appdata = os.path.join(os.environ.get("LOCALAPPDATA", ""), ".minecito")
             if not os.path.exists(local_appdata):
                 os.makedirs(local_appdata)
             return local_appdata
        return default_dir
    def get_available_versions(self) -> List[Dict[str, Any]]:
        try:
            return minecraft_launcher_lib.utils.get_available_versions(self.minecraft_directory)
        except Exception as e:
            logger.error(f"Error fetching versions: {e}")
            return []
    def install_version(self, version_id: str, callback: Dict[str, Callable]) -> None:
        try:
            minecraft_launcher_lib.install.install_minecraft_version(
                version_id, self.minecraft_directory, callback=callback
            )
            callback.get("setStatus", lambda s: None)("Verificando Runtime de Java...")
            minecraft_launcher_lib.install.install_jvm_runtime(
                 version_id, self.minecraft_directory, callback=callback
            )
        except Exception as e:
            logger.error(f"Installation failed: {e}")
            raise
    def launch_minecraft(self, version_id: str, callback_log: Callable[[str], None]) -> None:
        if not self.config_manager.current_user:
            raise ValueError("No user selected")
        user = self.config_manager.current_user
        jvm_args_list = user.jvm_args.split() if user.jvm_args else []
        jvm_args_list.append("-Djava.util.logging.SimpleFormatter.format=[%1$tT] [%4$-7s] %5$s")
        options = {
            "username": user.username,
            "uuid": user.uuid if user.uuid else str(uuid.uuid5(uuid.NAMESPACE_DNS, user.username)),
            "token": "0",
            "jvmArguments": jvm_args_list
        }
        custom_java = user.java_executable
        is_bad_system_java = False
        if custom_java:
             lower_java = custom_java.lower()
             if "oracle" in lower_java and "javapath" in lower_java:
                 is_bad_system_java = True
             elif lower_java == "javaw" or lower_java == "javaw.exe":
                 is_bad_system_java = True
        runtime_name = self._get_runtime_name_for_version(version_id)
        java_path = self._get_minecraft_jre_path(runtime_name)
        use_custom = False
        if custom_java and os.path.isfile(custom_java):
            if runtime_name == "jre-legacy" and is_bad_system_java:
                callback_log(f"Ignorando Java personalizado incompatible detectado (System Default): {custom_java}")
                use_custom = False
            else:
                use_custom = True
        if use_custom:
            callback_log(f"Usando Java personalizado (Configuración de Usuario): {custom_java}")
            options["executablePath"] = custom_java
        else:
            callback_log(f"Buscando Runtime predeterminado '{runtime_name}' en: {java_path}")
            if os.path.isfile(java_path):
                callback_log(f"Runtime interno encontrado. Usando: {java_path}")
                options["executablePath"] = java_path
            else:
                 callback_log("Runtime interno NO encontrado. Se intentará usar el defecto de la librería.")
        if any(ml in version_id.lower() for ml in ["fabric", "quilt", "forge"]):
            self._handle_modloader_jar(version_id)
        command = minecraft_launcher_lib.command.get_minecraft_command(
            version_id, self.minecraft_directory, options
        )
        callback_log(f"Executing command: {' '.join(command)}")
        creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        try:
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.minecraft_directory,
                creationflags=creationflags
            )
            self.game_running = True
            import locale
            sys_encoding = locale.getpreferredencoding()
            def read_stream(stream, is_stderr=False):
                try:
                    for line in iter(stream.readline, b''):
                         try:
                             decoded = line.decode(sys_encoding, errors='replace').strip()
                         except:
                             decoded = str(line)
                         if decoded:
                             prefix = ""
                             lower_line = decoded.lower()
                             has_level = any(tag in lower_line for tag in ["info:", "warn:", "error:", "información:", "advertencia:", "excepción:"])
                             is_formatted = decoded.startswith("[") and "]" in decoded
                             if not has_level and not is_formatted:
                                 if is_stderr:
                                     if "error" in lower_line or "exception" in lower_line:
                                         prefix = "ERROR: "
                                     elif "warn" in lower_line or "advertencia" in lower_line:
                                         prefix = "WARN: "
                                     elif "info" in lower_line or "información" in lower_line:
                                         prefix = "INFO: "
                                     else:
                                         prefix = "> "
                             callback_log(f"{prefix}{decoded}")
                except Exception as e:
                     callback_log(f"Log Error: {e}")
                finally:
                     stream.close()
            if self.process.stdout:
                threading.Thread(target=read_stream, args=(self.process.stdout, False), daemon=True).start()
            if self.process.stderr:
                threading.Thread(target=read_stream, args=(self.process.stderr, True), daemon=True).start()
        except Exception as e:
            self.game_running = False
            raise e
    def _get_runtime_name_for_version(self, version_id: str) -> str:
        if any(x in version_id for x in ["a1.", "b1.", "infdev", "c0."]):
             return "jre-legacy"
        try:
            parts = [int(p) for p in version_id.split('.') if p.isdigit()]
            if "w" in version_id and len(parts) < 2:
                if int(version_id.split('w')[0]) >= 21:
                    return "java-runtime-alpha"
                else:
                    return "jre-legacy"
            if not parts:
                return "java-runtime-delta"
            major = parts[0]
            minor = parts[1] if len(parts) > 1 else 0
            if major == 1:
                if minor <= 16:
                    return "jre-legacy"
                elif minor == 17:
                    return "java-runtime-alpha"
                elif minor >= 18 and minor <= 20:
                     if minor == 20 and len(parts) > 2 and parts[2] >= 5:
                         return "java-runtime-delta"
                     return "java-runtime-beta"
                elif minor >= 21:
                    return "java-runtime-delta"
            return "java-runtime-delta"
        except Exception:
            return "java-runtime-delta"
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
        return runtime_path
    def close_minecraft(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.game_running = False
    def _handle_modloader_jar(self, version_id: str):
        try:
            pass
        except Exception as e:
            logger.warning(f"Modloader jar handling warning: {e}")
    _ADJECTIVES = sorted([
        "Bill", "Cal", "Dar", "Fun", "Gen", "Gol", "Happy", "Hol", "Krit",
        "Mig", "Nus", "Sad", "Ser", "Shy", "Sil", "Smad", "Swy", "Thom",
    ])
    _NOUNS = sorted([
        "Bird", "Blast", "Cat", "Dog", "Dolly", "Don", "Elephy", "Fish",
        "Gra", "Lio", "Moo", "Nick", "Nill", "Phel", "Star", "Story",
        "Turly", "Vey", "White", "Win", "Znack",
    ])
    def _generate_random_usernames_set(self) -> set:
        max_length = 16
        return {
            f"{adj}as{noun}{i:02d}"[:max_length]
            for adj in self._ADJECTIVES
            for noun in self._NOUNS
            for i in range(100)
        }
    def generate_random_username(self) -> str:
        while True:
             adj = random.choice(self._ADJECTIVES)
             noun = random.choice(self._NOUNS)
             number = random.randint(10, 99)
             name = f"{adj}as{noun}{number}"[:16]
             return name
    def is_random_username(self, username: str) -> bool:
        import re
        pattern = r"(?i)^[a-z]+as[a-z]+\d{2}$"
        return bool(re.match(pattern, username))
    def is_version_installed(self, version_id: str) -> bool:
         return os.path.exists(os.path.join(self.minecraft_directory, "versions", version_id, f"{version_id}.json"))
